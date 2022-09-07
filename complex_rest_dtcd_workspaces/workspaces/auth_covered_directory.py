class AuthCoveredDirectory(AuthCoveredModel, Directory):
    keychain_model = WorkspacesKeychain

    def __init__(self, *args, path: str = None, title: str = None, creation_time: float = None, **kwargs):
        Directory.__init__(self, *args, path=path, title=title, creation_time=creation_time, **kwargs)
