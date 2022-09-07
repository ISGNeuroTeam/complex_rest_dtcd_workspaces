class AuthCoveredWorkspace(AuthCoveredModel, Workspace):
    keychain_model = WorkspacesKeychain

    def __init__(self, *args, path: str = None, title: str = None, creation_time: float = None, **kwargs):
        Workspace.__init__(self, *args, path=path, title=title, creation_time=creation_time, **kwargs)
