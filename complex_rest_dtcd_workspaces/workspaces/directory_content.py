from abc import ABC, abstractmethod
import uuid
import json
from .utils import FilesystemWorkspaceManager, _encode_name, _is_uuid4, _get_file_name, manager
from typing import Dict
from pathlib import Path
from dtcd_workspaces.workspaces import workspacemanager_exception
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from ..settings import DIR_META_NAME


class DirectoryContent(ABC):
    kwargs_map: Dict[str, str]
    manager: FilesystemWorkspaceManager = manager
    dir_metafile_name = DIR_META_NAME

    def __init__(self, path: str):
        self.path = path

    @classmethod
    def is_workspace(cls, _path: Path) -> bool:
        return _path.is_file() and _path.exists() and _path.suffix == '.json'

    @classmethod
    def is_directory(cls, _path: Path):
        return Path(_path, cls.dir_metafile_name).exists()

    @classmethod
    def _get_new_id(cls) -> str:
        return str(uuid.uuid4())

    @abstractmethod
    def _load_meta(self):
        raise NotImplementedError

    @abstractmethod
    def read(self):
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError

    @abstractmethod
    def save(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_id(cls, _path: Path):
        raise NotImplementedError

    def as_dict(self):
        self._load_meta()
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def as_json(self):
        return json.dumps(self.as_dict())

    def exists(self):
        return self.filesystem_path.exists()

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path)

    def get_target_directory_content(self, path: str):

        target = DirectoryContent(path=_encode_name(path))
        if not target.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.INVALID_PATH, path)
        if target.filesystem_path == self.filesystem_path.parent:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_PATH_EQ_OLD_PATH, path)
        if self.filesystem_path in target.filesystem_path.parents:
            raise WorkspaceManagerException(workspacemanager_exception.MOVING_DIR_INSIDE_ITSELF,
                                            self.filesystem_path,
                                            target.filesystem_path)

        return target

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
            ids.append(DirectoryContent.get_id(from_path))
            from_path = from_path.parent
        ids.append(DirectoryContent.get_id(from_path))
        return ids
