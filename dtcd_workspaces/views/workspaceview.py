from dtcd_workspaces.workspaces.filesystem_workspaces import Workspace, Directory
from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
from rest_auth.authentication import User
from rest_auth.exceptions import AccessDeniedError
import logging

logger = logging.getLogger('dtcd_workspaces')


def access_denied_response(user: User):
    return Response(f"Access denied for user with guid: {user.guid}", status.HTTP_403_FORBIDDEN)


class WorkspaceView(APIView):
    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        qs = dict(request.query_params)
        if 'id' not in qs and 'dir' not in qs:  # dir means that user wants dir info not listing the dir
            try:
                content = Directory(path=workspace_path).accessed_by(request.user).list()
            except AccessDeniedError as e:
                return access_denied_response(request.user)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
            response = {'current_directory': content.get('current_directory'),
                        'content': content.get('workspaces', []) + content.get('directories', [])}
            return Response(response, status.HTTP_200_OK)
        elif 'dir' in qs:
            try:
                workspace = Directory(path=workspace_path).accessed_by(request.user).read()
            except AccessDeniedError as e:
                return access_denied_response(request.user)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
            return Response(workspace, status.HTTP_200_OK)
        _id = qs['id'][0]
        try:
            workspace = Workspace(uid=_id, path=workspace_path).accessed_by(request.user).read()
        except AccessDeniedError as e:
            return access_denied_response(request.user)
        except Exception as e:
            return Response(str(e), status.HTTP_400_BAD_REQUEST)
        return Response(workspace, status.HTTP_200_OK)

    def post(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        workspaces = request.data
        created = []
        for conf in workspaces:
            try:
                if 'dir' not in conf:
                    created.append(
                        Directory(path=workspace_path).accessed_by(request.user).create_workspace(workspace_conf=conf)
                    )
                else:
                    created.append(
                        Directory(path=workspace_path).accessed_by(request.user).create_dir(_conf=conf)
                    )
            except AccessDeniedError as e:
                return access_denied_response(request.user)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        return Response(workspaces, status.HTTP_200_OK)

    def put(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        workspaces = request.data
        edited = []
        for conf in workspaces:
            try:
                if 'id' in conf:
                    edited.append(
                        Workspace(_conf=conf, path=workspace_path).accessed_by(request.user).update(_conf=conf)
                    )
                else:
                    edited.append(
                        Directory(_conf=conf, path=workspace_path).accessed_by(request.user).update(_conf=conf)
                    )
            except AccessDeniedError as e:
                return access_denied_response(request.user)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        return Response(edited, status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        ids = request.data
        if not ids:
            try:
                Directory(path=workspace_path).accessed_by(request.user).delete()
            except AccessDeniedError as e:
                return access_denied_response(request.user)
            except Exception as e:
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        else:
            for _id in ids:
                try:
                    Workspace(uid=_id, path=workspace_path).accessed_by(request.user).delete()
                except AccessDeniedError as e:
                    return access_denied_response(request.user)
                except Exception as e:
                    return Response(str(e), status.HTTP_400_BAD_REQUEST)
        return Response('success', status.HTTP_200_OK)
