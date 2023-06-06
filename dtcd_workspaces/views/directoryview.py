from .directory_content_view import DirectoryContentView
from .serializers import DirectorySerializer
from ..workspaces.directory import Directory


class DirectoryView(DirectoryContentView):
    serializer_class = DirectorySerializer
    directory_content_class = Directory
