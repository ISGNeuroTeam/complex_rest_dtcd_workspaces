import abc
import datetime
import json
import os.path
import uuid
from pathlib import Path
from typing import List, Dict, Union, Iterable, Optional

from dtcd_workspaces.workspaces import workspacemanager_exception
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from dtcd_workspaces.models import WorkspaceAuthCoveredModel
from rest_auth.authorization import IAuthCovered, auth_covered_method, AccessDeniedError, check_authorization
from .utils import manager, _get_dir_path, _is_uuid4, _decode_name, _rename, _remove, _copy, _get_file_name,\
    _encode_name
from ..settings import DIR_META_NAME, ROLE_MODEL_ACTIONS


class WorkspaceAuthCovered(WorkspaceAuthCoveredModel):
    """Provides additional interaction with Role Model"""

    def get_object(cls, obj_id: str) -> Optional['IAuthCovered']:
        """
        returns
        """

    def __init__(self, obj_path: str):
        """
        Args:
            obj_path (str): unique str, path for workspace of directory
        """
        super(self, WorkspaceAuthCovered).__init__()
        self.obj_path = obj_path
        self.permissions = None

    def get_plugin_name(self):
        return self.__module__.split('.')[0]

    @auth_covered_method(action_name='workspace.create')
    def can_create(self):
        return True

    @auth_covered_method(action_name='workspace.read')
    def can_read(self):
        return True

    @auth_covered_method(action_name='workspace.update')
    def can_update(self):
        return True

    @auth_covered_method(action_name='workspace.delete')
    def can_delete(self):
        return True

    def can_create_no_except(self):
        try:
            check_authorization(self, 'workspace.create')
        except AccessDeniedError:
            return False
        return True

    def can_read_no_except(self):
        try:
            check_authorization(self, 'workspace.read')
        except AccessDeniedError:
            return False
        return True

    def can_update_no_except(self):
        try:
            check_authorization(self, 'workspace.update')
        except AccessDeniedError:
            return False
        return True

    def can_delete_no_except(self):
        try:
            check_authorization(self, 'workspace.delete')
        except AccessDeniedError:
            return False
        return True

    def _load_permissions(self):
        self.permissions = {'create': self.can_create_no_except(),
                            'read': self.can_read_no_except(),
                            'update': self.can_update_no_except(),
                            'delete': self.can_delete_no_except()}


