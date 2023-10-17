from collections import defaultdict
from rest_auth.authorization import auth_covered_method, authz_integration

from .utils import remove
from .directory_base_object import DirectoryBaseObject
from .directory_content import DirectoryContent
from .directorycontent_exception import DirectoryContentException
from .workspace_tab import WorkspaceTab

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

    def load(self):
        """
        Load attributes from meta filename
        """
        if not self.absolute_filesystem_path.exists():
            raise DirectoryContentException(
                DirectoryContentException.DOES_NOT_EXIST, str(self.absolute_filesystem_path)
            )
        self._read_attributes_from_json_file(self.absolute_content_file_path)
        # traverse through tabs and make content attribute
        for p in self.absolute_filesystem_path.iterdir():
            if WorkspaceTab.is_path_for_cls(str(p)):
                # todo catch access denie exception
                workspace_tab = WorkspaceTab.get(str(p))
                if 'plugins' in self.content:
                    self.content['plugins'].extend(workspace_tab.plugins)

    @authz_integration(authz_action='update', id_attr='id')
    @auth_covered_method(action_name='dtcd_workspaces.update')
    def save(self):
        parent_dir_path = self.absolute_filesystem_path.parent
        if not parent_dir_path.exists():
            raise DirectoryContentException(DirectoryContentException.NO_DIR, str(parent_dir_path))
        self.absolute_filesystem_path.mkdir(exist_ok=True)
        # parse content and create tabs objects
        tabs_plugins = defaultdict(list)
        if 'plugins' in self.content:
            for plugin in self.content['plugins']:
                if 'position' in plugin and plugin['position'] is not None:
                    tabs_plugins[plugin['position']['tabId']].append(plugin)
        for tab_info in self.content['tabPanelsConfig']['tabsOptions']:
            # todo make update or create
            tab = WorkspaceTab.create(
                self.path + '/' + tab_info['id'],
                id = tab_info['id'],
                isActive=tab_info['isActive'],
                editName=tab_info['editName'],
                tabPanel=tab_info['tabPanel'],
                plugins=tabs_plugins
            )
        self._write_attributes_to_json_file(self.absolute_content_file_path)

DirectoryContent.register_child_class(Workspace)

