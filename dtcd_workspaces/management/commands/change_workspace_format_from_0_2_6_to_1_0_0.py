import json
import os
import traceback
import shutil

from pathlib import Path
from django.core.management.base import BaseCommand, CommandError

from core.globals import global_vars
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.directory_content import DirectoryContent
from dtcd_workspaces.workspaces.utils import encode_name, remove



class Command(BaseCommand):
    help = 'Update workspace and directory format'

    def add_arguments(self, parser):
        parser.add_argument(
            'old_format_workspace_dir',
            help='Directory with workspaces, old format'
        )

    def _get_new_path(self, old_format_filesystem_path: Path, name: str):
        # for all directories get title and encode it
        new_paths_dir_names = []
        old_dir_names = str(old_format_filesystem_path.parent.relative_to(self.old_format_base_path)).split(os.sep)
        if len(old_dir_names)==1 and old_dir_names[0] == '.':
            new_path = name
        else:
            for i in range(len(old_dir_names)):
                with open(self.old_format_base_path / os.sep.join(old_dir_names[0:i+1]) / DIR_META_NAME) as f:
                    dir_dct = json.load(f)
                    dir_name = dir_dct['title']
                    new_paths_dir_names.append(dir_name)
            new_path = os.sep.join(new_paths_dir_names) + os.sep + name
        return new_path

    def change_directory_format(self, old_format_dir_path: Path):

        self.stdout.write(self.style.WARNING(f'Handle path {old_format_dir_path}'))
        if old_format_dir_path!=self.old_format_base_path:
            try:
                with open(old_format_dir_path / DIR_META_NAME, 'r') as f:
                    directory_dict = json.load(f)
                    title = directory_dict.get('title', '')
                    dir_keys = set(directory_dict.keys())
                    for key in dir_keys:
                        if key not in Directory.saved_to_file_attributes:
                            del directory_dict[key]
                for attr in Directory.saved_to_file_attributes:
                    if attr not in dir_keys:
                        directory_dict[attr] = None

                dir_path = self._get_new_path(old_format_dir_path, title)
                self.stdout.write(self.style.WARNING(f'Create directory path={dir_path}'))
                Directory.create(
                    str(dir_path),
                    **directory_dict
                )

            except Exception as err:
                self.stdout.write(self.style.ERROR(f'Error occured while change format for {old_format_dir_path}'))
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        for child_item in old_format_dir_path.iterdir():
            if child_item.is_dir() and (child_item / DIR_META_NAME).exists():
                self.change_directory_format(child_item)
            else:
                if child_item.name.endswith('.json'):
                    self.change_workspace_format(child_item)

    def change_workspace_format(self, old_format_workspace_path: Path):
        self.stdout.write(self.style.WARNING(f'Handle path {old_format_workspace_path}'))
        try:
            with open(old_format_workspace_path) as f:
                workspace_dict = json.load(f)
                title = workspace_dict['title']
                w_keys = set(workspace_dict.keys())
                for key in w_keys:
                    if key not in Workspace.saved_to_file_attributes:
                        del workspace_dict[key]
                for attr in Workspace.saved_to_file_attributes:
                    if attr not in w_keys:
                        workspace_dict[attr] = None
                new_workspace_path = self._get_new_path(old_format_workspace_path, title)
                self.stdout.write(self.style.WARNING(f'Create workspace path={new_workspace_path}'))
                workspace = Workspace.create(
                    str(new_workspace_path),
                    **workspace_dict
                )

        except Exception as err:
            self.stdout.write(self.style.ERROR(f'Invalid workspace format {old_format_workspace_path}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def handle(self, *args, **options):
        global_vars['disable_authorization'] = True
        self.old_format_base_path = Path(options['old_format_workspace_dir'])
        self.base_path = Path(WORKSPACE_BASE_PATH)
        # copy root DIR_INFO
        shutil.copy(self.old_format_base_path / DIR_META_NAME, Path(WORKSPACE_BASE_PATH) / DIR_META_NAME)
        self.change_directory_format(self.old_format_base_path)
        self.stdout.write(self.style.SUCCESS('Successfully changed format'))

