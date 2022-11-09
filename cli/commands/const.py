import os

DSDL_CLI_DATASET_NAME = "DSDL_CLI_DATASET_NAME" # cd命令设置的环境变量的数据集名称

DEFAULT_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".dsdl") # 默认配置目录,放在用户的家目录下的.dsdl目录

__SQLITE_DB_NAME = "dsdl_cli.db" # sqlite数据库文件

SQLITE_DB_PATH = os.path.join(DEFAULT_CONFIG_DIR, __SQLITE_DB_NAME) # sqlite数据库文件路径