import datetime
import json
from typing import List

from pathlib import Path
from .workspacemanager_exception import WorkspaceManagerException
from .directory_content import DirectoryContent
from ..settings import DIR_META_NAME, WORKSPACE_BASE_PATH


class Directory(DirectoryContent):
    def __init__(self, path: str):
        super().__init__(path)
        self.content = None

    @property
    def dir_meta_path(self):
        return Path(self.absolute_filesystem_path) / DIR_META_NAME

    def list(self) -> List[DirectoryContent]:
        """
        Returns directory content
        """
        pass

    def load(self):
        """
        Load attributes from meta filename
        """
        if not self.absolute_filesystem_path.exists():
            raise WorkspaceManagerException(WorkspaceManagerException.NO_DIR, str(self.absolute_filesystem_path))
        self._read_attributes_from_json_file(self.dir_meta_path)

    @classmethod
    def get(cls, path: str) -> 'Directory':
        directory = Directory(path)
        directory.load()
        return directory

    def save(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise WorkspaceManagerException(WorkspaceManagerException.NO_DIR, str(parent_dir_path))
        self.absolute_filesystem_path.mkdir(exist_ok=True)
        self._write_attributes_to_json_file(self.dir_meta_path)




