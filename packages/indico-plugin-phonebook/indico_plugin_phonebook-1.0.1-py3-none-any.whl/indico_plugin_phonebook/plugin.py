# -*- coding: utf-8 -*-
"""
Indico Phonebook Plugin

Synchronizes Indico categories and user access with groups defined in
an external Phonebook GraphQL API (e.g., ePIC, STAR, sPHENIX).

Features:
- Health check endpoint
- Manual sync per experiment
- JSON-configurable endpoints
- User and category membership synchronization
"""

import json
import logging
import time

import requests
from flask import jsonify
from sqlalchemy.exc import IntegrityError

from indico.core.db import db
from indico.core.plugins import IndicoPlugin, plugin_engine
from indico.modules.categories import Category
from indico.modules.categories.models.principals import CategoryPrincipal
from indico.core.db.sqlalchemy.principals import PrincipalType
from indico.modules.auth.models.identities import Identity
from indico.modules.users.models.users import User
from indico.modules.groups.models.groups import LocalGroup
from indico.web.flask.wrappers import IndicoBlueprint
from indico.web.util import get_request_user

from .forms import PhonebookSettingsForm

logger = logging.getLogger('indico_plugin_phonebook')
logger.info("Loaded indico_plugin_phonebook")

phonebook_bp = IndicoBlueprint('plugin_phonebook', __name__, url_prefix='/phonebook')


@phonebook_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint."""
    logger.debug("Received ping request")
    return jsonify({'status': 'ok', 'message': 'The Phonebook plugin is alive.'})


def list_groups(url):
    """Fetches groups and members from the Phonebook GraphQL API."""
    logger.info("Fetching groups and members from the phonebook API...")
    query = {
        "query": """
        query {
            members {
                id
                orcid_id
                name_first
                name_last
                email
                groups {
                    name
                    category
                    role
                }
                igroups {
                    name
                    role
                }
            }
        }
        """
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=query)

    if response.status_code != 200:
        logger.error("Failed to fetch data: %s %s", response.status_code, response.text)
        raise Exception(f"Error: {response.status_code}, {response.text}")

    data = response.json()
    logger.info("Successfully retrieved members data.")

    groups, members, managers = {}, [], []
    for member in data.get('data', {}).get('members', []):
        members.append({
            'first_name': member['name_first'],
            'last_name': member['name_last'],
            'email': member['email'],
            'orcid': member['orcid_id'],
            'full_access': False})
        for group in member['groups']:
            member_record = {
                'first_name': member['name_first'],
                'last_name': member['name_last'],
                'email': member['email'],
                'orcid': member['orcid_id'],
                'full_access': False}            
            group_name = group['name']
            if group_name not in groups:
                groups[group_name] = []

            role = (group['role'] or '').strip().lower()
            full_access = role not in ('', 'member')
            member_record['full_access'] = full_access
            if full_access and member_record not in managers:
                managers.append(member_record)            
            groups[group_name].append(member_record)

    logger.info("Organized %d members into %d groups.", len(members), len(groups))
    return groups, members, managers


def add_or_update_member(category, user, full_access):
    """Add or update user access to the category."""
    principal = CategoryPrincipal.query.filter_by(category=category, user_id=user.id).first()
    if principal:
        if principal.full_access != full_access:
            logger.info(f"Updating access for user {user.email}(full_access:{full_access}) in category {category}")
            if not (full_access and principal.read_access):
                principal.read_access = True            
            principal.full_access = full_access
    else:
        logger.info("Adding user %s to category %s", user.email, category.title)
        principal = CategoryPrincipal(
            category=category, principal=user,
            read_access=True, full_access=full_access
        )
        db.session.add(principal)
    db.session.commit()


def delete_member(principal):
    """Remove user from category."""
    logger.info("Removing user %s from category %s", principal.user.email, principal.category.title)
    db.session.delete(principal)
    db.session.commit()


def sync_category_membership_by_email(category, members, user_emails_index):
    """Sync category membership with given list of members (by email)."""
    existing = {}
    for  p in CategoryPrincipal.query.filter_by(category=category, type=PrincipalType.user).all():
        if p.user is not None:
            if p.user.is_deleted:
                delete_member(p)
                continue
            existing[p.user.email] = p

    incoming_emails = {m['email'] for m in members}
    for member in members:
        users = user_emails_index.get(member['email'], [])
        if users:
            for user in users: 
                add_or_update_member(category, user, member['full_access'])
        # else:
        #    logger.warning(f"User {member} not found in Indico.")

    for email, principal in existing.items():
        if email not in incoming_emails:
            delete_member(principal)


def sync_category_membership_by_orcid(category, members, user_orcid_index):
    """
    Sync category membership with given list of members (matched by ORCID).
    """
    # Build map of ORCID -> list of existing CategoryPrincipal
    existing = {}
    for principal in CategoryPrincipal.query.filter_by(category=category, type=PrincipalType.user).all():
        user = principal.user
        identities = Identity.query.filter_by(user_id=user.id, provider='cilogon').all()
        orcid = None
        for identity in identities:
            data = identity.data
            orcid_list = data.get("affiliation_data", [None])
            orcid = orcid_list[0] if isinstance(orcid_list, list) else orcid_list
            if orcid:
                existing.setdefault(orcid, []).append(principal)
        # Delete users with no orcid
        if not orcid:
            delete_member(principal)
        if principal.user.is_deleted:
            delete_member(principal)

    incoming_orcids = {m['orcid'] for m in members}
    for member in members:
        users = user_orcid_index.get(member['orcid'], [])
        if users:
            for user in users:
                add_or_update_member(category, user, member['full_access'])
        # else:
        #    logger.warning(f"User {member} not found in Indico.")

    for orcid, principals in existing.items():
        if orcid not in incoming_orcids:
            for principal in principals:
                delete_member(principal)


def sync_group_membership_by_email(group, members, user_email_index):
    """Sync a LocalGroup's members based on email."""
    existing_members = {}
    for user in list(group.members):
        if user.is_deleted:
            logger.info(f"Removing is_deleted user {user.email} from group {group.name}")
            group.members.remove(user)
            continue
        existing_members[user.email] = user

    incoming_emails = {m['email'] for m in members}
    # Add new members
    for member in members:
        users = user_email_index.get(member['email'], [])
        for user in users:
            if user not in group.members and not user.is_deleted:
                logger.info(f"Adding user {user.email} to group {group.name}")
                group.members.add(user)

    # Remove users not in incoming list
    for email, user in existing_members.items():
        if email not in incoming_emails:
            logger.info(f"Removing user {user.email} from group {group.name}")
            group.members.remove(user)

    db.session.commit()