class BaseWorkspace(WorkspaceAuthCovered):
    """Represents any object related to workspaces (currently Workspace and Directory)"""

    # API_arg_name: Class_attr_name
    kwargs_map = {
        'workspace_path': 'path',
        'title': 'title',
        'creation_time': 'creation_time',
        'modification_time': 'modification_time',
        'is_dir': 'is_dir',
        'meta': 'meta'
    }

    manager = manager

    def __init__(self, *args, uid: str = None, path: str = None, title: str = None, creation_time: float = None,
                 modification_time: float = None, **kwargs):
        self.id = kwargs.get('_conf', {}).get('id', uid)  # get id from _conf for put method
        if '_conf' in kwargs:
            for key, value in kwargs.get('_conf', {}).items():
                if key in self.kwargs_map:
                    setattr(self, self.kwargs_map[key], value)
        self.path = self.path if hasattr(self, 'path') else _decode_name(path)
        self.title = self.title if hasattr(self, 'title') else title
        self.meta = self.meta if hasattr(self, 'meta') else None
        self.creation_time = getattr(self, 'creation_time', creation_time or datetime.datetime.now().timestamp())
        self.modification_time = None
        self.is_dir = False

        WorkspaceAuthCovered.__init__(self, path)

    @classmethod
    def is_workspace(cls, _path: Path) -> bool:
        return _path.is_file() and _path.exists() and _path.suffix == '.json'

    @classmethod
    @abc.abstractmethod
    def get_id(cls, _path: Path) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def filesystem_path(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _load_meta(self):
        raise NotImplementedError

    @classmethod
    def _get_new_id(cls) -> str:
        return str(uuid.uuid4())

    def as_dict(self):
        self._load_meta()
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def get_ids_chain(self, from_path: Path):
        """Get ids of object itself and all the object's parents"""
        ids = []
        # If object is a file i.e. workspace, then get its id and go for directories
        if self.is_workspace(from_path):
            file_name = _get_file_name(from_path)
            if _is_uuid4(file_name):
                ids.append(file_name)
            from_path = from_path.parent

        # Iterate through dirs and get ids
        while not from_path == self.manager.final_path:
            ids.append(Directory.get_id(from_path))
            from_path = from_path.parent
        ids.append(Directory.get_id(from_path))
        return ids

    def validate_move_to_target_directory(self, path: str):
        target = Directory(uid=self.id, title=self.title, path=_encode_name(path))
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


class Workspace(BaseWorkspace):
    kwargs_map = dict(**BaseWorkspace.kwargs_map, content='content')

    def __init__(self, *args, uid: str = None, path: str = None, title: str = None, creation_time: float = None,
                 modification_time: float = None, **kwargs):
        self.content = kwargs.get('_conf', {}).get('content')
        BaseWorkspace.__init__(self, *args,
                               uid=uid, path=path, title=title,
                               creation_time=creation_time, modification_time=modification_time,
                               **kwargs)
        self.id = self.id or self._get_new_id()
        self.plugin = self.get_plugin_name()
        self._from_file = None


    @classmethod
    def get_id(cls, _path: Path):
        return _path.with_suffix('').name

    def as_json(self):
        return json.dumps(self.as_dict())

    @property
    def _workspace_data(self) -> Dict:
        if not self._from_file:
            self._from_file = self._read_workspace_from_file()
        return self._from_file

    def _load_meta(self):
        self._load_permissions()
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

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path) / Path(self.id).with_suffix('.json')

    @auth_covered_method(action_name='workspace.read')
    def read(self) -> dict:
        self._load_content()
        return self.as_dict()

    @auth_covered_method(action_name='workspace.update')
    def update(self, *args, _conf: dict = None):

        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_WORKSPACE, self.filesystem_path)

        if 'new_path' in _conf:
            self._move(_conf['new_path'])
        else:
            self._update_workspace_data(_conf)
        return self.id

    def _move(self, path: str):
        target = self.validate_move_to_target_directory(path)

        self.can_update()

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

    @auth_covered_method(action_name='workspace.delete')
    def delete(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_WORKSPACE, self.filesystem_path)
        self._delete_from_file()


