#!/bin/sh
cp /dtcd_workspaces/docs/docker/keycloak/policies/policies.jar /opt/keycloak/providers/
/opt/keycloak/bin/kc.sh build
/opt/keycloak/bin/kc.sh import --optimized --dir /dtcd_workspaces/docs/docker/keycloak/realm_config
exec "$@"