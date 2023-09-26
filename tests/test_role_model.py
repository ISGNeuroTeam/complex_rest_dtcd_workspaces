import json
import shutil

from pathlib import Path


from rest.test import APIClient, APITestCase

from rest_auth.models import User, Action, Plugin, Permit, AccessRule, Role, Group, IAuthCovered, SecurityZone, AuthCoveredClass
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
    ordinary_user2 = User(username='ordinary_user2')
    ordinary_user2.set_password('ordinary_user2')
    ordinary_user2.save()


class RoleModelTest(APITestCase):

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
        self.auth_covered_object_class_import_str = 'dtcd_workspaces.workspaces.directory_content.DirectoryContent'
        self.base_url = '/dtcd_workspaces/v1'
        self.client = APIClient()

    def tearDown(self) -> None:
        shutil.rmtree(WORKSPACE_TMP_PATH)
        shutil.rmtree(WORKSPACE_BASE_PATH)

    def test_access_denied(self):
        self.login('admin', 'admin')
        workspace_path = 'test_workspace1'
        workspace = Workspace(workspace_path)
        workspace.save()
        user_group = Group(name='test_group')
        user_group.save()
        ordinary_user = User.objects.get(username='ordinary_user1')
        ordinary_user.groups.add(user_group)
        ordinary_user.save()

        user_role = Role(name='test_role')
        user_role.save()
        user_role.groups.add(user_group)
        security_zone = SecurityZone(name='root_zone')
        security_zone.save()

        # create keychain
        response = self.client.post(
            f'/auth/keychains/{self.auth_covered_object_class_import_str}/',
            {
                'security_zone': security_zone.id,
                'auth_covered_objects': [workspace_path,],
            },
            format='json'
        )
        keychain_id = response.data['id']
        # add permission for access deny
        action_read = Action.objects.get(plugin__name='dtcd_workspaces', name='dtcd_workspaces.read')

        # check access
        self.login('ordinary_user1', 'ordinary_user1')
        response = self.client.get(self.base_url + f'/workspace/?path={workspace_path}')
        self.assertEqual(response.status_code, 200)

        # forbid reading workspace
        self.login('admin', 'admin')
        response = self.client.post(
            f'/auth/permits/{self.auth_covered_object_class_import_str}/',
            {
                'access_rules': [
                    {
                        'action': action_read.id,
                        'rule': False,
                        'by_owner_only': False
                    }, ],
                'roles': [user_role.id, ],
                'keychain_ids': [str(keychain_id), ],


            },
            format='json'
        )
        # check exception raised, trying to read
        self.login('ordinary_user1', 'ordinary_user1')
        response = self.client.get(self.base_url + f'/workspace/?path={workspace_path}')
        self.assertEqual(response.status_code, 403)

    def test_create_denied(self):
        user_group = Group(name='test_group')
        user_group.save()
        ordinary_user = User.objects.get(username='ordinary_user1')
        ordinary_user.groups.add(user_group)
        ordinary_user.save()

        user_role = Role(name='test_role')
        user_role.save()
        user_role.groups.add(user_group)

        self.login('ordinary_user1', 'ordinary_user1')

        response = self.client.post(
            self.base_url + '/directory/?path=test1', data={'meta': {'tset': 'test'}}, format='json'
        )
        self.assertEqual(response.status_code, 200)

        # add permission for access deny
        action_create = Action.objects.get(plugin__name='dtcd_workspaces', name='dtcd_workspaces.create')

        self.login('admin', 'admin')
        response = self.client.post(
                f'/auth/permits/{self.auth_covered_object_class_import_str}/',
                {
                    'access_rules': [
                        {
                            'action': action_create.id,
                            'rule': False,
                            'by_owner_only': False
                        }, ],
                    'roles': [user_role.id, ],
                },
                format='json'
        )

        self.login('ordinary_user1', 'ordinary_user1')

        response = self.client.post(
            self.base_url + '/directory/?path=test3', data={'meta': {'tset': 'test'}}, format='json'
        )
        self.assertEqual(response.status_code, 403)

    def test_read_only_by_owner(self):
        user_group = Group(name='test_group')
        user_group.save()
        ordinary_user = User.objects.get(username='ordinary_user1')
        ordinary_user.groups.add(user_group)
        ordinary_user.save()

        ordinary_user2 = User.objects.get(username='ordinary_user2')
        ordinary_user2.groups.add(user_group)
        ordinary_user2.save()

        user_role = Role(name='test_role')
        user_role.save()
        user_role.groups.add(user_group)

        self.login('ordinary_user1', 'ordinary_user1')
        test_workspace_path = 'test1'
        # create test workspace ordinary_user1 is owner
        response = self.client.post(
            self.base_url + f'/workspace/?path={test_workspace_path}',
            data={'meta': {'tset': 'test'}, 'content': {'test_content': 'tset'}}, format='json'
        )
        workspace = Workspace.get(test_workspace_path)

        self.assertEqual(response.status_code, 200)

        # add permission for access deny
        action_read = Action.objects.get(plugin__name='dtcd_workspaces', name='dtcd_workspaces.read')

        self.login('admin', 'admin')

        # read access have only not owner (ordinary user2)
        response = self.client.post(
                f'/auth/permits/{self.auth_covered_object_class_import_str}/',
                {
                    'access_rules': [
                        {
                            'action': action_read.id,
                            'rule': False,
                            'by_owner_only': True,
                        },

                    ],
                    'roles': [user_role.id, ],
                },
                format='json'
        )
        self.assertEqual(response.status_code, 201)

        self.login('ordinary_user1', 'ordinary_user1')
        response = self.client.get(
            self.base_url + f'/workspace/?path={test_workspace_path}'
        )
        # ordinary user1 is owner so access denied
        self.assertEqual(response.status_code, 403)
        self.login('ordinary_user2', 'ordinary_user2')
        response = self.client.get(
            self.base_url + f'/workspace/?path={test_workspace_path}'
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_inner_directory_denied(self):
        user_group = Group(name='test_group')
        user_group.save()
        ordinary_user = User.objects.get(username='ordinary_user1')
        ordinary_user.groups.add(user_group)
        ordinary_user.save()

        user_role = Role(name='test_role')
        user_role.save()
        user_role.groups.add(user_group)

        directory = Directory('test1')
        directory.save()

        inner_dir = Directory('test1/inner_dir')
        inner_dir.save()

        self.login('admin', 'admin')
        action_delete = Action.objects.get(plugin__name='dtcd_workspaces', name='dtcd_workspaces.delete')

        # create keychain
        response = self.client.post(
            f'/auth/keychains/{self.auth_covered_object_class_import_str}/',
            {
                'auth_covered_objects': ['test1/inner_dir', ],
            },
            format='json'
        )
        keychain_id = response.data['id']
        # forbid delete inner directory
        response = self.client.post(
                f'/auth/permits/{self.auth_covered_object_class_import_str}/',
                {
                    'access_rules': [
                        {
                            'action': action_delete.id,
                            'rule': False,
                            'by_owner_only': False,
                        },

                    ],
                    'roles': [user_role.id, ],
                    'keychain_ids': [keychain_id, ]
                },
                format='json'
        )
        self.assertEqual(response.status_code, 201)

        # try to delete directory
        self.login('ordinary_user1', 'ordinary_user1')

        response = self.client.post(
            self.base_url + '/directory/?path=test1&action=delete', format='json'
        )
        self.assertEqual(response.status_code, 403)
