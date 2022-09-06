from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from dtcd_workspaces.workspaces.filesystem_workspaces import WorkspacesKeychain
from rest_auth.authentication import User
import logging

logger = logging.getLogger('dtcd_workspaces')


class TestView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']

    def get(self, request, **kwargs):
        wk = WorkspacesKeychain.objects.create()
        return Response({'msg': 'well done!'}, status.HTTP_200_OK)
