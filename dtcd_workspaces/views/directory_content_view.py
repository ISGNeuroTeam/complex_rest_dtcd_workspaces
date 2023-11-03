from rest_framework.serializers import ValidationError

from rest.views import APIView
from rest.response import Response, status, ErrorResponse
from rest.permissions import IsAuthenticated
from dtcd_workspaces.workspaces.directorycontent_exception import DirectoryContentException
import logging

logger = logging.getLogger('dtcd_workspaces')


class DirectoryContentView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']
    # defined in child classes
    serializer_class = None
    directory_content_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_handlers = {
            'create': self._create,
            'update': self._update,
            'delete': self._delete,
            'move': self._move,
            'get': self._get
        }

    def get(self, request, **kwargs):
        path = request.GET.get('path', None)
        if path is None:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message='path query parameter need')

        action = request.GET.get('action', 'get')

        try:
            try:
                return self.action_handlers[action](path, request, **kwargs)
            except KeyError as err:
                return ErrorResponse(
                    http_status=status.HTTP_400_BAD_REQUEST,
                    error_message='Action must be passed in query string, \
                        Available actions are: ' + ', '.join(self.action_handlers.keys())
                )
        except DirectoryContentException as err:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err))

    def post(self, request, **kwargs):
        path = request.GET.get('path', None)
        if path is None:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message='path query parameter need')

        # actions: create, update, move, delete
        action = request.GET.get('action', 'create')
        try:
            try:
                action_method = self.action_handlers[action]
            except KeyError as err:
                return ErrorResponse(
                    http_status=status.HTTP_400_BAD_REQUEST,
                    error_message='Action must be passed in query string, \
                            Available actions are: ' + ', '.join(self.action_handlers.keys())
                )
            return action_method(path, request, **kwargs)

        except DirectoryContentException as err:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err))

    def _get(self, path, request, **kwargs):
        try:
            directory_content = self.directory_content_class.get(path)
        except DirectoryContentException as err:
            return ErrorResponse(
                http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err)
            )
        return Response(data=self.serializer_class(directory_content).data, status=status.HTTP_200_OK)

    def _create(self, path, request, **kwargs):
        directory_content_dct = dict(request.data)
        directory_content_dct.update({'path': path})
        directory_content_serializer = self.serializer_class(
            data=directory_content_dct
        )
        if directory_content_serializer.is_valid():
            new_dir = directory_content_serializer.save()
        else:
            return ErrorResponse(
                data=directory_content_serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
                error_message='Invalid data'
            )
        return Response(data=self.serializer_class(new_dir).data, status=status.HTTP_200_OK)

    def _update(self, path, request, **kwargs):
        directory_content = self.directory_content_class.get(path)
        directory_content_dct = dict(request.data)
        directory_content_dct.update({'path': path})
        directory_content_serializer = self.serializer_class(directory_content, data=directory_content_dct, partial=True)
        if directory_content_serializer.is_valid():
            directory_content_serializer.save()
        else:
            return ErrorResponse(
                data=directory_content_serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
                error_message='Invalid data'
            )
        return Response(data=self.serializer_class(directory_content).data, status=status.HTTP_200_OK)

    def _move(self, path, request, **kwargs):
        new_path = request.data.get('new_path', None)
        if new_path is None:
            return ErrorResponse(
                http_status=status.HTTP_400_BAD_REQUEST, error_message='new path required for action move'
            )
        directory_content = self.directory_content_class.get(path)
        directory_content.move(new_path)
        return Response(data=self.serializer_class(directory_content).data, status=status.HTTP_200_OK)

    def _delete(self, path, request, **kwargs):
        directory_content = self.directory_content_class.get(path)
        directory_content.delete()
        return Response(status=status.HTTP_200_OK)

