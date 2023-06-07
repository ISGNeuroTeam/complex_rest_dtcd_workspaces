import json
from pathlib import Path


from rest.test import APIClient, TransactionTestCase as TestCase

from rest_auth.models import User

from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME


def create_test_users():
    admin_user = User(username='admin', is_staff=True, is_active=True)
    admin_user.set_password('admin')
    admin_user.save()
    ordinary_user1 = User(username='ordinary_user1')
    ordinary_user1.set_password('ordinary_user1')
    ordinary_user1.save()


class DirectoryApiTest(TestCase):
    def _get_user_token(self):
        data = {
            "login": "ordinary_user1",
            "password": "ordinary_user1"
        }
        response = self.client.post('/auth/login/', data=data)
        return response.data['token']

    def setUp(self) -> None:

        Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
        Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)
        (Path(WORKSPACE_BASE_PATH) / DIR_META_NAME).write_text(
            json.dumps({"meta": ""})
        )
        root_dir = Directory.get('')
        root_dir.save()
        create_test_users()
        self.base_url = '/dtcd_workspaces/v1'
        self.client = APIClient()
        self.user_token = self._get_user_token()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.user_token))

    def test_get_root_directory(self):
        response = self.client.get(self.base_url + '/directory/?path=')
        self.assertEqual(response.status_code, 200)
        directory_dct = response.data
        self.assertEqual(directory_dct['path'], '')

    def test_create_directory(self):
        meta = {'some_meta_info': 1}
        response = self.client.post(
            self.base_url + '/directory/?path=test1', data={'meta': meta}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        directory = Directory.get('test1')
        self.assertDictEqual(directory.meta, meta)
