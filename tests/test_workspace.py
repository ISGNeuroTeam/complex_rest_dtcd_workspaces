import json
import shutil
from pathlib import Path
import time
import os
from pathlib import Path
from rest.test import TransactionTestCase
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.filesystem_workspaces import DirectoryContentException
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.utils import encode_name


class TestWorkspace(TransactionTestCase):
    def setUp(self):
        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def test_create_workspace(self):
        test_directory_name = 'test'
        test_dir = Directory(test_directory_name).save()
        test_workspace_name = 'test'
        encoded_directory_name = encode_name(test_directory_name)
        encoded_worspace_name = encode_name(test_workspace_name)
        workspace = Workspace(str(Path(test_directory_name) / test_workspace_name))
        meta_info = {
            'some_meta': {
                'some_meta': 34,
            },
            'another_info': 'test'
        }
        content = {
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
        workspace.meta = meta_info
        workspace.content = content
        workspace.save()
        self.assertEqual(
            workspace.absolute_filesystem_path,
            Path(WORKSPACE_BASE_PATH) / encoded_directory_name / encoded_worspace_name
        )
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name).exists())
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name / encoded_worspace_name).exists())
        workspace = Workspace.get(str(Path(test_directory_name) / test_workspace_name))
        self.assertDictEqual(meta_info, workspace.meta)
        self.assertDictEqual(content, workspace.content)
