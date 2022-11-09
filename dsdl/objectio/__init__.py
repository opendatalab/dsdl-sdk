from .local import LocalFileReader
from .ali_oss import AliOSSFileReader
from .base import BaseFileReader

__all__ = [
    "LocalFileReader",
    "AliOSSFileReader",
    "BaseFileReader",
]
