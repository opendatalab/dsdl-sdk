from abc import ABC
from typing import Any


class Storage(ABC):

    def __init__(self):
        pass


def LocalDiskStorage(Storage):
    pass


def S3Storage(Storage):
    pass


def SftpStorage(Storage):
    pass


class StorageBuilder(object):

    def build_by_name(self, storage_name: str, config: Any) -> Storage:
        """
        Build storage client by name
        Args:
            storage_name:
            config:

        Returns:

        """
        pass
