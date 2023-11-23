import logging
from typing import List

from pathlib import Path
from rest_auth.authorization import auth_covered_method, authz_integration

from .utils import remove
from .directorycontent_exception import DirectoryContentException
from .directory_content import DirectoryContent
from ..settings import DIR_META_NAME, WORKSPACE_BASE_PATH
from .directory_base_object import DirectoryBaseObject
from rest_auth.exceptions import AccessDeniedError

class Directory(DirectoryBaseObject):
    content_file_name = DIR_META_NAME

    @property
    def absolute_content_file_path(self):
        return Path(self.absolute_filesystem_path) / DIR_META_NAME

    @auth_covered_method(action_name='dtcd_workspaces.read')
    def list(self) -> List[DirectoryContent]:
        """
        Returns directory content
        """
        directory_content_list = []
        for item in self.absolute_filesystem_path.iterdir():
            if not item.name == DIR_META_NAME:
                try:
                    dir_content = DirectoryContent.get(
                        self.get_relative_humanreadable_path(
                            str(item.relative_to(WORKSPACE_BASE_PATH))
                        )
                    )
                except DirectoryContentException as err:
                    logging.warning(f'Can\'t read directory content {item}. Skip it in list.\n {str(err)}')
                    continue
                except AccessDeniedError:
                    continue

                directory_content_list.append(dir_content)
        return directory_content_list

    @classmethod
    def get(cls, path: str) -> 'Directory':
        directory = Directory(path)
        directory.load()
        return directory

    @authz_integration(authz_action='delete', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.delete')
    def delete(self):
        # try to delete contents of directory first
        for dir_content in self.list():
            dir_content.delete()

        remove(self.absolute_filesystem_path)


DirectoryContent.register_child_class(Directory)