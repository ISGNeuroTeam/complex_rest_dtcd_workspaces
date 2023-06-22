import datetime
import json
from typing import List

from pathlib import Path
from rest_auth.authorization import auth_covered_method, auth_covered_func

from .utils import remove
from .directorycontent_exception import DirectoryContentException
from .directory_content import DirectoryContent
from ..settings import DIR_META_NAME, WORKSPACE_BASE_PATH


class Directory(DirectoryContent):
    def __init__(self, path: str, initialized_from_inside_class=False):
        super().__init__(path, initialized_from_inside_class)

    @classmethod
    def is_path_for_cls(cls, path: str) -> bool:
        """
        Returns True id path identify a directory
        """
        if Path(cls._get_absolute_filesystem_path(path)).is_dir():
            return True
        return False

    @property
    def dir_meta_path(self):
        return Path(self.absolute_filesystem_path) / DIR_META_NAME

    @auth_covered_method(action_name='read')
    def list(self) -> List[DirectoryContent]:
        """
        Returns directory content
        """
        directory_content_list = []
        for item in self.absolute_filesystem_path.iterdir():
            if not item.name == DIR_META_NAME:
                directory_content_list.append(
                    DirectoryContent.get(
                        self._get_relative_humanreadable_path(
                            str(item.relative_to(WORKSPACE_BASE_PATH))
                        )
                    )
                 )
        return directory_content_list

    def load(self):
        """
        Load attributes from meta filename
        """
        if not self.absolute_filesystem_path.exists():
            raise DirectoryContentException(DirectoryContentException.DOES_NOT_EXIST, str(self.absolute_filesystem_path))
        self._read_attributes_from_json_file(self.dir_meta_path)

    @classmethod
    def get(cls, path: str) -> 'Directory':
        directory = Directory(path, initialized_from_inside_class=True)
        directory.load()
        return directory

    @auth_covered_method(action_name='update')
    def save(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise DirectoryContentException(DirectoryContentException.NO_DIR, str(parent_dir_path))
        self.absolute_filesystem_path.mkdir(exist_ok=True)
        self._write_attributes_to_json_file(self.dir_meta_path)

    @auth_covered_method(action_name='delete')
    def delete(self):
        # try to delete contents of directory first
        for dir_content in self.list():
            dir_content.delete()

        remove(self.absolute_filesystem_path)


DirectoryContent.register_child_class(Directory)



