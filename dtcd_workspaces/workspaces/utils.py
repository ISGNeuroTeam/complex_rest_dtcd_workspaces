import base64
import os
import uuid
import json
from shutil import rmtree, copytree, copy2

from django.core.serializers.json import DjangoJSONEncoder

from dtcd_workspaces.workspaces.directorycontent_exception import DirectoryContentException
from pathlib import Path
from typing import List


class UUIDDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    uuid_possible_keys = ('uuid', 'guid', 'id')

    def object_hook(self, dct):
        key = None
        for k in UUIDDecoder.uuid_possible_keys:
            if k in dct:
                key = k
        if key:
            try:
                dct[key] = uuid.UUID(dct[key])
            except (ValueError, TypeError):
                pass
        return dct


def json_dumps(obj):
    return json.dumps(obj, cls=DjangoJSONEncoder)


def json_load(file: Path):
    return json.load(file, cls=UUIDDecoder)




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
        raise DirectoryContentException(DirectoryContentException.IO_ERROR, f)


def remove(f: Path):
    try:
        rmtree(f) if f.is_dir() else f.unlink()
    except IOError:
        raise DirectoryContentException(DirectoryContentException.IO_ERROR, f)


def copy(f: Path, t: Path):
    try:
        copytree(f, t / f.name) if f.is_dir() else copy2(f, t)  # copy2 preserves meta data
    except IOError as e:
        raise DirectoryContentException(DirectoryContentException.IO_ERROR, f)


def _is_uuid4(text: str):
    try:
        uuid_obj = uuid.UUID(text, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == text


def _get_file_name(file: Path) -> str:
    return file.with_suffix('').name

