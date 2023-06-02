from .directory_content import DirectoryContent
from .workspacemanager_exception import DirectoryContentException


class Workspace(DirectoryContent):
    saved_to_file_attributes = [
        'creation_time', 'modification_time', 'title', 'meta', 'content'
    ]

    def __init__(self, path: str):
        super().__init__(path)

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
            raise DirectoryContentException(DirectoryContentException.DOES_NOT_EXIST)

        self._read_attributes_from_json_file(self.absolute_filesystem_path)

    @classmethod
    def get(cls, path: str):
        workspace = Workspace(path)
        workspace.load()
        return workspace
