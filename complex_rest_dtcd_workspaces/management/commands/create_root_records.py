from django.core.management.base import BaseCommand, CommandError
from rest_auth.models import ProtectedResource, SecurityZone, KeyChain, User, Plugin


class Command(BaseCommand):
    help = 'Creates necessary records in rest auth for Role Model in workspaces'
    # TODO tests for this command?
    # https://docs.djangoproject.com/en/4.0/topics/testing/tools/#topics-testing-management-commands

    def handle(self, *args, **options):
        keychain_id = 'root_access_zone_keychain'

        if not KeyChain.objects.filter(keychain_id=keychain_id).exists():
            # admin may be missing
            try:
                admin = User.objects.get(username='admin')
            except User.DoesNotExist:
                raise CommandError(
                    'The user "admin" does not exist. '
                    'Have you forgot to create a superuser?'
                )

            # TODO plugin's name may change - get from settings?
            try:
                plugin = Plugin.objects.get(name='dtcd_workspaces')
            except Plugin.DoesNotExist:
                raise CommandError(
                    'The plugin "dtcd_workspaces" does not exist. '
                    "Is something wrong with this plugin's name?"
                )

            # TODO security zone with the given name might exist
            root_zone = SecurityZone(name='root_access')
            root_zone.save()
            root_keychain = KeyChain(keychain_id=keychain_id, plugin=plugin, zone=root_zone)
            root_keychain.save()

            # TODO better logic for this statment?
            # this protected resource object may exist already
            root_protected_resource = ProtectedResource.objects.get_or_create(
                object_id='',
                defaults=dict(
                    owner=admin,
                    keychain=root_keychain,
                    name='root_workspace_directory'
                )
            )

            self.stdout.write(self.style.SUCCESS('Successfully created necessary records in rest auth'))
        else:
            self.stderr.write(self.style.WARNING(f'KeyChain record with id "{keychain_id}" already exists.'))
