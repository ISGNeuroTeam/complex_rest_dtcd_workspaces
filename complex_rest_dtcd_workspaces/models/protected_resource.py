from django.db import models
from mixins.models import NamedModel
from dtcd_workspaces.models.models import WorkspacesKeychain


class ProtectedResource(NamedModel):
    object_id = models.CharField(max_length=256, blank=True, null=False, unique=True)
    owner = models.IntegerField(null=False, blank=False)
    keychain = models.ForeignKey(WorkspacesKeychain, related_name='protected_resources', on_delete=models.CASCADE)