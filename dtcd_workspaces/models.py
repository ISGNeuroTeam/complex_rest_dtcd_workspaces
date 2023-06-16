from rest_auth.models import KeyChainModel


class DirectoryContentKeychain(KeyChainModel):
    auth_covered_class_import_str = 'dtcd_workspaces.workspaces.directory_content.DirectoryContent'
