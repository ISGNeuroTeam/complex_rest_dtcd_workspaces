import json
import shutil
from pathlib import Path
import time
import os
from pathlib import Path
from rest.test import TransactionTestCase
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.filesystem_workspaces import WorkspaceManagerException
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.utils import encode_name


class TestDirs(TransactionTestCase):
    def setUp(self):
        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def test_create_directory(self):
        test_directory_name = 'test'
        encoded_directory_name = encode_name(test_directory_name)
        directory = Directory(test_directory_name)
        meta_info = {
            'some_meta': {
                'some_meta': 34,
            },
            'another_info': 'test'
        }
        directory.meta = meta_info
        directory.save()
        self.assertEqual(directory.absolute_filesystem_path, Path(WORKSPACE_BASE_PATH) / encoded_directory_name)
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name).exists())
        self.assertTrue((Path(WORKSPACE_BASE_PATH) / encoded_directory_name / DIR_META_NAME).exists())
        directory = Directory.get(test_directory_name)
        self.assertDictEqual(meta_info, directory.meta)


