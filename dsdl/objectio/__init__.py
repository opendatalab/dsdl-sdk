from .local import LocalFileReader
from .ali_oss import AliOSSFileReader
from .base import BaseFileReader
from .ceph import CephFileReader, PetrelFileReader

__all__ = [
    "LocalFileReader",
    "AliOSSFileReader",
    "BaseFileReader",
    "CephFileReader",
    "PetrelFileReader",
]
