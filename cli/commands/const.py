import os

DSDL_CLI_DATASET_NAME = "DATASET_NAME"  # cd命令设置的环境变量的数据集名称

DEFAULT_CONFIG_DIR = os.path.join(
    os.path.expanduser("~"), ".dsdl"
)  # 默认配置目录,放在用户的家目录下的.dsdl目录

__DEFAULT_CLI_CONFIG_FILE_NAME = "dsdl.json"  # 默认配置文件名称

DEFAULT_CLI_CONFIG_FILE = os.path.join(
    DEFAULT_CONFIG_DIR, __DEFAULT_CLI_CONFIG_FILE_NAME
)  # 默认配置文件路径

__SQLITE_DB_NAME = "dsdl_cli.db"  # sqlite数据库文件

SQLITE_DB_PATH = os.path.join(DEFAULT_CONFIG_DIR, __SQLITE_DB_NAME)  # sqlite数据库文件路径

PROG_NAME = "odl-cli"  # 程序名称

DEFAULT_LOCAL_STORAGE_PATH = os.path.join(DEFAULT_CONFIG_DIR, "datasets")  # 默认本地存储路径

DEFAULT_CLI_LOG_FILE_PATH = os.path.join(
    DEFAULT_CONFIG_DIR, "logs"
)  # default log file path

# 环境变量配置路径
_ENV_FILE_PATH = ".env"  # 默认环境变量文件名称
DEFAULT_ENV_FILE = os.path.join(DEFAULT_CONFIG_DIR, _ENV_FILE_PATH)  # 默认环境变量配置文件路径
