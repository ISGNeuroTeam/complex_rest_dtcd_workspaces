from pathlib import Path
from rest_auth.authorization import auth_covered_method, authz_integration

from .directorycontent_exception import DirectoryContentException
from .directory_content import DirectoryContent


class DirectoryBaseObject(DirectoryContent):
    # must be redefined in child classes
    content_file_name = None

    def __init__(self, path: str):
        super().__init__(path)

    @classmethod
    def is_path_for_cls(cls, path: str) -> bool:
        """
        Returns True id path identify a directory
        """
        absolute_path = Path(cls._get_absolute_filesystem_path(path))
        if absolute_path.is_dir() and (absolute_path / cls.content_file_name).exists():
            return True
        return False

    @property
    def absolute_content_file_path(self) -> Path:
        return Path(self.absolute_filesystem_path) / self.content_file_name

    def load(self):
        """
        Load attributes from meta filename
        """
        if not self.absolute_filesystem_path.exists():
            raise DirectoryContentException(
                DirectoryContentException.DOES_NOT_EXIST, str(self.absolute_filesystem_path)
            )
        self._read_attributes_from_json_file(self.absolute_content_file_path)

    @authz_integration(authz_action='update', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.update')
    def save(self):
        self._save_actions()

    def _save_actions(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise DirectoryContentException(DirectoryContentException.NO_DIR, str(parent_dir_path))
        self.absolute_filesystem_path.mkdir(exist_ok=True)
        self._write_attributes_to_json_file(self.absolute_content_file_path)

