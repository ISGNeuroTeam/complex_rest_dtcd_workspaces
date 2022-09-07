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
                logger.debug(f'List directory with path: {workspace_path}')
                content = Directory(path=workspace_path).list()
            except AccessDeniedError as e:
                logger.info(f'Access denied for listing directory with path: {workspace_path}. '
                             f'User: {request.user.username}')
                return access_denied_response(request.user)
            except Exception as e:
                logger.error(f'Failed to list directory with path: {workspace_path}. Error: {str(e)}')
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
            response = {'current_directory': content.get('current_directory'),
                        'content': content.get('workspaces', []) + content.get('directories', [])}
            logger.debug(f'Success listing directory with path: {workspace_path}. Response: {response}')
            return Response(response, status.HTTP_200_OK)
        elif 'dir' in qs:
            try:
                logger.debug(f'Get directory info with path: {workspace_path}')
                directory = Directory(path=workspace_path).read()
            except AccessDeniedError as e:
                logger.info(f'Access denied to get directory info with path: {workspace_path}. '
                             f'User: {request.user.username}')
                return access_denied_response(request.user)
            except Exception as e:
                logger.error(f'Failed to get directory info with path: {workspace_path}. Error: {str(e)}')
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
            logger.debug(f'Success getting directory info with path: {workspace_path}. Response: {directory}')
            return Response(directory, status.HTTP_200_OK)
        _id = qs['id'][0]
        try:
            logger.debug(f'Get workspace info with path - {workspace_path} and id - {_id}')
            workspace = Workspace(uid=_id, path=workspace_path).read()
        except AccessDeniedError as e:
            logger.info(f'Access denied to get workspace with path - {workspace_path} and id - {_id}')
            return access_denied_response(request.user)
        except Exception as e:
            logger.error(f'Failed to get workspace with path - {workspace_path} and id - {_id}')
            return Response(str(e), status.HTTP_400_BAD_REQUEST)
        logger.debug(f'Success getting workspace with path - {workspace_path} and id - {_id}. Response: {workspace}')
        return Response(workspace, status.HTTP_200_OK)

    def post(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        workspaces = request.data
        created = []
        for conf in workspaces:
            try:
                if 'dir' not in conf:
                    logger.debug(f'Create workspace with path - {workspace_path} and title - {conf.get("title")}')
                    ws = Workspace(path=workspace_path, _conf=conf)
                    ws.save()
                    created.append(
                        ws.id
                    )
                else:
                    logger.debug(f'Create directory with path - {workspace_path} and title - {conf.get("title")}')
                    dr = Directory(path=workspace_path, _conf=conf)
                    dr.save()
                    created.append(
                        dr.id
                    )
            except AccessDeniedError as e:
                logger.info(f'Access denied creating directory or workspace with path - {workspace_path} '
                             f'and title - {conf.get("title")}')
                return access_denied_response(request.user)
            except Exception as e:
                logger.error(f'Failed creating directory or workspace with path - {workspace_path} '
                             f'and title - {conf.get("title")}')
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        logger.debug(f'Created directories or workspaces with path - {workspace_path}')
        return Response(workspaces, status.HTTP_200_OK)

    def put(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        workspaces = request.data
        edited = []
        for conf in workspaces:
            try:
                if 'id' in conf:
                    logger.debug(f'Edit workspace with path - {workspace_path} and id - {conf.get("id")}')
                    edited.append(
                        Workspace(_conf=conf, path=workspace_path).update(_conf=conf)
                    )
                else:
                    logger.debug(f'Edit directory with path - {workspace_path} and title - {conf.get("title")}')
                    edited.append(
                        Directory(_conf=conf, path=workspace_path).update(_conf=conf)
                    )
            except AccessDeniedError as e:
                logger.info(f'Access denied editing workspace or directory with path - {workspace_path}')
                return access_denied_response(request.user)
            except Exception as e:
                logger.error(f'Failed editing workspace or directory with path - {workspace_path}')
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        logger.debug(f'Edited workspaces or directories with path - {workspace_path}')
        return Response(edited, status.HTTP_200_OK)

    def delete(self, request, **kwargs):
        workspace_path = kwargs.get('workspace_path', '')
        ids = request.data
        if not ids:
            try:
                logger.debug(f'Delete directory with path - {workspace_path}')
                Directory(path=workspace_path).delete()
            except AccessDeniedError as e:
                logger.info(f'Access denied deleting directory with path - {workspace_path}')
                return access_denied_response(request.user)
            except Exception as e:
                logger.error(f'failed deleting directory with path - {workspace_path}')
                return Response(str(e), status.HTTP_400_BAD_REQUEST)
        else:
            for _id in ids:
                try:
                    logger.debug(f'Delete workspace with path - {workspace_path} and id - {_id}')
                    Workspace(uid=_id, path=workspace_path).delete()
                except AccessDeniedError as e:
                    logger.info(f'Access denied deleting workspace with path - {workspace_path} and id - {_id}')
                    return access_denied_response(request.user)
                except Exception as e:
                    logger.error(f'Access denied deleting workspace with path - {workspace_path} and id - {_id}')
                    return Response(str(e), status.HTTP_400_BAD_REQUEST)
        logger.debug(f'Deleted workspaces or directory with path - {workspace_path}')
        return Response('success', status.HTTP_200_OK)
