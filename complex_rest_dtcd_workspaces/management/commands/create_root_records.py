from django.core.management.base import BaseCommand, CommandError
from rest_auth.models import ProtectedResource, SecurityZone, KeyChain, User, Plugin


class Command(BaseCommand):
    help = 'Creates necessary records in rest auth for Role Model in workspaces'

    def handle(self, *args, **options):
        if not KeyChain.objects.filter(keychain_id='root_access_zone_keychain').exists():
            admin = User.objects.get(username='admin')
            plugin = Plugin.objects.get(name='dtcd_workspaces')
            root_zone = SecurityZone(name='root_access')
            root_zone.save()
            root_keychain = KeyChain(keychain_id='root_access_zone_keychain', plugin=plugin, zone=root_zone)
            root_keychain.save()
            root_protected_resource = ProtectedResource(object_id='',
                                                        owner=admin,
                                                        keychain=root_keychain,
                                                        name='root_workspace_directory')
            root_protected_resource.save()
            self.stdout.write(self.style.SUCCESS('Successfully created necessary records in rest auth'))
        else:
            self.stderr.write(self.style.ERROR('Necessary records in rest auth already exist'))
