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


class TestDirs(TransactionTestCase):
    def setUp(self):
        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def _create_test_directory(self, directory_path: str, dir_meta: dict = None):
        paths_parts = directory_path.split('/')
        cur_path = paths_parts.pop(0)

        for path_part in paths_parts:
            directory = Directory(cur_path)
            directory.meta = {
                'some_meta': {
                    'path': cur_path
                }
            }
            directory.save()
            cur_path = cur_path + '/' + path_part

        directory = Directory(cur_path)
        directory.meta = dir_meta
        directory.save()

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

    def test_move_directory(self):
        meta_info = {
            'some_meta': {
                'some_meta': 34,
            },
            'info': 'test_moving'
        }
        self._create_test_directory('path1/path2/path3', meta_info)
        self._create_test_directory('path3/path4')
        directory = Directory.get('path1/path2/path3')
        directory.move('path3/path4/path234')

        directory = Directory.get('path3/path4/path234')
        self.assertDictEqual(directory.meta, meta_info)

    def test_list(self):
        parent_dir = Directory('path1')
        parent_dir.save()
        child_dir1 = Directory('path1/c_path1')
        child_dir1.save()
        child_dir2 = Directory('path1/c_path2')
        child_dir2.save()
        workspace = Workspace('path1/workspace1')
        workspace.save()
        workspace2 = Workspace('path1/workspace2')
        workspace2.save()
        dir_contents = parent_dir.list()
        self.assertEqual(len(dir_contents), 4)
        dirs = list(filter(
            lambda x: isinstance(x, Directory),
            dir_contents
        ))
        workspaces = list(filter(
            lambda x: isinstance(x, Workspace),
            dir_contents
        ))
        self.assertEqual(len(dirs), 2)
        self.assertEqual(len(workspaces), 2)

