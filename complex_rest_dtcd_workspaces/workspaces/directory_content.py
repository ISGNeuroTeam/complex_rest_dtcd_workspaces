import uuid
import datetime
import json
from .utils import FilesystemWorkspaceManager, _encode_name, _decode_name, _is_uuid4, _get_file_name, manager
from typing import Dict, List, Optional
from pathlib import Path
from dtcd_workspaces.workspaces import workspacemanager_exception
from dtcd_workspaces.workspaces.workspacemanager_exception import WorkspaceManagerException
from ..settings import DIR_META_NAME, ROLE_MODEL_ACTIONS
from dtcd_workspaces.models import ProtectedResource
from rest_auth.models import IAuthCovered, User
from rest_auth.authorization import auth_covered_method, check_authorization
from rest_auth.exceptions import AccessDeniedError


class DirectoryContent(IAuthCovered):
    kwargs_map: Dict[str, str]
    manager: FilesystemWorkspaceManager = manager
    dir_metafile_name = DIR_META_NAME

    def __init__(self, path: str, **kwargs):
        self.path = _decode_name(path)
        self.title = None
        self.meta = None
        self.permissions = {}
        self.creation_time = datetime.datetime.now().timestamp()
        self.modification_time = self.creation_time
        self.id = kwargs.get('_conf', {}).get('id', self._get_new_id())  # get id from _conf for put method

    @property
    def owner(self) -> Optional['User']:
        """
        Returns owner
        """
        return User.objects.get(id=self.protected_resource.owner)

    @owner.setter
    def owner(self, user: 'User'):
        """
        Sets owner
        """
        pr = ProtectedResource.objects.filter(object_id=self.id)
        if pr.exists():
            self.update_protected_resources(_id=self.id, owner_id=user.id)
        else:
            self.create_protected_resources(self.id, self.title, user.id, self.protected_resource.keychain)

    @property
    def keychain(self) -> Optional['IKeyChain']:
        """
        Returns object keychain
        """
        return self.protected_resource.keychain

    @keychain.setter
    def keychain(self, keychain: 'IKeyChain'):
        """
        sets keychain
        """
        pr = ProtectedResource.objects.filter(object_id=self.id)
        if pr.exists():
            self.update_protected_resources(_id=self.id, keychain=keychain)
        else:
            self.create_protected_resources(self.id, self.title, self.protected_resource.owner, keychain)

    def _load_permissions(self):
        for action_name in ROLE_MODEL_ACTIONS.keys():
            try:
                check_authorization(self, 'workspace.create')
                self.permissions[action_name] = True
            except AccessDeniedError:
                self.permissions[action_name] = False

    @classmethod
    def is_workspace(cls, _path: Path) -> bool:
        return _path.is_file() and _path.exists() and _path.suffix == '.json'

    @classmethod
    def is_directory(cls, _path: Path):
        return Path(_path, cls.dir_metafile_name).exists()

    @classmethod
    def _get_new_id(cls) -> str:
        return str(uuid.uuid4())

    @classmethod
    def get_id(cls, _path: Path):
        raise NotImplementedError

    @property
    def filesystem_path(self):
        return self.manager.get_filesystem_path(self.path)

    @property
    def protected_resource(self) -> ProtectedResource:
        ids_chain = self.get_ids_chain(self.filesystem_path)
        resources = {obj.object_id: obj for obj in ProtectedResource.objects.filter(object_id__in=ids_chain)}
        _protected_resource: Optional[ProtectedResource] = None
        for _id in ids_chain:  # ids_chain is never empty because of create_root_records command
            _protected_resource = resources.get(_id)
            if _protected_resource:
                break
        return _protected_resource

    def _load_meta(self):
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    @auth_covered_method(action_name='workspace.create')
    def create(self):
        self.save()  # save flushes object data to permanent storage (currently file system)

    def read(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def as_dict(self):
        self._load_meta()
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    def as_json(self):
        return json.dumps(self.as_dict())

    def exists(self):
        return self.filesystem_path.exists()

    def get_target_directory_content(self, path: str):

        target = DirectoryContent(path=_encode_name(path))
        if not target.filesystem_path.exists():
            raise WorkspaceManagerException(workspacemanager_exception.INVALID_PATH, path)
        if target.filesystem_path == self.filesystem_path.parent:
            raise WorkspaceManagerException(workspacemanager_exception.NEW_PATH_EQ_OLD_PATH, path)
        if self.filesystem_path in target.filesystem_path.parents:
            raise WorkspaceManagerException(workspacemanager_exception.MOVING_DIR_INSIDE_ITSELF,
                                            self.filesystem_path,
                                            target.filesystem_path)

        return target

    def get_ids_chain(self, from_path: Path):
        """Get ids of object itself and all the object's parents"""
        ids = []
        # If object is a file i.e. workspace, then get its id and go for directories
        if self.is_workspace(from_path):
            file_name = _get_file_name(from_path)
            if _is_uuid4(file_name):
                ids.append(file_name)
            from_path = from_path.parent

        # Iterate through dirs and get ids
        while not from_path == self.manager.final_path:
            ids.append(DirectoryContent.get_id(from_path))
            from_path = from_path.parent
        ids.append(DirectoryContent.get_id(from_path))
        return ids

    def create_protected_resources(self, _id: str, title: str, owner_id: int, keychain: 'IKeyChain'):
        res = ProtectedResource(object_id=_id, name=title, owner=owner_id, keychain=keychain)
        res.save()

    def update_protected_resources(self, _id: str, title: str = None, owner_id: int = None,
                                   keychain: 'IKeyChain' = None):
        try:
            res: ProtectedResource = ProtectedResource.objects.get(object_id=_id)
            if title:
                res.name = title
            if owner_id:
                res.owner = owner_id
            if keychain:
                res.keychain = keychain
            res.save()
        except ProtectedResource.DoesNotExist as e:
            pass

    def delete_protected_resources(self, ids: List[str] = tuple()):
        resources = ProtectedResource.objects.filter(object_id__in=ids)
        resources.delete()
