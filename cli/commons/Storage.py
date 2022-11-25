import shutil
from abc import ABC, abstractmethod
from typing import Any


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

    def remove_tree(self, s3_path: str) -> bool:
        raise NotImplementedError


class SftpStorage(Storage):

    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def remove_tree(self, path: str) -> bool:
        raise NotImplementedError


class StorageBuilder(object):

    @staticmethod
    def build_by_name(storage_name: str, config: Any) -> Storage:
        """
        Build storage client by name
        Args:
            storage_name:
            config:

        Returns:

        """
        # TODO 总是返回本地存储，改为根据storage_name，从config里取出配置，根据配置构建不同的存储
        return LocalDiskStorage()
