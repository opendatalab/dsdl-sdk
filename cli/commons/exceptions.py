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
    DATASET_PATH_NOT_EXISTS = (
        5  # 虽然数据库里能找到数据集名字，但是路径不存在。比如路径不在默认路径下，需要在删除时候指定 --storage, 否则只会到default路径下
    )
    VIEW_FROM_INSPECT_FAILED = 6  # 从inspect命令中中查看数据集失败
    VIEW_LOCAL_DATASET_FAILED = 7  # 从本地查看数据集失败
    VIEW_REMOTE_DATASET_FAILED = 8  # 从远程查看数据集失败


class CLIException(Exception):
    """Base exception for all exceptions in this module."""

    def __init__(self, errcode: ExistCode, message: str):
        self.message = message
        self.errcode = int(errcode.value)
