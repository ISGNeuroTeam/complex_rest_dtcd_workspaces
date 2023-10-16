from pathlib import Path
from rest_auth.authorization import auth_covered_method, authz_integration

from .utils import remove
from .directory_content import DirectoryContent
from .directorycontent_exception import DirectoryContentException


class FileBaseObject(DirectoryContent):

    @classmethod
    def is_path_for_cls(cls, path: str) -> bool:
        """
        Return True if path identify a FileBaseObject
        """
        try:
            cls._validate_path(path)
        except DirectoryContentException:
            return False
        absolute_filesystem_path = cls._get_absolute_filesystem_path(path)

        # check type postfix
        if absolute_filesystem_path.split('_')[-1] == cls.object_type_postfix:
            if not Path(absolute_filesystem_path).is_dir():
                return True
        return False

    @authz_integration(authz_action='update', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.update')
    def save(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise DirectoryContentException(DirectoryContentException.NO_DIR, str(parent_dir_path))

        self._write_attributes_to_json_file(self.absolute_filesystem_path)

    def load(self):
        """
        loads attributes from filename
        """
        if not self.absolute_filesystem_path.exists():
            raise DirectoryContentException(DirectoryContentException.DOES_NOT_EXIST, self.path)

        self._read_attributes_from_json_file(self.absolute_filesystem_path)

    @classmethod
    def get(cls, path: str):
        file_base_object = cls(path, initialized_from_inside_class=True)
        file_base_object.load()
        return file_base_object

    @authz_integration(authz_action='delete', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.delete')
    def delete(self):
        remove(self.absolute_filesystem_path)