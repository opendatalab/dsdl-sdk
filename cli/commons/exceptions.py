from enum import Enum


class ExistCode(Enum):
    """
    定义错误码
    """
    SUCCESS = 0
    NOT_SUPPORTED_STORE_PATH = 1
    STORAGE_NAME_NOT_EXIST = 2  # 有storage这个配置，但是没有storage_name这个配置
    STORAGE_NOT_EXIST = 3  # 没有storage这个配置
    DATASET_NOT_EXIST_LOCAL = 4  # 本地没有这个数据集


class CLIException(Exception):
    """Base exception for all exceptions in this module."""

    def __init__(self, errcode: ExistCode, message: str):
        self.message = message
        self.errcode = int(errcode.value)
