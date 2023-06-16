import configparser
import os
from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent

ROLE_MODEL_ACTIONS = {
    'create': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'read': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'update': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'delete': {
        'default_rule': True,  # allow or deny True or False, default True,
        'owner_applicability': True,  # default True
    },
    'move': {
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
# try to read path to config from environment
conf_path_env = os.environ.get('dtcd_workspaces_conf', None)

if conf_path_env is None:
    conf_path = PROJECT_DIR / 'dtcd_workspaces.conf'
else:
    conf_path = Path(conf_path_env).resolve()

# main config
config_parser = configparser.ConfigParser()

config_parser.read(conf_path)

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
