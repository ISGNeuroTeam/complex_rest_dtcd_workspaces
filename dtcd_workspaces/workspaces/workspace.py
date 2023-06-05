from pathlib import Path
from .directory_content import DirectoryContent
from .workspacemanager_exception import DirectoryContentException


class Workspace(DirectoryContent):
    saved_to_file_attributes = [
        'creation_time', 'modification_time', 'title', 'meta', 'content'
    ]

    def __init__(self, path: str):
        super().__init__(path)
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
        workspace = Workspace(path)
        workspace.load()
        return workspace


DirectoryContent.register_child_class(Workspace)

