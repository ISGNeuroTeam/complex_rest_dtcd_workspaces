from collections import defaultdict
from pathlib import Path
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH
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

    def __init__(self, path: str):
        super().__init__(path)
        self.content = None


    @classmethod
    def get(cls, path: str):
        workspace = Workspace(path)
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
        self._load_tabs()

    def _load_tabs(self):
        if self.content is None or 'tabPanelsConfig' not in self.content:
            return
        self.content['tabPanelsConfig']['tabsOptions'] = []
        tabs_list:list = self.content['tabPanelsConfig']['tabsOptions']
        # iterdir workspace dir and update or delete tabs
        for tab_abs_path in self.absolute_filesystem_path.iterdir():
            tab_filesystem_rel_path = str(tab_abs_path.relative_to(WORKSPACE_BASE_PATH))
            tab_filesystem_rel_path = tab_filesystem_rel_path.rstrip('_tab')
            try:
                tab_path = self.get_relative_humanreadable_path(tab_filesystem_rel_path)
            except DirectoryContentException: # skip not encoded strings
                continue
            if WorkspaceTab.is_path_for_cls(str(tab_path)):
                tab:WorkspaceTab = WorkspaceTab.get(str(tab_path))
                tabs_list.append({
                    'id': tab.id,
                    'isActive': tab.isActive,
                    'editName': tab.editName,
                    'name': tab.name,
                    'permissions': tab.permissions,
                    'order': tab.order,
                    'meta': tab.meta
                })
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
        self._save_tabs()

    def _save_tabs(self):
        # go through options and create tab dict
        tabs_dict = {}
        if self.content is None or  'tabPanelsConfig' not in self.content:
            return

        for tab_info in self.content['tabPanelsConfig']['tabsOptions']:
            tabs_dict[tab_info['id']] = tab_info

        # iterdir workspace dir and update or delete tabs
        for tab_abs_path in self.absolute_filesystem_path.iterdir():
            tab_filesystem_rel_path = str(tab_abs_path.relative_to(WORKSPACE_BASE_PATH))
            tab_filesystem_rel_path = tab_filesystem_rel_path.rstrip('_tab')
            try:
                tab_path = self.get_relative_humanreadable_path(tab_filesystem_rel_path)
            except DirectoryContentException: # skip not encoded strings
                continue
            if WorkspaceTab.is_path_for_cls(str(tab_path)):
                tab = WorkspaceTab.get(str(tab_path))
                if tab.id not in tabs_dict:
                    tab.delete()
                else:  # update
                    tab_info = tabs_dict.pop(tab.id)
                    for tab_attr in ('isActive', 'editName', 'name', 'id', 'order'):
                        setattr(tab, tab_attr, tab_info.get(tab_attr, None))
                    setattr(tab, 'meta', tab_info.get('meta', {}))
                    tab.save()

        tabs_order_counter = 0
        # create tabs that don't exist
        for tab_id, tab_info in tabs_dict.items():
            tabs_order_counter = tabs_order_counter + 1            
            tab_path = f'{self.path}/{tab_id}'
            tab = WorkspaceTab.create(
                tab_path,
                id=tab_info.get('id', None),
                isActive=tab_info.get('isActive', None),
                editName=tab_info.get('editName', None),
                name=tab_info.get('name', None),
                order=tab_info.get('order', tabs_order_counter),
                meta=tab_info.get('meta', dict())
            )
        self.content['tabPanelsConfig']['tabsOptions'] = []


DirectoryContent.register_child_class(Workspace)

