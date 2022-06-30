import configparser
import os
from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults


PROJECT_DIR = Path(__file__).parent

default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'graph': {},
    'workspace': {},
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': 'password',
        'name': 'neo4j'
    },
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
    with open(Path(WORKSPACE_BASE_PATH) / DIR_META_NAME, 'w') as fw:
        fw.write('{"id": ""}')

if not os.path.isdir(WORKSPACE_TMP_PATH):
    os.mkdir(Path(WORKSPACE_TMP_PATH))
