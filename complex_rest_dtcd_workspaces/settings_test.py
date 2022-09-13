import os
from pathlib import Path


PROJECT_DIR = Path(__file__)

while PROJECT_DIR.name != 'complex_rest':
    PROJECT_DIR = PROJECT_DIR.parent

PROJECT_DIR = PROJECT_DIR / 'plugin_dev' / 'dtcd_workspaces' / 'tests'

ROLE_MODEL_ACTIONS = {
    'workspace.create': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'workspace.read': {
            'default_rule': True,  # allow or deny True or False, default True,
            'owner_applicability': True,  # default True
    },
    'workspace.update': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'workspace.delete': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
}

default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'workspace': {},
}

# workspace configuration
WORKSPACE_BASE_PATH = PROJECT_DIR / 'root_workspace_directory'
WORKSPACE_TMP_PATH = PROJECT_DIR / 'tmp'
DIR_META_NAME = '.DIR_INFO'
