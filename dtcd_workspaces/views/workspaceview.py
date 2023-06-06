from .directory_content_view import DirectoryContentView
from .serializers import WorkspaceSerializer
from ..workspaces.workspace import Workspace


class WorkspaceView(DirectoryContentView):
    serializer_class = WorkspaceSerializer
    directory_content_class = Workspace
