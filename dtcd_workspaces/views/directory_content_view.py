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
    
    def get(self, request, **kwargs):
        path = request.GET['path']
        try:
            directory_content = self.directory_content_class.get(path)
        except DirectoryContentException as err:
            return ErrorResponse(
                http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err)
            )
        return Response(data=self.serializer_class(directory_content).data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        path = request.POST.get('path', None)
        if path is None:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message='path query parameter need')

        # actions: create, update, move, delete
        action = request.POST.get('action', 'create')
        try:
            if action == 'create':
                try:
                    existing_dir = self.directory_content_class.get(path)
                    return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message='Path already exist')
                except DirectoryContentException as err:  # if directory not exists than ok
                    pass

                directory_content_serializer = self.serializer_class(data=request.POST)
                try:
                    directory_content_serializer.is_valid()
                except ValidationError as err:
                    return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err))
                new_dir = directory_content_serializer.save()
                return Response(data=self.serializer_class(new_dir).data, status=status.HTTP_200_OK)
            elif action == 'update':
                directory_content = self.directory_content_class.get(path)
                directory_content_serializer = self.serializer_class(directory_content, data=request.POST, partial=True)
                directory_content_serializer.save()
                return Response(data=self.serializer_class(directory_content).data, status=status.HTTP_200_OK)
            elif action == 'move':
                new_path = request.POST.get('new_path', None)
                if new_path is None:
                    return ErrorResponse(
                        http_status=status.HTTP_400_BAD_REQUEST, error_message='new path required for action update'
                    )
                directory_content = self.directory_content_class.get(path)
                directory_content.move(new_path)
                return Response(data=self.serializer_class(directory_content), status=status.HTTP_200_OK)
            elif action == 'delete':
                directory_content = self.directory_content_class.get(path)
                directory_content.delete()
            else:
                return ErrorResponse(
                    http_status=status.HTTP_400_BAD_REQUEST,
                    error_message='Available actions are create, update, move, delete'
                )
        except DirectoryContentException as err:
            return ErrorResponse(http_status=status.HTTP_404_NOT_FOUND, error_message=str(err))