def sync_group_membership_by_orcid(group, members, user_orcid_index):
    """Sync a LocalGroup's members based on ORCID."""
    # Build ORCID -> user mapping from group members
    group_orcids = {}
    for user in list(group.members):
        identities = Identity.query.filter_by(user_id=user.id, provider='cilogon').all()
        orcid = None
        for identity in identities:
            data = identity.data
            orcid_list = data.get("affiliation_data", [None])
            orcid = orcid_list[0] if isinstance(orcid_list, list) else orcid_list
            if orcid:
                group_orcids[orcid] = user
        # Delete users with no orcid
        if not orcid:
            logger.info(f"Removing user {user.email} with no ORCID from group {group.name}")
            group.members.remove(user)

    incoming_orcids = {m['orcid'] for m in members}

    # Add new members
    for member in members:
        users = user_orcid_index.get(member['orcid'], [])
        for user in users:
            if user not in group.members:
                logger.info(f"Adding user {user.email} to group {group.name}")
                group.members.add(user)

    # Remove users not in incoming list
    for orcid, user in group_orcids.items():
        if orcid not in incoming_orcids:
            logger.info(f"Removing user {user.email} from group {group.name}")
            group.members.remove(user)

    db.session.commit()


def soft_delete_category_recursive(category):
    """Recursively mark category and its children as deleted."""
    for sub in category.children:
        if not sub.is_deleted:
            soft_delete_category_recursive(sub)
    category.is_deleted = True
    db.session.add(category)
    db.session.commit()


def build_user_orcid_index(members):
    """
    Build an index of Indico users based on ORCIDs provided in a member list.
    """
    users = {}
    for member in members:
        orcid = member.get('orcid')
        if orcid:
            # if orcid in users:
            #   logger.warning(f"orcid {orcid} already defined for another user {member}.")                       
            users[orcid] = []

    identities = Identity.query.filter_by(provider='cilogon').all()
    for identity in identities:
        data = identity.data
        orcid_list = data.get("affiliation_data", [None])
        orcid = orcid_list[0] if isinstance(orcid_list, list) else orcid_list
        if orcid and orcid in users:
            if identity.user not in users[orcid] and not identity.user.is_deleted:
                users[orcid].append(identity.user)

    for member in members:
        orcid = member.get('orcid')
        #if orcid not in users or not users[orcid]:
        #    logger.warning(f"User {member} with {orcid}  not found in Indico.")

    return users