class Directory(BaseWorkspace):
    kwargs_map = dict(**BaseWorkspace.kwargs_map, id='id')

    dir_metafile_name = DIR_META_NAME

    def __init__(self, *args, uid: str = None, path: str = None, title: str = None, creation_time: float = None,
                 modification_time: float = None, **kwargs):
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
                self.path = str(Path(path) / _conf['title'])  # new directory
            elif 'new_title' in _conf:
                self.validate_dir_name(_conf['new_title'])  # rename
        BaseWorkspace.__init__(self, *args,
                               uid=uid, path=path, title=title,
                               creation_time=creation_time, modification_time=modification_time,
                               **kwargs)
        if not self.id:
            if self.exists():
                self._load_meta()
            else:
                self.id = self._get_new_id()

        WorkspaceAuthCovered.__init__(self)
        self.plugin = self.get_plugin_name()
        self.is_dir = True

    def exists(self):
        return self.filesystem_path.exists()

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

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path)

    @property
    def _meta_file(self):
        return self.filesystem_path / self.dir_metafile_name

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
    def is_workspace_directory(cls, _path: Path):
        return Path(_path, cls.dir_metafile_name).exists()

    @classmethod
    def get_id(cls, _path: Path):
        meta = cls.read_dir_meta(_path)
        return meta.get('id')

    def _iterdir(self) -> Iterable[Union[Workspace, 'Directory']]:
        for item in self.filesystem_path.iterdir():
            retrieved = self._retrieve_workspace_or_directory(item)
            if retrieved:
                yield retrieved

    def _recursive_iterdir(self) -> Iterable[Union[Workspace, 'Directory']]:
        for item in self.filesystem_path.rglob('*'):
            retrieved = self._retrieve_workspace_or_directory(item)
            if retrieved:
                yield retrieved

    def _retrieve_workspace_or_directory(self, item: Path) -> Union[Workspace, 'Directory']:
        if Workspace.is_workspace(item):
            human_readable_path = self.manager.get_human_readable_path(item.parent)
            return Workspace(uid=Workspace.get_id(item), path=_encode_name(human_readable_path)).accessed_by(self.user)
        elif Directory.is_workspace_directory(item):
            human_readable_path = self.manager.get_human_readable_path(item)
            return Directory(path=_encode_name(human_readable_path)).accessed_by(self.user)

    def _load_meta(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)
        meta: dict = self.read_dir_meta(self.filesystem_path)
        for key, value in meta.items():
            if key in self.kwargs_map:
                setattr(self, self.kwargs_map[key], value)
        if self.filesystem_path != self.manager.final_path:
            self.title = _decode_name(self.filesystem_path.name)
        self._load_permissions()

    def as_json(self):
        return json.dumps(self.as_dict())

    @auth_covered_method(action_name='workspace.read')
    def read(self) -> dict:
        if self.title:
            self.modification_time = os.path.getmtime(self.filesystem_path)
            return self.as_dict()
        if not self.path:
            return self.as_dict()
        raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)

    @auth_covered_method(action_name='workspace.read')
    def list(self) -> Dict[str, List]:
        """List directory content allowed to read by user"""
        directories, workspaces = [], []
        for item in self._iterdir():
            if item.can_read_no_except():
                if isinstance(item, Workspace):
                    item.modification_time = os.path.getmtime(item.filesystem_path)
                    workspaces.append(item.as_dict())
                elif isinstance(item, Directory):
                    item.modification_time = os.path.getmtime(item.filesystem_path)
                    directories.append(item.as_dict())
        current_dir = self.read()
        return {'workspaces': workspaces, 'directories': directories, 'current_directory': current_dir}

    @auth_covered_method(action_name='workspace.create')
    def create_workspace(self, *args, workspace_conf: dict = None) -> str:
        """Create workspace, write data on drive and return id"""
        workspace = Workspace(_conf=workspace_conf, path=_encode_name(self.path))
        workspace.save()
        return workspace.id

    @auth_covered_method(action_name='workspace.create')
    def create_dir(self, *args, _conf: dict = None) -> str:
        """Create directory, write data on drive and return id"""
        directory = Directory(_conf=_conf, path=self.path)
        directory.save()
        return directory.id

    @auth_covered_method(action_name='workspace.update')
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
        self.title = new_title
        self.path = str(Path(self.path).parent / new_title)  # update path according to new_title

    def _update_meta(self, new_meta: dict):
        self.meta = new_meta
        self.manager.write_file(
            self.as_dict(),
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
        target = self.validate_move_to_target_directory(path)

        # Check if we allowed to move all the content
        for item in self._recursive_iterdir():
            item.can_update()  # Will raise an error if not

        _copy(self.filesystem_path, target.filesystem_path)
        self._delete_directory()
        self.path = str(Path(path) / self.title)

    @auth_covered_method(action_name='workspace.delete')
    def delete(self):
        if not self.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.NO_DIR, self.filesystem_path)
        if self.manager.final_path == self.filesystem_path:
            raise WorkspaceManagerException(workspacemanager_exception.DELETING_ROOT, self.filesystem_path)

        for item in self._recursive_iterdir():
            item.can_delete()  # Will raise an error if not
        self._delete_directory()

    def is_empty_dir(self):
        content = os.listdir(self.filesystem_path)
        if len(content) == 1 and content[0] == self.dir_metafile_name:
            return True
        return False
