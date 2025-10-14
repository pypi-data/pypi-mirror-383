# Indico Phonebook Plugin

This Indico plugin automatically syncs categories, user access rights, and local groups with an external Phonebook service, such as ePIC, STAR, or sPHENIX collaboration directories.

## Features

- Health check endpoint (`/phonebook/ping`)
- Manual sync per experiment (`/phonebook/<experiment>/sync`)
- JSON-configurable experiment settings
- Two sync strategies: by **email** or **ORCID**
- Synchronizes:
  - Category membership (with access control)
  - Local Indico groups:
    - All members group
    - Managers group
  - Subcategories based on Phonebook groups

## Configuration

Update the plugin’s settings via Indico’s admin panel using a JSON configuration:

```json
{
  "epic": {
    "url": "https://phonebook.sdcc.bnl.gov/ePIC/",
    "parent_category_title": "ePIC",
    "member_group": "epic-members",
    "manager_group": "epic-managers",
    "sync_strategy": "orcid"
  }
}
```

Explanation:
* member_group: name of a LocalGroup to sync with all Phonebook members
* manager_group: name of a LocalGroup to sync with members with manager roles
* sync_strategy: either "email" or "orcid"


## Installation

Clone this repository into your Indico plugins directory:

```bash
cd ~/indico/plugins
git clone https://git.racf.bnl.gov/gitea/CDS/indico-plugin-phonebook.git
cd  indico-plugin-phonebook
git checkout tags/v1.0.0 -b v1.0.0 # to get a specific tag version
pip install -e .
```

Add in indico.conf:
```
PLUGINS = {'phonebook'}
```

Restart indico.
