from .directory_content import DirectoryContent
from .filebaseobject import FileBaseObject


class WorkspaceTab(FileBaseObject):
    check_permissions_in_auth_covered_methods = False
    saved_to_file_attributes = [
          'id', 'creation_time', 'modification_time', 'keychain_id', 'owner_guid',
          'editName', 'name', 'isActive', 'order'
    ]
    object_type_postfix = 'tab'

    def __init__(self, path: str):
        self.path: str = self._validate_path(path)
        self.creation_time: float = None
        self.modification_time: float = None
        self.owner_guid = None
        self.keychain_id = None
        self.id = None
        self.isActive = None
        self.editName = None
        self.name = None
        self.order = None

    @property
    def title(self) -> str:
        return self.name

DirectoryContent.register_child_class(WorkspaceTab)

