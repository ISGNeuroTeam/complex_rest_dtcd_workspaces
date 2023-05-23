from rest_auth.models import KeyChainModel, AuthCoveredModel
from django.db import models


class WorkspaceKeyChain(KeyChainModel):
    auth_covered_class_import_str = 'dtcd_workspaces.workspaces.filesystem_workspaces.WorkspaceAuthCovered'


class WorkspaceAuthCoveredModel(AuthCoveredModel):
    keychain_model = WorkspaceKeyChain
    id = models.UUIDField(primary_key=True, editable=False)
    # path for workspace or directory
    obj_path = models.CharField(max_length=4096)
