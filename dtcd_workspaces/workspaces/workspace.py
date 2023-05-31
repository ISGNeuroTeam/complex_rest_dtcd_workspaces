from directory_content import DirectoryContent


class Workspace(DirectoryContent):
    def __init__(self, path: str):
        super().__init__(path)

    def save(self):
        pass
