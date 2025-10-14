# -*- coding: utf-8 -*-
"""
Form definitions for the Indico Phonebook Plugin.

This file defines the plugin's admin settings form, including a JSON
text area for endpoint configuration with validation against a strict schema.

"""
import json

from wtforms import TextAreaField, ValidationError, SelectField

from wtforms.widgets import TextArea
from indico.web.forms.base import IndicoForm
from jsonschema import validate, ValidationError as JSONSchemaValidationError


# Define the expected JSON Schema
ENDPOINTS_SCHEMA = {
    "type": "object",
    "additionalProperties": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "format": "uri"},
            "parent_category_title": {"type": "string"},
            "parent_category": {"type": "integer"},
            "member_group": {"type": "string"},
            "manager_group": {"type": "string"},
            "sync_strategy": {
                "type": "string",
                "enum": ["email", "orcid"],
                "description": "Choose how to map users: by email or ORCID. Defaults to email."
            }
        },
        "required": ["url", "sync_strategy"],
        "anyOf": [
            {"required": ["parent_category_title"]},
            {"required": ["parent_category"]}
        ],
        "additionalProperties": False
    }
}

def validate_json(form, field):
    """Validate that the field contains valid JSON and matches the expected schema."""
    try:
        data = json.loads(field.data)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON: {str(e)}")

    try:
        validate(instance=data, schema=ENDPOINTS_SCHEMA)
    except JSONSchemaValidationError as e:
        raise ValidationError(f"JSON schema validation error: {e.message}")


class PhonebookSettingsForm(IndicoForm):
    """Settings form for the Phonebook plugin.

    Includes a JSON textarea for defining experiment endpoints.
    """
    endpoints = TextAreaField(
        'Endpoints (JSON)',
        widget=TextArea(),
        description='Define endpoint configuration as a JSON object.',
        validators=[validate_json],
        render_kw={
            'rows': 20,
            'cols': 90,
            'style': 'font-family: monospace; resize: vertical;'
        }
    )
