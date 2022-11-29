import re
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from boto3 import Session


class Storage(ABC):
    """
    对config里支持的本地存储方式的一种抽象
    """

    @abstractmethod
    def remove_tree(self, path: str) -> bool:
        """
        删除整个目录
        Returns:

        """
        pass


class LocalDiskStorage(Storage):

    def remove_tree(self, local_path: str) -> bool:
        try:
            shutil.rmtree(local_path, ignore_errors=True)
            return True
        except Exception as e:
            return False


class S3Storage(Storage):

    def __init__(self, path: str, endpoint: str, access_key: str,
                 secret_key: str):
        self.path = path
        self.bucket, _ = self.__split_s3_path(path)
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        # build s3 client
        self.s3cli = self.__build_s3_cli()

    def remove_tree(self, s3_path: str) -> bool:
        bucket, obj_key = self.__split_s3_path(s3_path)
        r = self.s3cli.delete_object(Bucket=self.bucket, Key=obj_key)
        return r.status == 200

    def __build_s3_cli(self):
        session = Session(self.access_key, self.secret_key)
        s3_client = session.client("s3",
                                   endpoint_url=self.endpoint,
                                   use_ssl=False)
        return s3_client

    def __split_s3_path(self, s3_path: str) -> Tuple[str, str]:
        s3_path_pattern = re.compile("^s3://([^/]+)(?:/(.*))?$")
        m = s3_path_pattern.match(s3_path)
        if m is None:
            return "", ""
        return m.group(1), (m.group(2) or "")


class SftpStorage(Storage):

    def remove_tree(self, path: str) -> bool:
        raise NotImplementedError

    def __init__(self):
        raise NotImplementedError


class StorageBuilder(object):

    @staticmethod
    def build_by_name(storage_name: str, config: Dict) -> Storage:
        """
        Build storage client by name
        Args:
            storage_name:
            config:

        Returns:

        """

        if "storage" in config.keys():
            storage_config = config['storage'].get(storage_name, None)
            if storage_config is not None:
                path = storage_config.get('path', None)
                if path is not None:
                    if path.startswith('s3://'):
                        endpoint = storage_config.get('endpoint', None)
                        access_key = storage_config.get('access_key', None)
                        secret_key = storage_config.get('secret_key', None)
                        return S3Storage(path, endpoint, access_key,
                                         secret_key)
                    elif path.startswith('sftp://'):
                        return SftpStorage()
                    else:
                        return LocalDiskStorage()
                else:
                    raise Exception('storage config error')
            else:
                raise Exception("Storage config not found")
        else:
            raise Exception("Storage config not found")
