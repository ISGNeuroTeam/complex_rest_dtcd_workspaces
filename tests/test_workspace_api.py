import json
import shutil

from pathlib import Path


from rest.test import APIClient, TransactionTestCase as TestCase

from rest_auth.models import User
from rest_auth.apps import on_ready_actions as rest_auth_on_ready_actions
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.workspaces.workspace import Workspace
from dtcd_workspaces.workspaces.directorycontent_exception import DirectoryContentException
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME


def create_test_users():
    admin_user = User(username='admin', is_staff=True, is_active=True)
    admin_user.set_password('admin')
    admin_user.save()
    ordinary_user1 = User(username='ordinary_user1')
    ordinary_user1.set_password('ordinary_user1')
    ordinary_user1.save()


class WorkspaceApiTest(TestCase):
    def _get_user_token(self):
        data = {
            "login": "ordinary_user1",
            "password": "ordinary_user1"
        }
        response = self.client.post('/auth/login/', data=data)
        return response.data['token']

    def setUp(self) -> None:
        rest_auth_on_ready_actions()
        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)
        (Path(WORKSPACE_BASE_PATH) / DIR_META_NAME).write_text(
            json.dumps({"meta": {'root_meta': 'some_root_meta'}})
        )
        root_dir = Directory.get('')
        root_dir.save()
        create_test_users()
        self.base_url = '/dtcd_workspaces/v1/workspace'
        self.client = APIClient()
        self.user_token = self._get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.user_token))

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def test_create_workspace(self):
        meta = {'some_meta_info': 1}
        content = {
            'some_content': 'some_content'
        }
        response = self.client.post(
            self.base_url + '/?path=test1', data={'meta': meta, 'content': content}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        workspace = Workspace.get('test1')
        self.assertDictEqual(workspace.meta, meta)
        self.assertDictEqual(workspace.content, content)

    def test_update_workspace(self):
        self.test_create_workspace()
        new_meta = {
            'new_meta': 'new_meta'
        }
        response = self.client.post(
            self.base_url + '/?path=test1&action=update',
            data={
                'meta': new_meta
            },
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        workspace = Workspace.get('test1')
        self.assertDictEqual(workspace.meta, new_meta)

    def test_move_workspace(self):
        dir1 = Directory('path1')
        dir1.save()
        dir2 = Directory('path1/path2')
        dir2.save()
        dir3 = Directory('path4')
        dir3.save()

        test_meta = {
           'meta': 'test_meta'
        }
        test_content = {
            'test_content': 3
        }
        workspace = Workspace('path1/path2/test_path')
        workspace.meta = test_meta
        workspace.content = test_content
        workspace.save()
        response = self.client.post(
            self.base_url + '/?path=path1/path2/test_path&action=move',
            data={
                'new_path': 'path4/new_test_path'
            }
        )
        self.assertEqual(response.status_code, 200)
        workspace = Workspace.get('path4/new_test_path')
        self.assertDictEqual(workspace.meta, test_meta)
        self.assertDictEqual(workspace.content, test_content)

    def test_delete_workspace(self):
        meta = {'some_meta_info': 1}
        content = {'some_content': 34}
        response = self.client.post(
            self.base_url + '/?path=test1', data={'meta': meta, 'content': content}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        workspace = Workspace.get('test1')
        self.assertDictEqual(workspace.meta, meta)
        self.assertDictEqual(workspace.content, content)
        response = self.client.post(
            self.base_url + '/?path=test1&action=delete', format='json'
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(DirectoryContentException):  # now not exist
            workspace = workspace.get('test1')





