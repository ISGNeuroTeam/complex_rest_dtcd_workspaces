import time
from pathlib import Path
import os
from shutil import rmtree, copytree
from rest.test import TransactionTestCase
from dtcd_workspaces.workspaces.utils import FilesystemWorkspaceManager
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException


class TestWorkspaceDir(TransactionTestCase):

    def setUp(self) -> None:
        tests_path = Path(__file__).parent
        rmtree(tests_path / 'tmp', ignore_errors=True)
        rmtree(tests_path / 'workspaces', ignore_errors=True)
        copytree(tests_path / 'workspaces.example', tests_path / 'workspaces')
        os.mkdir(tests_path / 'tmp')
        self.fsw_manager = FilesystemWorkspaceManager(str(tests_path / 'workspaces'), str(tests_path / 'tmp'))

    def test_workspace_path_not_specified(self):
        dirs = self.fsw_manager.list_directories()
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, {"parent1", "parent2"})

    def test_workspace_path_empty(self):
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, {"parent1", "parent2"})

    def test_workspace_path_working(self):
        dirs = self.fsw_manager.list_directories(workspace_path='parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, {"child1", "child2"})
        dirs = self.fsw_manager.list_directories(workspace_path='parent1/child1')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, set())

    def test_workspace_multiple_slashes1(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='/')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_multiple_slashes2(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='//')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_multiple_slashes3(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='///')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_dots_with_slashes(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='/../')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_dots(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='..')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_left_slash_dots(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='/..')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_right_slash_dots(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='../')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'multiple slashes exception not thrown')

    def test_workspace_invalid_path_short(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='qwerty')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'invalid path exception not thrown')

    def test_workspace_invalid_path_long(self):
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='qwerty/booby/trap')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'invalid path exception not thrown')

    def test_all_dirs(self):
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, {"parent1", "parent2"})
        dirs = self.fsw_manager.list_directories(workspace_path='parent2')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, {"child1", "child2"})
        dirs = self.fsw_manager.list_directories(workspace_path='parent2/child2')
        dir_names = {d['name'] for d in dirs}
        self.assertEqual(dir_names, set())

    def test_one_dir(self):
        dir = self.fsw_manager.read_dir('parent1', workspace_path='')  # useless?
        self.assertEqual(dir['name'], 'parent1')
        dir = self.fsw_manager.read_dir('child2', workspace_path='parent2')  # useless?
        self.assertEqual(dir['name'], 'child2')

    def test_dir_that_doesnt_exist_root(self):
        try:
            dir = self.fsw_manager.read_dir('root', workspace_path='')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'doesn\'t exist exception not raised')

    def test_dir_that_doesnt_exist_lvl1(self):
        try:
            dir = self.fsw_manager.read_dir('root', workspace_path='parent2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'doesn\'t exist exception not raised')

    def test_dir_that_doesnt_exist_lvl2(self):
        try:
            dir = self.fsw_manager.read_dir('root', workspace_path='parent2/child2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'doesn\'t exist exception not raised')

    def test_dir_that_empty_root(self):
        try:
            dir = self.fsw_manager.read_dir('', workspace_path='')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'empty exception not raised')

    def test_dir_that_empty_lvl1(self):
        try:
            dir = self.fsw_manager.read_dir('', workspace_path='parent2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'empty exception not raised')

    def test_dir_that_empty_lvl2(self):
        try:
            dir = self.fsw_manager.read_dir('', workspace_path='parent2/child2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'empty exception not raised')

    def test_dir_with_slashes_root(self):
        try:
            dir = self.fsw_manager.read_dir('booby/trap', workspace_path='')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'name with slashes exception not raised')

    def test_dir_with_slashes_lvl1(self):
        try:
            dir = self.fsw_manager.read_dir('boobytrap/', workspace_path='parent2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'name with slashes exception not raised')

    def test_dir_with_slashes_lvl2(self):
        try:
            dir = self.fsw_manager.read_dir('/boobytrap/', workspace_path='parent2/child2')  # useless?
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False, 'name with slashes exception not raised')

    def test_post_dir_root(self):
        self.fsw_manager.create_dir({'name': 'mom'}, workspace_path='')
        dirs = self.fsw_manager.list_directories()
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('mom' in dir_names)

    def test_post_dir(self):
        self.fsw_manager.create_dir({'name': 'dad'}, workspace_path='parent2/child2')
        dirs = self.fsw_manager.list_directories(workspace_path='parent2/child2')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('dad' in dir_names)

    def test_post_dir_with_rubbish(self):
        self.fsw_manager.create_dir({'name': 'granny', 'age': 18}, workspace_path='')
        dirs = self.fsw_manager.list_directories()
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('granny' in dir_names)

    def test_post_dir_with_no_name(self):
        try:
            self.fsw_manager.create_dir({'age': 18}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_post_dir_empty_name(self):
        try:
            self.fsw_manager.create_dir({'name': ''}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_post_dir_name_with_slashes(self):
        try:
            self.fsw_manager.create_dir({'name': 'booby/trap'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    # def test_post_dir_wrong_type(self):
    #     self.fsw_manager.write_dir([{'name': 'bro'}], workspace_path='')

    # def test_post_dir_name_not_str(self):
    #     self.fsw_manager.write_dir({'name': 18}, workspace_path='')

    def test_delete_dir_root(self):
        self.fsw_manager.remove_dir('parent1', workspace_path='')
        dirs = self.fsw_manager.list_directories()
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' not in dir_names)
        try:
            dirs = self.fsw_manager.list_directories(workspace_path='parent1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_delete_dir(self):
        self.fsw_manager.remove_dir('child2', workspace_path='parent1')
        dirs = self.fsw_manager.list_directories(workspace_path='parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('child2' not in dir_names)

    def test_delete_dir_empty_name(self):
        try:
            self.fsw_manager.remove_dir('', workspace_path='parent1/child1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_delete_dir_name_with_slashes(self):
        try:
            self.fsw_manager.remove_dir('booby/trap', workspace_path='parent1/child1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_delete_not_existing_dir(self):
        try:
            self.fsw_manager.remove_dir('booby', workspace_path='parent1/child1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_change_name_root(self):
        self.fsw_manager.update_dir({'old_name': 'parent1', 'new_name': 'mama'}, workspace_path='')
        self.fsw_manager.update_dir({'old_name': 'parent2', 'new_name': 'papa'}, workspace_path='')
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('mama' in dir_names)
        self.assertTrue('papa' in dir_names)
        self.assertTrue('parent1' not in dir_names)
        self.assertTrue('parent2' not in dir_names)

    def test_change_name(self):
        self.fsw_manager.update_dir({'old_name': 'child1', 'new_name': 'julia'}, workspace_path='parent1')
        self.fsw_manager.update_dir({'old_name': 'child2', 'new_name': 'monty'}, workspace_path='parent2')
        dirs = self.fsw_manager.list_directories(workspace_path='parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('julia' in dir_names)
        self.assertTrue('monty' not in dir_names)
        self.assertTrue('child1' not in dir_names)
        self.assertTrue('child2' in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent2')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('julia' not in dir_names)
        self.assertTrue('monty' in dir_names)
        self.assertTrue('child1' in dir_names)
        self.assertTrue('child2' not in dir_names)

    def test_no_old_name(self):
        try:
            self.fsw_manager.update_dir({'new_name': 'julia'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_empty_old_name(self):
        try:
            self.fsw_manager.update_dir({'old_name': '', 'new_name': 'julia'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_no_new_name(self):
        try:
            self.fsw_manager.update_dir({'old_name': 'parent1'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_empty_new_name(self):
        try:
            self.fsw_manager.update_dir({'old_name': 'parent1', 'new_name': ''}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_move_dir_down(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        self.fsw_manager.update_dir({'old_name': 'parent1', 'new_path': 'parent2'}, workspace_path='')
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' not in dir_names)
        self.assertTrue('parent2' in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent2')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent2/parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('child1' in dir_names)
        self.assertTrue('child2' in dir_names)

    def test_move_dir_up_and_empty_path_is_a_root(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        self.fsw_manager.update_dir({'old_name': 'child1', 'new_path': ''}, workspace_path='parent1')
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' in dir_names)
        self.assertTrue('parent2' in dir_names)
        self.assertTrue('child1' in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('child2' in dir_names)
        self.assertTrue('child1' not in dir_names)

    def test_invalid_new_path(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        try:
            self.fsw_manager.update_dir({'old_name': 'child1', 'new_path': 'parent2/booby/trap'}, workspace_path='parent1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_new_path_equal_old_path(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        try:
            self.fsw_manager.update_dir({'old_name': 'child1', 'new_path': 'parent1'}, workspace_path='parent1')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_move_inside_itself(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        try:
            self.fsw_manager.update_dir({'old_name': 'parent1', 'new_path': 'parent1/child1'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_move_and_rename(self):
        # will be implemented with role model TODO
        self.assertTrue(True)
        return
        # should only move
        self.fsw_manager.update_dir({'old_name': 'parent1', 'new_path': 'parent2', 'new_name': 'parent3'}, workspace_path='')
        dirs = self.fsw_manager.list_directories(workspace_path='')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' not in dir_names)
        self.assertTrue('parent2' in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent2')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('parent1' in dir_names)
        self.assertTrue('parent3' not in dir_names)
        dirs = self.fsw_manager.list_directories(workspace_path='parent2/parent1')
        dir_names = {d['name'] for d in dirs}
        self.assertTrue('child1' in dir_names)
        self.assertTrue('child2' in dir_names)

    def test_reserved_meta_file_name(self):
        try:
            self.fsw_manager.create_dir({"name": self.fsw_manager.dir_metafile_name}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def new_dirname_eq_old_dirname(self):
        try:
            self.fsw_manager.update_dir({'old_name': 'parent1', 'new_name': 'parent1'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_dir_exists(self):
        try:
            self.fsw_manager.create_dir({"name": 'parent2'}, workspace_path='')
        except WorkspaceManagerException as e:
            self.assertTrue(True)
            return
        self.assertTrue(False)

    def test_ctime(self):
        self.fsw_manager.create_dir({"name": 'parent3'}, workspace_path='')
        d = self.fsw_manager.read_dir('parent3')
        self.assertEqual(d["creation_time"], d["modification_time"])

    def test_mtime(self):
        self.fsw_manager.create_dir({"name": 'parent3'}, workspace_path='')
        time.sleep(1)
        self.fsw_manager.update_dir({'old_name': 'parent3', 'new_name': 'parent4'}, workspace_path='')
        d = self.fsw_manager.read_dir('parent4')
        self.assertNotEqual(d["creation_time"], d["modification_time"])
        self.fsw_manager.create_workspace({"title": "test", "content": "/parent4/"}, workspace_path='parent4')
        d = self.fsw_manager.read_dir('parent4')
        self.assertNotEqual(d["creation_time"], d["modification_time"])

    def tearDown(self) -> None:
        pass
