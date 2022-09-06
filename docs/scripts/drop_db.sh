#!/bin/bash
  
sudo -u postgres psql -h localhost -p 5433 << EOF
REASSIGN OWNED BY dtcd_workspaces TO postgres;
DROP OWNED BY dtcd_workspaces;
drop database dtcd_workspaces;
EOF
