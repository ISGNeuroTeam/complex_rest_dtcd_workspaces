import json
import os.path
from pathlib import Path
from typing import Dict
from dtcd_workspaces.workspaces.directory_content import DirectoryContent
from dtcd_workspaces.workspaces import workspacemanager_exception
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from .utils import _remove, _copy


class Workspace(DirectoryContent):
    # API_arg_name: Class_attr_name
    kwargs_map = {
        'workspace_path': 'path',
        'title': 'title',
        'creation_time': 'creation_time',
        'modification_time': 'modification_time',
        'is_dir': 'is_dir',
        'meta': 'meta',
        'content': 'content',
    }

    def __init__(self, *args, path: str = None, **kwargs):
        super().__init__(path, **kwargs)
        self.content = None
        if '_conf' in kwargs:
            for key, value in kwargs.get('_conf', {}).items():
                if key in self.kwargs_map:
                    setattr(self, self.kwargs_map[key], value)

        self.is_dir = False
        self._from_file = None

        if self.exists():
            self._load_meta()


    @classmethod
    def get_id(cls, _path: Path) -> str:
        return _path.with_suffix('').name

    @property
    def _workspace_data(self) -> Dict:
        if not self._from_file:
            self._from_file = self._read_workspace_from_file()
        return self._from_file

    def _load_meta(self):
        # self._load_permissions()
        if self.content is None:  # content was not loaded
            self.creation_time = self._workspace_data.get('creation_time')
            self.title = self._workspace_data.get('title')
            self.meta = self._workspace_data.get('meta')
            self.modification_time = os.path.getmtime(self.filesystem_path)

    def _load_content(self):
        self.content = self._workspace_data.get('content')
        self.creation_time = self._workspace_data.get('creation_time')
        self.title = self._workspace_data.get('title')
        self.meta = self._workspace_data.get('meta')
        self.modification_time = os.path.getmtime(self.filesystem_path)

    def _read_workspace_from_file(self) -> Dict:
        try:
            with self.filesystem_path.open() as fr:
                workspace = json.load(fr)
                return workspace
        except IOError:
            raise WorkspaceManagerException(workspacemanager_exception.NO_WORKSPACE, self.id)

    def _save_to_file(self):
        self.manager.write_file(
            self.as_dict(),
            self.filesystem_path
        )

    def _delete_from_file(self):
        _remove(self.filesystem_path)

    def save(self):
        self._save_to_file()
        # self.update_auth_record(_id=self.id, title=self.title)

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path) / Path(self.id).with_suffix('.json')

    # @check_authorization(action='workspace.read')
    def read(self) -> dict:
        self._load_content()
        return self.as_dict()

    # @check_authorization(action='workspace.update')
    def update(self, *args, _conf: dict = None):

        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_WORKSPACE, self.filesystem_path)

        if 'new_path' in _conf:
            self._move(_conf['new_path'])
        else:
            self._update_workspace_data(_conf)
        return self.id

    def _move(self, path: str):
        target = self.get_target_directory_content(path)

        # self.can_update()

        _copy(self.filesystem_path, target.filesystem_path)
        self._delete_from_file()
        self.path = path

    def _update_workspace_data(self, _conf: dict = None):
        # load all the workspace data from file
        self._load_content()
        # update data object with conf
        for key, value in _conf.items():
            if key in self.kwargs_map:
                setattr(self, self.kwargs_map[key], value)
        # write data back
        self._from_file = None  # cached values should be purged, because of update on file system
        self.save()

    # @check_authorization(action='workspace.delete')
    def delete(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_WORKSPACE, self.filesystem_path)
        self._delete_from_file()
        # self.delete_auth_record(ids=[self.id])