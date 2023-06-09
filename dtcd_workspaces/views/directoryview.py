from rest.response import Response, status, ErrorResponse
from .directory_content_view import DirectoryContentView
from .serializers import DirectorySerializer, WorkspaceSerializer
from ..workspaces.directory import Directory
from ..workspaces.workspace import Workspace
from ..workspaces.directorycontent_exception import DirectoryContentException


class DirectoryView(DirectoryContentView):
    serializer_class = DirectorySerializer
    directory_content_class = Directory

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_handlers.update(
            {
                'list': self._list
            }
        )

    def _list(self, path: str, request, **kwargs):
        try:
            directory = Directory.get(path)
        except DirectoryContentException as err:
            return ErrorResponse(http_status=status.HTTP_404_NOT_FOUND, error_message=str(err))

        directory_content_list = directory.list()
        workspaces = list(
            filter(
                lambda dir_content_instance: isinstance(dir_content_instance, Workspace),
                directory_content_list
            )
        )
        directories = list(
            filter(
                lambda dir_content_instance: isinstance(dir_content_instance, Directory),
                directory_content_list
            )
        )
        return Response(
            data={
                'workspaces': WorkspaceSerializer(workspaces, many=True).data,
                'directories': DirectorySerializer(directories, many=True).data,
            }
        )


