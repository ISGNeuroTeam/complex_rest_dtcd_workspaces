from rest_framework.serializers import ValidationError

from rest.views import APIView
from rest.response import Response, status, ErrorResponse
from rest.permissions import IsAuthenticated
from rest_auth.authentication import User
from dtcd_workspaces.workspaces.directory import Directory
from .serializers import DirectorySerializer
from dtcd_workspaces.workspaces.workspacemanager_exception import DirectoryContentException
import logging

logger = logging.getLogger('dtcd_workspaces')


class DirectoryView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']

    def get(self, request, **kwargs):
        path = request.GET['path']
        try:
            directory = Directory.get(path)
        except DirectoryContentException as err:
            return ErrorResponse(
                http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err)
            )
        return Response(data=DirectorySerializer(directory).data, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        path = request.POST.get('path', None)
        if path is None:
            return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message='path query parameter need')

        # actions: create, update, move
        action = request.POST.get('action', 'create')
        if action == 'create':
            directory_serializer = DirectorySerializer(data=request.POST)
            try:
                directory_serializer.is_valid()
            except ValidationError as err:
                return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err))
            new_dir = directory_serializer.create()
            return Response(data=DirectorySerializer(new_dir).data, status=status.HTTP_200_OK)
        if action == 'update':
            try:
                directory = Directory.get(path)
            except DirectoryContentException.DOES_NOT_EXIST as err:
                return ErrorResponse(http_status=status.HTTP_404_NOT_FOUND, error_message=str(err))
            directory_serializer = DirectorySerializer(directory, data=request.POST, partial=True)
            directory_serializer.save()
            return Response(data=DirectorySerializer(directory).data, status=status.HTTP_200_OK)
        if action == 'move':
            new_path = request.POST.get('new_path', None)
            if new_path is None:
                return ErrorResponse(
                    http_status=status.HTTP_400_BAD_REQUEST, error_message='directory required for action update'
                )
            try:
                directory = Directory.get(path)
                directory.move(new_path)
            except DirectoryContentException as err:
                return ErrorResponse(http_status=status.HTTP_400_BAD_REQUEST, error_message=str(err))
            return Response(data=DirectorySerializer(directory), status=status.HTTP_200_OK)



