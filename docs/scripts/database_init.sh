#!/bin/bash

# Creates initial records in rest_auth for Role Model in workspaces.
# Uses custom Django command for this.

# <project>/plugins/<this-plugin>/
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# go to project's directory
cd $SCRIPT_DIR/../..

# use project's venv
python="venv/bin/python"

# create initial entries
# limit the loaded plugins to this particular one
export COMPLEX_REST_PLUGIN_NAME="dtcd_workspaces"

sudo -u postgres psql -h localhost -p 5433 << EOF
CREATE ROLE dtcd_workspaces LOGIN PASSWORD 'password';
EOF

sudo -u postgres psql -h localhost -p 5433 << EOF
CREATE DATABASE dtcd_workspaces;
EOF

sudo -u postgres psql -h localhost -p 5433 << EOF
grant all privileges on database dtcd_workspaces to dtcd_workspaces;
EOF

$python complex_rest/manage.py create_root_records