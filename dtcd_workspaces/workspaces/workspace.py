from rest_auth.authorization import auth_covered_method, authz_integration

from .utils import remove
from .directory_base_object import DirectoryBaseObject
from .directory_content import DirectoryContent


class Workspace(DirectoryBaseObject):
    content_file_name = '.WORKSPACE'
    saved_to_file_attributes = DirectoryContent.saved_to_file_attributes + [
        'content',
    ]

    def __init__(self, path: str, initialized_from_inside_class=False):
        super().__init__(path, initialized_from_inside_class)
        self.content = None


    @classmethod
    def get(cls, path: str):
        workspace = Workspace(path, initialized_from_inside_class=True)
        workspace.load()
        return workspace

    @authz_integration(authz_action='delete', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.delete')
    def delete(self):
        remove(self.absolute_filesystem_path)


DirectoryContent.register_child_class(Workspace)

