import json
import os.path
from pathlib import Path
from typing import List, Dict, Iterable
from dtcd_workspaces.workspaces.directory_content import DirectoryContent
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces import workspacemanager_exception
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from .utils import _get_dir_path, _decode_name, _rename, _remove, _copy, _encode_name


class Directory(DirectoryContent):
    # API_arg_name: Class_attr_name
    kwargs_map = {
        'workspace_path': 'path',
        'title': 'title',
        'creation_time': 'creation_time',
        'modification_time': 'modification_time',
        'is_dir': 'is_dir',
        'meta': 'meta',
        'id': 'id'
    }

    def __init__(self, *args, path: str = None, **kwargs):
        super().__init__(path, **kwargs)

        if '_conf' in kwargs:
            _conf = kwargs['_conf']
            if 'title' not in _conf and \
                    "new_title" not in _conf and \
                    "new_path" not in _conf and \
                    "new_meta" not in _conf:
                raise WorkspaceManagerException(workspacemanager_exception.NO_DIR_NAME)
            if 'new_path' in _conf:
                pass  # move
            elif 'title' in _conf:
                self.validate_dir_name(_conf['title'])
                self.title = _conf['title']
                self.path = str(Path(self.path) / self.title)  # new directory
            elif 'new_title' in _conf:
                self.validate_dir_name(_conf['new_title'])  # rename
            for key, value in kwargs.get('_conf', {}).items():
                if key in self.kwargs_map:
                    setattr(self, self.kwargs_map[key], value)

        self.is_dir = True

        if self.exists():
            self._load_meta()


    def _write_directory(self):
        if not self.filesystem_path.exists():
            try:
                self.filesystem_path.mkdir()
            except IOError:
                raise WorkspaceManagerException(workspacemanager_exception.UNABLE_TO_MKDIR, self.filesystem_path)

            self.manager.write_file(
                self.as_dict(),
                self._meta_file
            )
        else:
            raise WorkspaceManagerException(workspacemanager_exception.DIR_EXISTS)

    def validate_dir_name(self, name):
        if '/' in name:
            raise WorkspaceManagerException(workspacemanager_exception.SLASHES_IN_DIR_NAME, name)
        if not name:
            raise WorkspaceManagerException(workspacemanager_exception.EMPTY_DIR_NAME)
        if name == self.dir_metafile_name:
            raise WorkspaceManagerException(workspacemanager_exception.DIR_NAME_RESERVED_FOR_META, name)

    def _delete_directory(self):
        _remove(self.filesystem_path)

    def save(self):
        self._write_directory()
        # self.update_auth_record(_id=self.id, title=self.title)

    @property
    def _meta_file(self):
        return self.filesystem_path / self.dir_metafile_name

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path)

    @classmethod
    def read_dir_meta(cls, dir_path: Path) -> dict:
        """Read specific directory metadata"""
        meta_path = dir_path / cls.dir_metafile_name
        if meta_path.exists():
            with open(meta_path) as meta_file:
                meta_info = json.load(meta_file)
                return {
                    "id": meta_info.get("id"),
                    'title': meta_info.get("title"),
                    'creation_time': meta_info.get("creation_time"),
                    'meta': meta_info.get("meta"),
                    'modification_time': os.path.getmtime(dir_path)
                }
        return {}

    @classmethod
    def get_id(cls, _path: Path):
        meta = cls.read_dir_meta(_path)
        return meta.get('id')

    def _iterdir(self) -> Iterable[DirectoryContent]:
        for item in self.filesystem_path.iterdir():
            retrieved = self._retrieve_directory_content(item)
            if retrieved:
                yield retrieved

    def _recursive_iterdir(self) -> Iterable[DirectoryContent]:
        for item in self.filesystem_path.rglob('*'):
            retrieved = self._retrieve_directory_content(item)
            if retrieved:
                yield retrieved

    def _retrieve_directory_content(self, item: Path) -> DirectoryContent:
        if DirectoryContent.is_workspace(item):
            human_readable_path = self.manager.get_human_readable_path(item.parent)
            return Workspace(path=_encode_name(human_readable_path), _conf={'id': Workspace.get_id(item)})
        elif DirectoryContent.is_directory(item):
            human_readable_path = self.manager.get_human_readable_path(item)
            return Directory(path=_encode_name(human_readable_path))

    def _load_meta(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)
        meta: dict = self.read_dir_meta(self.filesystem_path)
        for key, value in meta.items():
            if key in self.kwargs_map:
                setattr(self, self.kwargs_map[key], value)
        if self.filesystem_path != self.manager.final_path:
            self.title = _decode_name(self.filesystem_path.name)
        # self._load_permissions()

    # @check_authorization(action='workspace.read')
    def read(self) -> dict:  # WTF?!
        if self.title:
            self.modification_time = os.path.getmtime(self.filesystem_path)
            return self.as_dict()
        if not self.path:
            return self.as_dict()
        raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)

    # @check_authorization(action='workspace.read')
    def list(self) -> Dict[str, List]:
        """List directory content allowed to read by user"""
        directories, workspaces = [], []
        for item in self._iterdir():
            # if item.can_read_no_except():
            item.modification_time = os.path.getmtime(item.filesystem_path)
            if isinstance(item, Workspace):
                workspaces.append(item.as_dict())
            elif isinstance(item, Directory):
                directories.append(item.as_dict())
        return {'workspaces': workspaces, 'directories': directories, 'current_directory': self.read()}

    # @check_authorization(action='workspace.update')
    def update(self, *args, _conf: dict = None):
        """Rename or move directory"""
        if 'new_path' in _conf:
            self._move(_conf['new_path'])
        elif 'new_title' in _conf:
            self._update_title(_conf['new_title'])
        elif 'new_meta' in _conf:
            self._update_meta(_conf['new_meta'])
        else:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_TITLE_OR_PATH_NOT_PROVIDED)

    def _update_title(self, new_title: str):
        self._rename(new_title)
        # Call auth parent class to update its record if it has changed
        # self.update_auth_record(_id=self.id, title=new_title)
        self.title = new_title
        self.path = str(Path(self.path).parent / new_title)  # update path according to new_title

    def _update_meta(self, new_meta: dict):
        self.meta = new_meta
        data = self.as_dict()
        data['meta'] = new_meta
        self.manager.write_file(
            data,
            self._meta_file
        )

    def _rename(self, title: str):
        if self.filesystem_path == self.manager.final_path:
            raise WorkspaceManagerException(workspacemanager_exception.IS_ROOT)
        path = _get_dir_path(title, self.filesystem_path.parent)
        if path == self.filesystem_path:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_PATH_EQ_OLD_PATH, path)
        if path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.INVALID_PATH, path)
        _rename(self.filesystem_path, path)

    def _move(self, path: str):
        target = self.get_target_directory_content(path)

        # Check if we allowed to move all the content
        # for item in self._recursive_iterdir():
        #     item.can_update()  # Will raise an error if not

        _copy(self.filesystem_path, target.filesystem_path)
        self._delete_directory()
        self.path = str(Path(path) / self.title)

    # @check_authorization(action='workspace.delete')
    def delete(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)
        if self.manager.final_path == self.filesystem_path:
            raise WorkspaceManagerException(workspacemanager_exception.DELETING_ROOT, self.filesystem_path)

        # Check if we allowed to delete all the content and gather auth_records ids to be deleted
        auth_record_ids = [self.id]
        # for item in self._recursive_iterdir():
        #     auth_record_ids.append(item.id)
        #     item.can_delete()  # Will raise an error if not -> has_perm
        self._delete_directory()
        # self.delete_auth_record(ids=auth_record_ids)
