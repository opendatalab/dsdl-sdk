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
    QUERY_SYNTAX_ERROR = 9  # 查询数据集时的语法报错
    DATASET_PARAM_NOT_EXIST = 10  # 缺少dataset name参数
    SPLIT_NOT_EXIST = 11  # split在本地和远端都不存在
    DATASET_NOT_EXIST_REMOTE = 12  # dataset在远端都不存在
    SQLITE_OPERATION_ERROR = 13  # sqlite操作报错
    DATASET_NOT_EXIST = 14  # dataset在本地和远端都不存在
    DISK_SPACE_NOT_ENOUGH = 15  # 磁盘空间不足
    NO_DATASET_LOCAL = 16 # 本地没有数据集
    VIEW_TASK_TYPE_ERROR = 17 # 不支持的任务类型


class CLIException(Exception):
    """Base exception for all exceptions in this module."""

    def __init__(self, errcode: ExistCode, message: str):
        self.message = message
        self.errcode = int(errcode.value)
