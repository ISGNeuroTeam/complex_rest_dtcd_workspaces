import datetime
import json
from typing import List

from pathlib import Path
from .workspacemanager_exception import WorkspaceManagerException
from .directory_content import DirectoryContent
from ..settings import DIR_META_NAME, WORKSPACE_BASE_PATH


class Directory(DirectoryContent):
    def __init__(self, path: str, ):
        super().__init__(path)

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
        with open(self.dir_meta_path, 'r', encoding='UTF-8') as f:
            dir_meta = json.load(f)
            for attr in self.saved_to_file_attributes:
                setattr(self, attr, dir_meta[attr])

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
        temp_dict = {}
        for attr in self.saved_to_file_attributes:
            temp_dict[attr] = getattr(self, attr)
        if self.creation_time is None:
            self.creation_time = datetime.datetime.now().timestamp()
        else:
            self.modification_time = datetime.datetime.now().timestamp()

        self.write_file(temp_dict, self.dir_meta_path)


