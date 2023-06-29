import json
import traceback

from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.utils import encode_name, remove

WORKSPACE_BASE_PATH = Path(WORKSPACE_BASE_PATH)


class Command(BaseCommand):
    help = 'Update workspace and directory format'

    def change_directory_format(self, dir_path: Path):
        try:
            with open(dir_path / DIR_META_NAME) as f:
                directory = json.load(f)
                dir_keys = set(directory.keys())
                for key in dir_keys:
                    if key not in Directory.saved_to_file_attributes:
                        del directory[key]
            for attr in Directory.saved_to_file_attributes:
                if attr not in dir_keys:
                    directory[attr] = None

            with open(dir_path / DIR_META_NAME, 'w') as f:
                json.dump(directory, f)

        except Exception as err:
            self.stdout.write(self.style.ERROR(f'Error occured while change format for {dir_path}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

        for child_item in dir_path.iterdir():
            if child_item.is_dir():
                self.change_directory_format(child_item)
            else:
                if child_item.name.endswith('.json'):
                    self.change_workspace_format(child_item)

    def change_workspace_format(self, workspace_path: Path):
        # rename workspace with title, remove id
        try:
            with open(workspace_path) as f:
                workspace = json.load(f)
                title = workspace['title']
                w_keys = set(workspace.keys())
                for key in w_keys:
                    if key not in Workspace.saved_to_file_attributes:
                        del workspace[key]
                for attr in Workspace.saved_to_file_attributes:
                    if attr not in w_keys:
                        workspace[attr] = None
                new_workspace_path = workspace_path.parent / encode_name(title)
                with open(new_workspace_path, 'w') as f_out:
                    json.dump(workspace, f_out)
                    remove(workspace_path)

        except Exception as err:
            self.stdout.write(self.style.ERROR(f'Invalid workspace format {workspace_path}'))
            self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def handle(self, *args, **options):

        base_path = Path(WORKSPACE_BASE_PATH)
        self.change_directory_format(base_path)

        self.stdout.write(self.style.SUCCESS('Successfully changed format'))

