from dtcd_workspaces.workspaces.filesystem_workspaces import Workspace, Directory, WorkspaceManagerException
from dtcd_workspaces.workspaces import utils, workspacemanager_exception
from rest_auth.authorization import check_authorization
from typing import List, Dict, Union
from pathlib import Path


class TWorkspace(Workspace):

    @staticmethod
    def get_plugin_name(view_filepath: str):
        return 'dtcd_workspaces'

    def validate_move_to_target_directory(self, path: str, user):

        target = TDirectory(uid=self.id, title=self.title, path=utils._encode_name(path)).accessed_by(user)
        target.can_create()
        if not target.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.INVALID_PATH, path)
        if target.filesystem_path == self.filesystem_path.parent:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_PATH_EQ_OLD_PATH, path)
        if self.filesystem_path in target.filesystem_path.parents:
            raise WorkspaceManagerException(workspacemanager_exception.MOVING_DIR_INSIDE_ITSELF,
                                            self.filesystem_path,
                                            target.filesystem_path)

        return target


class TDirectory(Directory):

    @staticmethod
    def get_plugin_name(view_filepath: str):
        return 'dtcd_workspaces'

    @check_authorization(action='workspace.read')
    def list(self) -> Dict[str, List]:
        """List directory content allowed to read by user"""
        directories, workspaces = [], []
        for item in self._iterdir():
            if item.can_read_no_except():
                if isinstance(item, TWorkspace):
                    workspaces.append(item.as_dict())
                elif isinstance(item, TDirectory):
                    directories.append(item.as_dict())

        return {'workspaces': workspaces, 'directories': directories}

    def _retrieve_workspace_or_directory(self, item: Path) -> Union[TWorkspace, 'TDirectory']:
        if Workspace.is_workspace(item):
            human_readable_path = self.manager.get_human_readable_path(item.parent)
            return TWorkspace(uid=Workspace.get_id(item), path=utils._encode_name(human_readable_path)).accessed_by(self.user)
        elif Directory.is_workspace_directory(item):
            human_readable_path = self.manager.get_human_readable_path(item)
            return TDirectory(path=utils._encode_name(human_readable_path)).accessed_by(self.user)

    def validate_move_to_target_directory(self, path: str, user):

        target = TDirectory(uid=self.id, title=self.title, path=utils._encode_name(path)).accessed_by(user)
        target.can_create()
        if not target.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.INVALID_PATH, path)
        if target.filesystem_path == self.filesystem_path.parent:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_PATH_EQ_OLD_PATH, path)
        if self.filesystem_path in target.filesystem_path.parents:
            raise WorkspaceManagerException(workspacemanager_exception.MOVING_DIR_INSIDE_ITSELF,
                                            self.filesystem_path,
                                            target.filesystem_path)

        return target