from pathlib import Path
from rest_auth.authorization import auth_covered_method, auth_covered_func

from .directory_content import DirectoryContent
from .directorycontent_exception import DirectoryContentException


class Workspace(DirectoryContent):
    saved_to_file_attributes = DirectoryContent.saved_to_file_attributes + [
        'content',
    ]

    @auth_covered_func(action_name='create')
    def __init__(self, path: str, initialized_from_inside_class=False):
        super().__init__(path, initialized_from_inside_class)
        self.content = None

    @classmethod
    def is_path_for_cls(cls, path: str) -> bool:
        """
        Return True if class identify a workspace
        """
        try:
            cls._validate_path(path)
        except DirectoryContentException:
            return False
        if not Path(cls._get_absolute_filesystem_path(path)).is_dir():
            return True
        return False

    @auth_covered_method(action_name='update')
    def save(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise DirectoryContentException(DirectoryContentException.NO_DIR, str(parent_dir_path))

        self._write_attributes_to_json_file(self.absolute_filesystem_path)

    @auth_covered_method(action_name='read')
    def load(self):
        """
        loads attributes from filename
        """
        if not self.absolute_filesystem_path.exists():
            raise DirectoryContentException(DirectoryContentException.DOES_NOT_EXIST, self.path)

        self._read_attributes_from_json_file(self.absolute_filesystem_path)

    @classmethod
    def get(cls, path: str):
        workspace = Workspace(path, initialized_from_inside_class=True)
        workspace.load()
        return workspace


DirectoryContent.register_child_class(Workspace)

