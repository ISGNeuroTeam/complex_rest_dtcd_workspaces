import base64
import os
import json
import uuid
import datetime

from typing import List
from pathlib import Path

from dtcd_workspaces.workspaces.directorycontent_exception import DirectoryContentException
from dtcd_workspaces.workspaces.utils import decode_name, encode_name

from dtcd_workspaces.settings import WORKSPACE_BASE_PATH, WORKSPACE_TMP_PATH, DIR_META_NAME
from dtcd_workspaces.workspaces.utils import encode_name, decode_name, copy, remove
from dtcd_workspaces.models import DirectoryContentKeychain

from core.globals import global_vars
from rest_auth.models.abc import IAuthCovered
from rest_auth.models import User
from rest_auth.authorization import auth_covered_method, auth_covered_func


class DirectoryContent:
    # child classes must be registered
    _child_classes = []

    @staticmethod
    def register_child_class(child_cls):
        DirectoryContent._child_classes.append(child_cls)

    # attributes list for json file
    # may be reassigned in child classes
    saved_to_file_attributes = [
        'creation_time', 'modification_time', 'meta', 'keychain_id', 'owner_guid'
    ]

    # --------------role model api methods--------------------
    keychain_model = DirectoryContentKeychain

    @property
    def auth_id(self):
        return self.path

    @property
    def owner(self):
        if self.owner_guid:
            try:
                return User.objects.get(guid=self.owner_guid)
            except User.DoesNotExist:
                return None
        return None

    @owner.setter
    def owner(self, user: 'User'):
        self.owner_guid = user.guid.hex

    @property
    def keychain(self):
        if self.keychain_id:
            try:
                return DirectoryContentKeychain.objects.get(id=self.keychain_id)
            except DirectoryContentKeychain.DoesNotExist:
                return None
        return None

    @keychain.setter
    def keychain(self, keychain: DirectoryContentKeychain):
        self.keychain_id = keychain.id

    @classmethod
    def get_auth_object(cls, auth_id: str):
        return cls.get(auth_id)
    # --------------------------------------------------------

    @classmethod
    def is_path_for_cls(cls, path: str) -> bool:
        """
        determines whether the path belongs to an object of the child class
        """
        raise NotImplementedError

    def __init__(self, path: str, initialized_from_inside_class=False):
        """
        Args:
            path (str): Human readable relative path
            initialized_from_inside_class (bool): Flag, initialization from get class method
                if initialized_from_inside_class=False then object didn't exist before
        """
        self.path: str = self._validate_path(path)
        self.creation_time: float = None
        self.modification_time: float = None
        self.meta: dict = None
        self.owner_guid = None
        self.keychain_id = None

        if not initialized_from_inside_class: # directory content object created for the first time
            self._create_actions(path)

    @auth_covered_func(action_name='create')
    def _create_actions(self, path):
        print(f'CREATE ACTION {path}')
        # use get method to get existing directory content
        if self.absolute_filesystem_path.exists():
            raise DirectoryContentException(DirectoryContentException.PATH_EXISTS, path)

        # when first creation owner is current user
        current_user = global_vars.get_current_user()
        if current_user:
            self.owner_guid = current_user.guid.hex
        else:
            self.owner_guid = None

    @property
    def title(self) -> str:
        return Path(self.path).name

    @property
    def absolute_filesystem_path(self) -> Path:
        return Path(WORKSPACE_BASE_PATH) / self.relative_filesystem_path

    @property
    def relative_filesystem_path(self) -> str:
        return self._get_relative_filesystem_path(self.path)

    @classmethod
    def _get_absolute_filesystem_path(cls, path: str) -> str:
        return str(Path(WORKSPACE_BASE_PATH) / DirectoryContent._get_relative_filesystem_path(path))

    def _write_attributes_to_json_file(self, absolute_file_path: Path):
        if self.creation_time is None:
            self.creation_time = datetime.datetime.now().timestamp()
        else:
            self.modification_time = datetime.datetime.now().timestamp()
        temp_dict = {}
        for attr in self.saved_to_file_attributes:
            temp_dict[attr] = getattr(self, attr)

        self._write_file(temp_dict, absolute_file_path)

    def _read_attributes_from_json_file(self, absolute_file_path: Path):
        """
        Load attributes from json file
        """
        with open(absolute_file_path, 'r', encoding='UTF-8') as f:
            dct = json.load(f)
            for attr in self.saved_to_file_attributes:
                setattr(self, attr, dct.get(attr))
        self._read_method()

    @auth_covered_method(action_name='read')
    def _read_method(self):
        """
        Method for decorator
        """
        pass

    @staticmethod
    def _write_file(data: dict, absolute_filesystem_path: Path):
        """
        Writes dictionary to json file
        Args:
            data (dict): dictionary to write
            absolute_filesystem_path (Path): path to json file
        """
        temp_file = Path(WORKSPACE_TMP_PATH) / Path(f'temp_{str(uuid.uuid4())}')
        try:
            temp_file.write_text(json.dumps(data))
            temp_file.rename(absolute_filesystem_path)  # atomic operation
        except IOError:
            raise DirectoryContentException(DirectoryContentException.IO_ERROR, absolute_filesystem_path)

    @staticmethod
    def _get_relative_filesystem_path(relative_human_readable_path: str) -> str:
        """
        Returns filesystem path
        """
        return os.sep.join(map(
            lambda path_part: encode_name(path_part),
            relative_human_readable_path.split('/')  # no os.sep because it's parameter
        ))

    @staticmethod
    def _get_relative_humanreadable_path(relative_filesystem_path: str) -> str:
        """
        Returns humanreadable path relative to root workspace directory
        """
        return '/'.join(
            map(
                lambda path_part: decode_name(path_part),
                relative_filesystem_path.split(os.sep)
            )
        )

    @staticmethod
    def _validate_path(path):
        tokens = path.split('/')
        for token in tokens[:len(tokens) - 1]:  # security
            if token == '..' or token == '' or token == DIR_META_NAME:
                raise DirectoryContentException(DirectoryContentException.PATH_WITH_DOTS, path)
        if tokens[-1] == '..' or tokens[-1] == DIR_META_NAME:
            raise DirectoryContentException(DirectoryContentException.PATH_WITH_DOTS, path)
        return path

    @auth_covered_method(action_name='update')
    def save(self):
        """
        Saves object to filesystem storage
        """
        raise NotImplementedError

    def load(self):
        """
        load attributes from filesystem
        Raises DirectoryContentException.DOES_NOT_EXIST exception
        """
        raise NotImplementedError

    @classmethod
    def get(cls, path: str) -> 'DirectoryContent':
        """
        Load object from filesystem storage
        """
        for child_cls in DirectoryContent._child_classes:
            if child_cls.is_path_for_cls(path):
                return child_cls.get(path)

    @auth_covered_method(action_name='move')
    def move(self, new_path: str):
        """
        Moves all content to new path
        Args:
            new_path (str): new relative path
        """

        new_absolute_path = Path(self._get_absolute_filesystem_path(new_path))
        new_title = new_path.split('/')[-1]
        new_directory_path = '/'.join(new_path.split('/')[:-1])
        directory_absolute_path = Path(self._get_absolute_filesystem_path(new_directory_path))

        if not directory_absolute_path.exists():
            raise DirectoryContentException(DirectoryContentException.INVALID_PATH, new_directory_path)
        if new_path == self.path:
            raise DirectoryContentException(DirectoryContentException.NEW_PATH_EQ_OLD_PATH, new_directory_path)
        if self.absolute_filesystem_path in new_absolute_path.parents:
            raise DirectoryContentException(DirectoryContentException.MOVING_DIR_INSIDE_ITSELF, self.path, new_directory_path)

        try:
            self.absolute_filesystem_path.rename(new_absolute_path)
        except IOError as err:
            raise DirectoryContentException(DirectoryContentException.IO_ERROR, str(err))

        self.path = new_path

    @auth_covered_method(action_name='delete')
    def delete(self):
        remove(self.absolute_filesystem_path)









