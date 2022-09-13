import json
from pathlib import Path
import time
import os
from shutil import rmtree
from rest.test import TransactionTestCase
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from dtcd_workspaces.workspaces import utils
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.management.commands.create_root_records import Command
from rest_auth.models import User, Plugin, Action
from settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME


class TestWorkspaceDirs(TransactionTestCase):
    tmp_path = Path(WORKSPACE_TMP_PATH)
    base_path = Path(WORKSPACE_BASE_PATH)
    meta_name = DIR_META_NAME

    def _create_root_dir_object(self):
        self.root_dir = Directory(path='')

    def _create_necessary_db_records(self):
        self._create_action_records()
        Command().handle()

    def _create_necessary_fs_objects(self):
        if not self.tmp_path.exists():
            os.mkdir(self.tmp_path)
        if not self.base_path.exists():
            os.mkdir(self.base_path)
            with open(self.base_path / self.meta_name, 'w') as fw:
                fw.write('{"id": ""}')

    def _create_action_records(self):
        Action(name='workspace.create', plugin=self.plugin).save()
        Action(name='workspace.read', plugin=self.plugin).save()
        Action(name='workspace.update', plugin=self.plugin).save()
        Action(name='workspace.delete', plugin=self.plugin).save()

    def setUp(self) -> None:
        self.admin = User.objects.create_superuser('admin', '', 'admin')
        self.admin.save()
        self.plugin = Plugin(name='dtcd_workspaces')
        self.plugin.save()
        self._create_necessary_db_records()
        self._create_necessary_fs_objects()
        self._create_root_dir_object()

    def test_create_workspace_in_root(self):
        title = 'root_ws'
        content = 'root_ws_content'
        ws = Workspace(path='', _conf={
            "title": title,
            "content": content})
        ws.create()
        directory_contents = [p.stem for p in self.base_path.glob('*.json')]

        self.assertEqual(len(directory_contents), 1)  # only one ws in root dir
        self.assertTrue(ws.id in directory_contents)
        with open((self.base_path / ws.id).with_suffix('.json')) as fr:
            ws = json.load(fr)
        self.assertEqual(title, ws.get('title'))
        self.assertEqual(content, ws.get('content'))

    def test_create_dir_in_root(self):
        title = "in_root_dir"
        dr = Directory(path='', _conf={"title": title})
        dr.create()
        directory_contents = [p for p in self.base_path.glob('*') if p.is_dir()]

        self.assertEqual(len(directory_contents), 1)  # only one dir in root dir
        self.assertEqual(utils._encode_name(title), directory_contents[0].name)  # fs dir name was encoded right
        with open(directory_contents[0] / self.meta_name) as fr:
            dr = json.load(fr)
        self.assertEqual(title, dr.get('title'))

    def test_create_workspace(self):
        dir_title = "in_root_dir"
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        title = 'dir_ws'
        content = 'dir_ws_content'
        ws = Workspace(path=utils._encode_name(dir_title), _conf={
            "title": title,
            "content": content})
        ws.create()
        directory_contents = [p.stem for p in dr.filesystem_path.glob('*.json')]
        self.assertEqual(len(directory_contents), 1)  # only one ws in root dir
        self.assertTrue(ws.id in directory_contents)
        with open((dr.filesystem_path / ws.id).with_suffix('.json')) as fr:
            ws = json.load(fr)
        self.assertEqual(title, ws.get('title'))
        self.assertEqual(content, ws.get('content'))

    def test_create_dir(self):
        parent_title = "in_root_dir"
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        title = "dir_inside_another_dir"
        dr = Directory(path=utils._encode_name(parent_title), _conf={"title": title})
        dr.create()
        directory_contents = [p for p in parent_dr.filesystem_path.glob('*') if p.is_dir()]
        self.assertEqual(len(directory_contents), 1)  # only one dir in root dir
        self.assertEqual(utils._encode_name(title), directory_contents[0].name)  # fs dir name was encoded right
        with open(directory_contents[0] / self.meta_name) as fr:
            dr = json.load(fr)
        self.assertEqual(title, dr.get('title'))

    def test_list_dir_in_root(self):
        dtitle0 = "catalogue0"
        dr0 = Directory(path='', _conf={"title": dtitle0})
        dr0.create()
        dtitle1 = "catalogue1"
        dr1 = Directory(path='', _conf={"title": dtitle1})
        dr1.create()
        ws0 = Workspace(path='', _conf={
            "title": "ws0",
            "content": "content0"})
        ws0.create()
        ws1 = Workspace(path='', _conf={
            "title": "ws1",
            "content": "content1"})
        ws1.create()

        listing = self.root_dir.list()
        self.assertEqual(len(listing['workspaces'] + listing['directories']), 4)
        listing['workspaces'].sort(key=lambda x: x['title'])
        listing['directories'].sort(key=lambda x: x['title'])
        ws_ids = [ws0.id, ws1.id]
        for i in range(len(listing['workspaces'])):
            self.assertEqual(ws_ids[i], listing['workspaces'][i]['id'])
            self.assertEqual('', listing['workspaces'][i]['path'])
            self.assertEqual(f'ws{i}', listing['workspaces'][i]['title'])
            self.assertEqual(None, listing['workspaces'][i]['content'])
            self.assertEqual(False, listing['workspaces'][i]['is_dir'])
        for i in range(len(listing['directories'])):
            self.assertEqual(f'catalogue{i}', listing['directories'][i]['path'])
            self.assertEqual(f'catalogue{i}', listing['directories'][i]['title'])
            self.assertEqual(True, listing['directories'][i]['is_dir'])
        self.assertEqual('', listing['current_directory']['id'])
        self.assertEqual('', listing['current_directory']['path'])
        self.assertEqual(True, listing['current_directory']['is_dir'])

    def test_list_dir(self):
        parent_title = 'in_root_dir'
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        dtitle0 = "catalogue0"
        dr0 = Directory(path=utils._encode_name(parent_title), _conf={"title": dtitle0})
        dr0.create()
        dtitle1 = "catalogue1"
        dr1 = Directory(path=utils._encode_name(parent_title), _conf={"title": dtitle1})
        dr1.create()
        ws0 = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": "ws0",
            "content": "content0"})
        ws0.create()
        ws1 = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": "ws1",
            "content": "content1"})
        ws1.create()

        listing = parent_dr.list()
        self.assertEqual(len(listing['workspaces'] + listing['directories']), 4)
        listing['workspaces'].sort(key=lambda x: x['title'])
        listing['directories'].sort(key=lambda x: x['title'])
        ws_ids = [ws0.id, ws1.id]
        for i in range(len(listing['workspaces'])):
            self.assertEqual(ws_ids[i], listing['workspaces'][i]['id'])
            self.assertEqual(parent_title, listing['workspaces'][i]['path'])
            self.assertEqual(f'ws{i}', listing['workspaces'][i]['title'])
            self.assertEqual(None, listing['workspaces'][i]['content'])
            self.assertEqual(False, listing['workspaces'][i]['is_dir'])
        for i in range(len(listing['directories'])):
            self.assertEqual(f'{parent_title}/catalogue{i}', listing['directories'][i]['path'])
            self.assertEqual(f'catalogue{i}', listing['directories'][i]['title'])
            self.assertEqual(True, listing['directories'][i]['is_dir'])
        self.assertEqual(parent_title, listing['current_directory']['path'])
        self.assertEqual(True, listing['current_directory']['is_dir'])

    def test_get_workspace_in_root(self):
        title = 'root_ws'
        content = 'root_ws_content'
        ws = Workspace(path='', _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual('', data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_get_directory_in_root(self):
        title = "in_root_dir"
        dr = Directory(path='', _conf={"title": title})
        dr.create()
        data = dr.read()
        self.assertEqual(title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])

    def test_get_workspace(self):
        parent_title = 'in_root_dir'
        dr = Directory(path='', _conf={"title": parent_title})
        dr.create()
        title = 'dir_ws'
        content = 'dir_ws_content'
        ws = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(parent_title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_get_directory(self):
        parent_title = "in_root_dir"
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        title = "dir_inside_another_dir"
        dr = Directory(path=utils._encode_name(parent_title), _conf={"title": title})
        dr.create()
        data = dr.read()
        self.assertEqual(f"{parent_title}/{title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])

    def test_update_workspace_title_in_root(self):
        title = 'root_ws'
        new_title = 'sw_toor'
        content = 'root_ws_content'
        ws = Workspace(path='', _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"title": new_title})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual('', data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_workspace_content_in_root(self):
        title = 'root_ws'
        content = 'root_ws_content'
        new_content = 'tnetnoc_sw_toor'
        ws = Workspace(path='', _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"content": new_content})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual('', data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(new_content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_workspace_in_root(self):
        title = 'root_ws'
        new_title = 'sw_toor'
        content = 'root_ws_content'
        new_content = 'tnetnoc_sw_toor'
        ws = Workspace(path='', _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"title": new_title, "content": new_content})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual('', data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(new_content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_workspace_title(self):
        title = 'dir_ws'
        new_title = 'sw_rid'
        content = 'dir_ws_content'
        parent_title = "in_root_dir"
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        ws = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"title": new_title})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(parent_title, data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_workspace_content(self):
        title = 'dir_ws'
        content = 'dir_ws_content'
        new_content = 'tnetnoc_sw_rid'
        parent_title = 'in_root_dir'
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        ws = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"content": new_content})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(parent_title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(new_content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_workspace(self):
        title = 'dir_ws'
        new_title = 'sw_rid'
        content = 'dir_ws_content'
        new_content = 'tnetnoc_sw_rid'
        parent_title = 'in_root_dir'
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        ws = Workspace(path=utils._encode_name(parent_title), _conf={
            "title": title,
            "content": content})
        ws.create()
        data = ws.read()
        self.assertAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        time.sleep(1)
        ws.update(_conf={"title": new_title, "content": new_content})
        data = ws.read()
        self.assertNotAlmostEqual(data['creation_time'], data['modification_time'], delta=1)
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(parent_title, data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(new_content, data['content'])
        self.assertEqual(False, data['is_dir'])

    def test_update_directory_in_root(self):
        title = 'in_root_dir'
        new_title = 'rid_toor_ni'
        dr = Directory(path='', _conf={"title": title})
        dr.create()
        dr.update(_conf={"new_title": new_title})
        data = dr.read()
        self.assertEqual(new_title, data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(True, data['is_dir'])

    def test_update_directory(self):
        title = "dir_inside_another_dir"
        new_title = 'rid_rethona_edisni_rid'
        parent_title = 'in_root_dir'
        parent_dr = Directory(path='', _conf={"title": parent_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(parent_title), _conf={"title": title})
        dr.create()
        dr.update(_conf={"new_title": new_title})
        data = dr.read()
        self.assertEqual(f"{parent_title}/{new_title}", data['path'])
        self.assertEqual(new_title, data['title'])
        self.assertEqual(True, data['is_dir'])

    def test_move_workspace_from_root_and_back(self):
        title = "moving_ws"
        content = 'discontent'
        dir_title = 'in_root_dir'
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        ws = Workspace(path='', _conf={"title": title, "content": content})
        ws.create()
        old_path = ws.filesystem_path.parent
        ws.update(_conf={"new_path": dir_title})
        new_path = ws.filesystem_path.parent
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(dir_title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 1)
        ws.update(_conf={"new_path": ""})
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual("", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 0)

    def test_move_workspace_far_from_root_and_back(self):
        title = "moving_ws"
        content = 'discontent'
        parent_dir_title = 'in_root_dir'
        dir_title = 'next_dir'
        parent_dr = Directory(path='', _conf={"title": parent_dir_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(parent_dir_title), _conf={"title": dir_title})
        dr.create()
        ws = Workspace(path='', _conf={"title": title, "content": content})
        ws.create()
        old_path = ws.filesystem_path.parent
        ws.update(_conf={"new_path": f"{parent_dir_title}/{dir_title}"})
        new_path = ws.filesystem_path.parent
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(f"{parent_dir_title}/{dir_title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 1)
        ws.update(_conf={"new_path": ""})
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual("", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 0)

    def test_move_workspace(self):
        title = "moving_ws"
        content = 'discontent'
        source_dir = 'src'
        destination_dir = 'dst'
        src = Directory(path='', _conf={"title": source_dir})
        src.create()
        dst = Directory(path='', _conf={"title": destination_dir})
        dst.create()
        ws = Workspace(path=utils._encode_name(source_dir), _conf={"title": title, "content": content})
        ws.create()
        old_path = ws.filesystem_path.parent
        ws.update(_conf={"new_path": destination_dir})
        new_path = ws.filesystem_path.parent
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(destination_dir, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 0)  # no workspace at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 1)
        ws.update(_conf={"new_path": source_dir})
        data = ws.read()
        self.assertEqual(ws.id, data['id'])
        self.assertEqual(source_dir, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(content, data['content'])
        self.assertEqual(False, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*.json'))), 1)  # workspace back at old path
        self.assertEqual(len(list(new_path.glob('*.json'))), 0)

    def test_move_directory_from_root_and_back(self):
        title = "moving_dir"
        dir_title = 'in_root_dir'
        dr = Directory(path='', _conf={"title": title})
        dr.create()
        dst = Directory(path='', _conf={"title": dir_title})
        dst.create()
        old_path = dr.filesystem_path.parent
        dr.update(_conf={"new_path": dir_title})
        new_path = dr.filesystem_path.parent
        data = dr.read()
        self.assertEqual(f"{dir_title}/{title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 2)  # no directory at old path
        self.assertEqual(len(list(new_path.glob('*'))), 2)
        dr.update(_conf={"new_path": ""})
        data = dr.read()
        self.assertEqual(title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 3)  # directory back at old path
        self.assertEqual(len(list(new_path.glob('*'))), 1)

    def test_move_directory_far_from_root_and_back(self):
        title = "moving_dir"
        dir_title = 'in_root_dir'
        next_dir_title = "next_dir"
        dr = Directory(path='', _conf={"title": title})
        dr.create()
        in_root_dir = Directory(path='', _conf={"title": dir_title})
        in_root_dir.create()
        next_dir = Directory(path=utils._encode_name(dir_title), _conf={"title": next_dir_title})
        next_dir.create()
        old_path = dr.filesystem_path.parent
        dr.update(_conf={"new_path": f"{dir_title}/{next_dir_title}"})
        new_path = dr.filesystem_path.parent
        data = dr.read()
        self.assertEqual(f"{dir_title}/{next_dir_title}/{title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 2)  # no directory at old path
        self.assertEqual(len(list(new_path.glob('*'))), 2)
        dr.update(_conf={"new_path": ""})
        data = dr.read()
        self.assertEqual(title, data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 3)  # directory back at old path
        self.assertEqual(len(list(new_path.glob('*'))), 1)

    def test_move_directory(self):
        title = "moving_dir"
        source_dir = 'src'
        destination_dir = 'dst'
        src = Directory(path='', _conf={"title": source_dir})
        src.create()
        dst = Directory(path='', _conf={"title": destination_dir})
        dst.create()
        dr = Directory(path=utils._encode_name(source_dir), _conf={"title": title})
        dr.create()
        old_path = dr.filesystem_path.parent
        dr.update(_conf={"new_path": destination_dir})
        new_path = dr.filesystem_path.parent
        data = dr.read()
        self.assertEqual(f"{destination_dir}/{title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 1)  # no directory at old path
        self.assertEqual(len(list(new_path.glob('*'))), 2)
        dr.update(_conf={"new_path": source_dir})
        data = dr.read()
        self.assertEqual(f"{source_dir}/{title}", data['path'])
        self.assertEqual(title, data['title'])
        self.assertEqual(True, data['is_dir'])
        self.assertEqual(len(list(old_path.glob('*'))), 2)  # directory back at old path
        self.assertEqual(len(list(new_path.glob('*'))), 1)

    def test_move_dir_inside_itself(self):
        dir_title = 'in_root_dir'
        next_dir_title = "next_dir"
        in_root_dir = Directory(path='', _conf={"title": dir_title})
        in_root_dir.create()
        next_dir = Directory(path=utils._encode_name(dir_title), _conf={"title": next_dir_title})
        next_dir.create()
        try:
            in_root_dir.update(_conf={"new_path": f"{dir_title}/{next_dir_title}"})
            self.assertTrue(False, 'dir somehow was moved inside itself')
        except WorkspaceManagerException:
            self.assertTrue(True)

    def test_move_dir_where_dir_with_such_name_already_exists(self):
        dir_title = 'in_root_dir'
        next_dir_title = "next_dir"
        in_root_dir = Directory(path='', _conf={"title": dir_title})
        in_root_dir.create()
        next_dir = Directory(path=utils._encode_name(dir_title), _conf={"title": next_dir_title})
        next_dir.create()
        phony_dir = Directory(path='', _conf={"title": next_dir_title})
        phony_dir.create()
        try:
            phony_dir.update(_conf={"new_path": f"{dir_title}"})
            self.assertTrue(False, 'dir somehow was moved inside a dir that already has the dir with such name')
        except Exception as e:
            self.assertTrue(True)

    def test_delete_workspace_in_root(self):
        title = 'deleteme'
        content = 'dark secrets'
        ws = Workspace(path='', _conf={"title": title, "content": content})
        ws.create()
        ws.delete()
        self.assertEqual(len(list(self.root_dir.filesystem_path.glob('*.json'))), 0)

    def test_delete_workspace(self):
        title = 'deleteme'
        content = 'dark secrets'
        dir_title = 'in_root_dir'
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        ws = Workspace(path=utils._encode_name(dir_title), _conf={"title": title, "content": content})
        ws.create()
        ws.delete()
        self.assertEqual(len(list(dr.filesystem_path.glob('*.json'))), 0)

    def test_delete_directory_in_root(self):
        title = 'deleteme'
        content = 'dark secrets'
        dir_title = 'in_root_dir'
        next_dir = "next_dir"
        parent_dr = Directory(path='', _conf={"title": dir_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(dir_title), _conf={"title": next_dir})
        dr.create()
        ws = Workspace(path=utils._encode_name(dir_title), _conf={"title": title, "content": content})
        ws.create()
        ws0 = Workspace(path=utils._encode_name(dir_title), _conf={"title": title + '0', "content": content + '0'})
        ws0.create()
        self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 7)
        parent_dr.delete()
        self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 1)

    def test_delete_directory(self):
        title = 'deleteme'
        content = 'dark secrets'
        dir_title = 'in_root_dir'
        next_dir = "next_dir"
        parent_dr = Directory(path='', _conf={"title": dir_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(dir_title), _conf={"title": next_dir})
        dr.create()
        ws = Workspace(path=utils._encode_name(f'{dir_title}/{next_dir}'), _conf={"title": title, "content": content})
        ws.create()
        ws0 = Workspace(path=utils._encode_name(f'{dir_title}/{next_dir}'), _conf={"title": title + '0', "content": content + '0'})
        ws0.create()
        self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 7)
        dr.delete()
        self.assertEqual(len(list(self.root_dir.filesystem_path.rglob('*'))), 3)

    def test_reserved_meta_file_name(self):
        dir_title = self.root_dir.dir_metafile_name
        try:
            Directory(path='', _conf={"title": dir_title}).create()
            self.assertTrue(False, 'dir with meta filename somehow was created')
        except WorkspaceManagerException:
            self.assertTrue(True)

    def test_dir_exists(self):
        dir_title = 'in_root_dir'
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        try:
            dr.create()
            self.assertTrue(False, 'dir already existed but somehow created again')
        except WorkspaceManagerException:
            self.assertTrue(True)

    def test_update_workspace_meta(self):
        title = 'ws'
        content = 'dark secrets'
        meta = {'color': 'TRANSPARENT'}
        new_meta = {'color': 'TEAL'}
        ws = Workspace(path='', _conf={"title": title, "content": content, "meta": meta})
        ws.create()
        color = ws.read().get("meta", {}).get("color")
        ws.update(_conf={"meta": new_meta})
        new_color = ws.read().get("meta", {}).get("color")
        self.assertNotEqual(color, new_color)

    def test_update_directory_meta(self):
        dir_title = 'in_root_dir'
        meta = {'color': 'TRANSPARENT'}
        new_meta = {'color': 'TEAL'}
        dr = Directory(path='', _conf={"title": dir_title, "meta": meta})
        dr.create()
        color = dr.read().get("meta", {}).get("color")
        dr.update(_conf={"new_meta": new_meta})
        new_color = dr.read().get("meta", {}).get("color")
        self.assertNotEqual(color, new_color)

    def test_get_owner_workspace(self):
        dir_title = 'in_root_dir'
        title = 'ws'
        content = 'dark secrets'
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        ws = Workspace(path=utils._encode_name(dir_title), _conf={"title": title, "content": content})
        ws.create()
        self.assertEqual(ws.owner, User.objects.get(username='admin'))

    def test_get_owner_directory(self):
        parent_dir_title = 'in_root_dir'
        dir_title = 'next_dir'
        parent_dr = Directory(path='', _conf={"title": parent_dir_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(parent_dir_title), _conf={"title": dir_title})
        dr.create()
        self.assertEqual(dr.owner, User.objects.get(username='admin'))

    def test_set_owner_workspace(self):
        pass

    def test_set_owner_directory(self):
        pass

    def test_get_keychain_workspace(self):
        dir_title = 'in_root_dir'
        title = 'ws'
        content = 'dark secrets'
        dr = Directory(path='', _conf={"title": dir_title})
        dr.create()
        ws = Workspace(path=utils._encode_name(dir_title), _conf={"title": title, "content": content})
        ws.create()
        self.assertTrue(dr.keychain.id == 12 or dr.keychain.id == 13)

    def test_get_keychain_directory(self):
        parent_dir_title = 'in_root_dir'
        dir_title = 'next_dir'
        parent_dr = Directory(path='', _conf={"title": parent_dir_title})
        parent_dr.create()
        dr = Directory(path=utils._encode_name(parent_dir_title), _conf={"title": dir_title})
        dr.create()
        self.assertTrue(dr.keychain.id == 12 or dr.keychain.id == 13)

    def test_set_keychain_workspace(self):
        pass

    def test_set_keychain_directory(self):
        pass

    def tearDown(self) -> None:
        rmtree(self.tmp_path, ignore_errors=False)
        rmtree(self.base_path, ignore_errors=False)
