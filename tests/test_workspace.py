import json
import shutil
from pathlib import Path
import time
import os
from pathlib import Path
from rest.test import TransactionTestCase
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.directory_content import DirectoryContent

from dtcd_workspaces.workspaces.utils import encode_name


class TestWorkspace(TransactionTestCase):
    test_meta_info = {
        'some_meta': {
            'some_meta': 34,
        },
        'another_info': 'test'
    }
    test_content = {
        "id": "29b1aa3f-a5f4-4dd4-9904-cf1b2890791d",
        "title": "Test_flow",
        "column": "12",
        "editMode": True,
        "plugins": [
            {
                "guid": "LogSystem_0_7_0",
                "meta": {
                    "type": "core",
                    "title": "Система логирования",
                    "name": "LogSystem",
                    "version": "0.7.0",
                    "withDependencies": False,
                    "priority": 7
                },
                "config": None,
            },
        ]
    }

    def setUp(self):
        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def _create_workspace(self, path: str, meta_info: dict = None, content: dict = None):
        if meta_info is None:
            meta_info = self.test_meta_info
        if content is None:
            content = self.test_content

        workspace = Workspace(path)
        workspace.meta = meta_info
        workspace.content = content
        workspace.save()
        return workspace

    def test_create_workspace(self):
        test_directory_name = 'test'
        test_dir = Directory(test_directory_name).save()
        test_workspace_name = 'test'
        encoded_directory_name = encode_name(test_directory_name)
        encoded_worspace_name = encode_name(test_workspace_name)
        workspace = self._create_workspace(str(Path(test_directory_name) / test_workspace_name))

        self.assertEqual(
            workspace.absolute_filesystem_path,
            Path(WORKSPACE_BASE_PATH) / encoded_directory_name / encoded_worspace_name
        )
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name).exists())
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name / encoded_worspace_name).exists())
        workspace = Workspace.get(str(Path(test_directory_name) / test_workspace_name))
        self.assertDictEqual(self.test_meta_info, workspace.meta)
        self.assertDictEqual(self.test_content, workspace.content)

    def test_create_workspace_in_root(self):
        workspace_name = 'workspace_in_root'
        workspace = self._create_workspace(workspace_name)
        workspace = Workspace.get(workspace_name)
        self.assertDictEqual(self.test_content, workspace.content)

    def test_move_workspace(self):
        dir1 = Directory('path1')
        dir1.save()
        dir2 = Directory('path1/path2')
        dir2.save()

        dir3 = Directory('path3')
        dir3.save()
        test_meta = {
            'name': 'moving workspace'
        }
        workspace = self._create_workspace('path1/path2/workspace_test', meta_info=test_meta)
        workspace.save()
        workspace.move('path3/workspace_test3')

        workspace = Workspace.get('path3/workspace_test3')

        self.assertDictEqual(workspace.meta, test_meta)

    def test_rename_workspcace(self):
        workspace = Workspace('test')
        content = {
            'name': 'test_rename'
        }
        workspace.content = content
        workspace.save()

        workspace.move('new_name_test')
        workspace = Workspace.get('new_name_test')
        self.assertDictEqual(workspace.content, content)

