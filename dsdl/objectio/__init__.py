from .local import LocalFileReader
from .ali_oss import AliOSSFileReader
from .base import BaseFileReader
from .ceph import CephFileReader, PetrelFileReader
from .aws_oss import AwsOSSFileReader

__all__ = [
    "LocalFileReader",
    "AliOSSFileReader",
    "BaseFileReader",
    "CephFileReader",
    "PetrelFileReader",
    "AwsOSSFileReader",
]
