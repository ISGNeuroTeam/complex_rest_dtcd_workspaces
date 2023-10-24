from .directory_content import DirectoryContent
from .filebaseobject import FileBaseObject


class WorkspaceTab(FileBaseObject):
    saved_to_file_attributes = [
          'id', 'creation_time', 'modification_time', 'keychain_id', 'owner_guid',
          'editName'
    ]
    object_type_postfix = 'tab'

    def __init__(self, path: str, initialized_from_inside_class=False):
        self.path: str = self._validate_path(path)
        self.creation_time: float = None
        self.modification_time: float = None
        self.owner_guid = None
        self.keychain_id = None
        self.id = None
        self.isActive = None
        self.editName = None
        self.plugins = None


DirectoryContent.register_child_class(WorkspaceTab)