def build_user_email_index(members):
    """
    Build an index of Indico users based on emails provided in a member list.
    """
    users = {}
    for member in members:
        email = member.get('email')
        if email:
            users[email] = User.query.filter(User.email == email, User.is_deleted == False).all()
            if not users[email]:
                logger.warning(f"User {member} with {email}  not found in Indico.")
    return users


@phonebook_bp.route('/<experiment>/sync', methods=['POST'])
def sync(experiment):
    """Syncs one experiment's categories and members."""
    start_time = time.time()
    plugin = plugin_engine.get_plugin('phonebook')
    endpoints = plugin.endpoints

    if experiment not in endpoints:
        return jsonify({'error': f"Unknown experiment '{experiment}'"}), 500

    user, authorized = get_request_user()
    if not authorized or user is None:
        return jsonify({'error': 'Unauthorized access'}), 403

    config = endpoints[experiment]
    parent_title = config.get("parent_category_title")
    parent_id = config.get("parent_category")
    member_group = config.get("member_group", None)
    manager_group = config.get("manager_group", None)
    strategy = config.get('sync_strategy')

    if not parent_title and not parent_id:
        return jsonify({'error': f"Missing 'parent_category_title' or 'parent_category' for '{experiment}' in config."}), 500

    query = Category.query.filter_by(is_deleted=False)
    if parent_title:
        query = query.filter(Category.title == parent_title)
    if parent_id:
        query = query.filter(Category.id == parent_id)
    parent_category = query.first()
    if not parent_category:
        return jsonify({'error': f"Category '{parent_title}' '{parent_id}' not found!"}), 500

    if member_group:
         members_group = LocalGroup.query.filter_by(name=member_group).first()
         if not members_group:
             return jsonify({'error': f"Group for members '{member_group}' not found!"}), 500

    if manager_group:
         managers_group = LocalGroup.query.filter_by(name=manager_group).first()
         if not managers_group:
             return jsonify({'error': f"Group for managers '{manager_group}' not found!"}), 500

    if not parent_category.can_manage(user):
        return jsonify({'error': 'You do not have permission to synchronize the category {parent_title}.'}), 403

    groups, members, managers = list_groups(config['url'])
    if strategy == 'orcid':
        user_orcid_index = build_user_orcid_index(members)
        # sync_category_membership_by_orcid(parent_category, members, user_orcid_index)
        if member_group:
            sync_group_membership_by_orcid(members_group, members, user_orcid_index)
        if manager_group:
            sync_group_membership_by_orcid(managers_group, managers, user_orcid_index)
    else:
        user_email_index = build_user_email_index(members)
        # sync_category_membership_by_email(parent_category, members, user_email_index)
        if member_group:
             sync_group_membership_by_email(members_group, members, user_email_index)
        if manager_group:
             sync_group_membership_by_email(managers_group, managers, user_email_index)

    existing_categories = {
        cat.title: cat for cat in Category.query.filter_by(parent=parent_category, is_deleted=False).all()
    }

    for cat_title, cat_obj in existing_categories.items():
        if cat_title not in groups:
            soft_delete_category_recursive(cat_obj)

    for group_name, group_members in groups.items():
        if group_name not in existing_categories:
            logger.info("Creating new subcategory %s", group_name)
            subcategory = Category(
                title=group_name, parent=parent_category, protection_mode=2
            )
            db.session.add(subcategory)
            db.session.commit()
            existing_categories[group_name] = subcategory

        if strategy == 'orcid':
            sync_category_membership_by_orcid(existing_categories[group_name], group_members, user_orcid_index)
        else:
            sync_category_membership_by_email(existing_categories[group_name], group_members, user_email_index)

    db.session.commit()
    duration = round(time.time() - start_time, 3)
    logger.info("Synchronization completed in %.3f seconds.", duration)
    return jsonify({'status': 'ok', 'duration_seconds': duration}), 200


class PhonebookPlugin(IndicoPlugin):
    """Phonebook

    Synchronizes Indico categories and user access with Phonebook.
    """
    configurable = True
    settings_form = PhonebookSettingsForm
    default_settings = {
        'endpoints': '{}',
        'sync_strategy': 'email' 
    }

    @property
    def endpoints(self):
        try:
            return json.loads(self.settings.get('endpoints') or '{}')
        except Exception:
            logger.exception("Failed to parse 'endpoints' setting.")
            return {}

    def init(self):
        super().init()
        self.bp = phonebook_bp

    def get_blueprints(self):
        return self.bp
