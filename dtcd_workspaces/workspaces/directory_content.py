import base64
import os
import json
import uuid

from typing import List
from pathlib import Path

from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from dtcd_workspaces.workspaces.utils import decode_name, encode_name

from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.utils import encode_name, decode_name


class DirectoryContent:
    saved_to_file_attributes = [
        'creation_time', 'modification_time', 'title', 'meta'
    ]

    def __init__(self, path: str):
        """
        Args:
            path (str): Human readable relative path
        """
        self.path: str = self._validate_path(path)
        self.creation_time: float = None
        self.modification_time: float = None
        self.title: str = self._get_title_from_path(path)
        self.meta: dict = None

    @staticmethod
    def _get_title_from_path(path: str) -> str:
        return Path(path).name

    @property
    def absolute_filesystem_path(self) -> Path:
        return Path(WORKSPACE_BASE_PATH) / self.relative_filesystem_path

    @property
    def relative_filesystem_path(self) -> str:
        return self._get_relative_filesystem_path(self.path)

    @staticmethod
    def get_absolute_filesystem_path(path: str) -> str:
        return str(Path(WORKSPACE_BASE_PATH) / DirectoryContent._get_relative_filesystem_path(path))

    @staticmethod
    def write_file(data: dict, absolute_filesystem_path: Path):
        temp_file = Path(WORKSPACE_TMP_PATH) / Path(f'temp_{str(uuid.uuid4())}')
        try:
            temp_file.write_text(json.dumps(data))
            temp_file.rename(absolute_filesystem_path)  # atomic operation
        except IOError:
            raise WorkspaceManagerException(WorkspaceManagerException.IO_ERROR, absolute_filesystem_path)


    @staticmethod
    def _get_relative_filesystem_path(human_readable_path: str) -> str:
        """
        Returns filesystem path
        """
        return os.sep.join(map(
            lambda path_part: encode_name(path_part),
            human_readable_path.split('/')  # no os.sep because it's parameter
        ))

    @staticmethod
    def _get_relative_humanreadable_path(relative_filesystem_path: str) -> str:
        """
        Returns humanreadable path
        """
        return '/'.join(
            map(
                lambda path_part: decode_name(path_part),
                relative_filesystem_path.split(os.sep)
            )
        )


    @staticmethod
    def _validate_path(path):
        tokens = path.split(os.sep)

        for token in tokens[:len(tokens) - 1]:  # security
            if token == '..' or token == '':
                raise WorkspaceManagerException(WorkspaceManagerException.PATH_WITH_DOTS, path)
        if tokens[-1] == '..':
            raise WorkspaceManagerException(WorkspaceManagerException.PATH_WITH_DOTS, path)
        return path

    def save(self):
        """
        Saves object to filesystem storage
        """
        raise NotImplementedError

    def load(self):
        """
        load attributes from filesystem
        """
        raise NotImplementedError

    @classmethod
    def get(cls, path: str) -> 'DirectoryContent':
        """
        Load object from filesystem storage
        """
        raise NotImplementedError

    def move(self, new_path):
        """
        Moves all content to new path
        """
        raise NotImplementedError

    def delete(self):
        pass









