from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from rest_auth.authentication import User
import logging

logger = logging.getLogger('dtcd_workspaces')


class DirectoryView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, **kwargs):
        return {}
