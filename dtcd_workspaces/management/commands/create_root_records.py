import json

from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from core.globals import global_vars
from rest_auth.models import User, Plugin, SecurityZone

from dtcd_workspaces.models import DirectoryContentKeychain
from dtcd_workspaces.workspaces.directory import Directory
from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME


class Command(BaseCommand):
    help = 'Creates necessary records in rest auth for Role Model in workspaces'
    # TODO tests for this command?
    # https://docs.djangoproject.com/en/4.0/topics/testing/tools/#topics-testing-management-commands

    def handle(self, *args, **options):
        # disable authorization
        global_vars['disable_authorization'] = True
        keychain_name = 'root_access_zone_keychain'

        if not DirectoryContentKeychain.objects.filter(_name=keychain_name).exists():
            # admin may be missing
            try:
                admin = User.objects.get(username='admin')
            except User.DoesNotExist:
                raise CommandError(
                    'The user "admin" does not exist. '
                    'Have you forgot to create a superuser?'
                )

            root_zone, created = SecurityZone.objects.get_or_create(name='root_access')

            root_keychain = DirectoryContentKeychain(name=keychain_name)
            root_keychain.zone = root_zone
            root_keychain.save()

            # get or create root directory

            Path(WORKSPACE_BASE_PATH).mkdir(exist_ok=True, parents=True)
            Path(WORKSPACE_TMP_PATH).mkdir(exist_ok=True, parents=True)
            directory_root_meta_path = Path(WORKSPACE_BASE_PATH) / DIR_META_NAME
            with open(directory_root_meta_path, 'w') as fw:
                fw.write(
                    json.dumps(
                        {
                        "id": "6d4a84ba-f411-4ac6-8b01-85d5ed620cf5",
                        "owner_guid": "52540440-2a83-4587-ad10-202df4c31095",
                        "meta": {'root_meta': 'some_root_meta'}
                    })
                )

            self.stdout.write(self.style.SUCCESS('Successfully created root keychain and root security zone'))
