import base64
import os
import uuid
import json
from shutil import rmtree, copytree, copy2

from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from dtcd_workspaces.workspaces import workspacemanager_exception
from pathlib import Path
from typing import List


def encode_name(name: str) -> str:
    encoded = base64.urlsafe_b64encode(name.encode()).decode()
    return encoded


def decode_name(encoded_name: str) -> str:
    decoded = base64.urlsafe_b64decode(encoded_name).decode()
    return decoded


def _get_dir_path(name: str, path: Path) -> Path:
    _path = path / encode_name(name)
    return _path


def _rename(f: Path, t: Path):
    try:
        os.rename(f, t)
    except IOError:
        raise WorkspaceManagerException(workspacemanager_exception.IO_ERROR, f)


def _remove(f: Path):
    try:
        rmtree(f) if f.is_dir() else f.unlink()
    except IOError:
        raise WorkspaceManagerException(workspacemanager_exception.IO_ERROR, f)


def _copy(f: Path, t: Path):
    try:
        copytree(f, t / f.name) if f.is_dir() else copy2(f, t)  # copy2 preserves meta data
    except IOError as e:
        raise WorkspaceManagerException(workspacemanager_exception.IO_ERROR, f)


def _is_uuid4(text: str):
    try:
        uuid_obj = uuid.UUID(text, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == text


def _get_file_name(file: Path) -> str:
    return file.with_suffix('').name


class FilesystemWorkspaceManager:

    """Manager does what is required for objects related to workspaces (currently Workspace and Directory)"""

    def __init__(self, path, tmp_path):
        self.final_path = Path(path)
        self.tmp_path = Path(tmp_path)

    def _resolve_path(self, path_tokens: List[str]) -> Path:
        """Encode path part by part"""
        resolved_path = self.final_path
        for token in path_tokens:
            if token:  # skipping root which is represented as empty string
                resolved_path = _get_dir_path(token, resolved_path)
        return resolved_path

    def _resolve_filesystem_path(self, path_tokens: List[str]) -> Path:
        """Decode path part by part"""
        resolved_path = Path('')
        for token in path_tokens:
            resolved_path /= decode_name(token)
        return resolved_path

    def _get_tokens_from_path(self, path: str):

        tokens = path.split(os.sep)

        for token in tokens[:len(tokens) - 1]:  # security
            if token == '..' or token == '':
                raise WorkspaceManagerException(workspacemanager_exception.PATH_WITH_DOTS, path)
        if tokens[-1] == '..':
            raise WorkspaceManagerException(workspacemanager_exception.PATH_WITH_DOTS, path)

        return tokens

    def get_filesystem_path(self, human_readable_path: str) -> Path:
        """Encode human-readable parth into acceptable charset"""
        return self._resolve_path(self._get_tokens_from_path(human_readable_path))

    def get_human_readable_path(self, filesystem_path: Path) -> str:
        """Decode human-filesystem_path parth into acceptable charset"""
        relative_path = str(filesystem_path)[len(str(self.final_path)) + 1:]
        resolved_path = str(self._resolve_filesystem_path(self._get_tokens_from_path(relative_path)))
        return resolved_path if not resolved_path == '.' else ''

    def write_file(self, data: dict, path: Path):
        temp_file = self.tmp_path / Path(f'temp_{str(uuid.uuid4())}').with_suffix('.json')
        try:
            temp_file.write_text(json.dumps(data))
            temp_file.rename(path)  # atomic operation
        except IOError:
            raise WorkspaceManagerException(workspacemanager_exception.IO_ERROR, path)


manager = FilesystemWorkspaceManager(WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH)
