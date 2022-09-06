import configparser
import os
from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent
PLUGIN_NAME = PROJECT_DIR.name

ROLE_MODEL_AUTH_COVERED_CLASSES = [
    "workspaces.filesystem_workspaces.AuthCoveredWorkspace",
    "workspaces.filesystem_workspaces.AuthCoveredDirectory",
    "workspaces.filesystem_workspaces.WorkspacesKeychain"
]

ROLE_MODEL_AUTH_COVERED_CLASSES = [
    PLUGIN_NAME + "." + item  # plugin.relpathtoclass
    for item in ROLE_MODEL_AUTH_COVERED_CLASSES
]

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

# main config
config_parser = configparser.ConfigParser()
config_parser.read(PROJECT_DIR / 'dtcd_workspaces.conf')
# FIXME option false in config gets converted from 'false' to True
ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

# service dirs
if not os.path.isdir(PROJECT_DIR / "plugins"):
    os.mkdir(PROJECT_DIR / "plugins")

if not os.path.isdir(PROJECT_DIR / "public"):
    os.mkdir(PROJECT_DIR / "public")

# workspace configuration
WORKSPACE_BASE_PATH = ini_config['workspace']['base_path']
WORKSPACE_TMP_PATH = ini_config['workspace']['tmp_path']
DIR_META_NAME = ini_config['workspace'].get('dir_meta', '.DIR_INFO')

if not os.path.isdir(WORKSPACE_BASE_PATH):
    os.mkdir(Path(WORKSPACE_BASE_PATH))

if not (Path(WORKSPACE_BASE_PATH) / DIR_META_NAME).exists():
    with open(Path(WORKSPACE_BASE_PATH) / DIR_META_NAME, 'w') as fw:
        fw.write('{"id": ""}')

if not os.path.isdir(WORKSPACE_TMP_PATH):
    os.mkdir(Path(WORKSPACE_TMP_PATH))

# configure your own database if you need
DATABASE = {
        "ENGINE": 'django.db.backends.postgresql',
        "NAME": ini_config['db_conf']['database'],
        "USER": ini_config['db_conf']['user'],
        "PASSWORD": ini_config['db_conf']['password'],
        "HOST": ini_config['db_conf']['host'],
        "PORT": ini_config['db_conf']['port']
}
