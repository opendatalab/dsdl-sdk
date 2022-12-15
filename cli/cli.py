"""

References:
    https://developer.aliyun.com/article/740160
    https://docs.python.org/zh-cn/3/library/argparse.html
"""

import importlib
import inspect
import json
import os.path
import sys
from pathlib import Path
from typing import Any

from loguru import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from commands.__init__ import __version__
from commands.cmdbase import CmdBase
from commands.const import (
    DEFAULT_CLI_CONFIG_FILE,
    DEFAULT_CLI_LOG_FILE_PATH,
    DEFAULT_CONFIG_DIR,
    DEFAULT_LOCAL_STORAGE_PATH,
    PROG_NAME,
    SQLITE_DB_PATH,
)
from commons.argument_parser import CustomHelpFormatter
from commons.argument_parser import DsdlArgumentParser as ArgumentParser
from commons.loghandler import setup_loger
from commons.stdio import print_stderr
from utils.admin import initialize_db

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DSDLClient(object):
    """
    DSDL 命令行客户端
    """

    def __init__(self) -> None:
        """
        初始化命令行客户端
        """
        self.__config = self.__init_cli_config()
        self.__parser = ArgumentParser(
            prog=PROG_NAME,
            description="""
            Use '%(prog)s <command>' to access/load datasets either from local
            file system or remote cloud storage, can also perform data-preprocessing
            including filtering, visualization, etc.""",
            epilog=
            "Report bugs to https://github.com/opendatalab/dsdl-sdk/issues",
            usage=
            f"{PROG_NAME} GLOBAL_FLAGS | COMMAND [COMMAND_ARGS] [DATASET_NAME]\n",
            formatter_class=CustomHelpFormatter,
        )
        self.__subparsers = self.__parser.add_subparsers(title="Commands", )
        self.__init_subcommand_parser()

        self.__init_global_flags()  # 初始化全局参数
        self.__args = self.__parser.parse_args()

    def execute(self):
        """
        执行命令
        Returns:

        """
        if hasattr(self.__args, "command_handler"):
            self.__args.command_handler(self.__args, self.__config)
        else:
            self.__parser.print_usage()

    def __init_cli_config(self) -> Any:
        """

        Returns:

        """
        # 检查配置文件是否存在，如果没有则创建一个
        # 检查sqlite数据库是否存在，如果没有则创建一个
        # 检查sqlite数据库是否有表，如果没有则创建表
        if os.path.exists(DEFAULT_CONFIG_DIR) is False:  # 配置目录
            os.makedirs(DEFAULT_CONFIG_DIR)
        if os.path.exists(DEFAULT_CLI_LOG_FILE_PATH) is False:
            os.makedirs(DEFAULT_CLI_LOG_FILE_PATH)
        if os.path.exists(SQLITE_DB_PATH) is False:  # sqlite数据库,并初始化table
            initialize_db(SQLITE_DB_PATH)
        if os.path.exists(DEFAULT_CLI_CONFIG_FILE) is False:  # 默认配置文件
            with open(DEFAULT_CLI_CONFIG_FILE, 'w') as f:
                with open(
                        os.path.join(os.path.dirname(__file__),
                                     'resources/default_cli_cfg.json'),
                        'r') as f2:
                    x = json.loads(f2.read())
                    x["storage"]['default'][
                        'path'] = DEFAULT_LOCAL_STORAGE_PATH
                    f.write(json.dumps(x, ensure_ascii=False, indent=4))
        if os.path.exists(DEFAULT_LOCAL_STORAGE_PATH) is False:  # 默认存放数据的目录
            os.makedirs(DEFAULT_LOCAL_STORAGE_PATH)

        #########################################################
        # todo 以上正确做法是放在pip install的时候，自定义一个安装脚本，目前先简单做,加快命令速度
        #########################################################

        # 接下来读取配置文件，然后返回成一个json对象
        with open(DEFAULT_CLI_CONFIG_FILE, "r") as f:
            return json.loads(f.read())

    def __init_global_flags(self):
        """
        初始化默认参数
        Returns: None

        """
        self.__parser._optionals.title = "Global flags"
        self.__parser.add_argument(
            "-v",
            "--version",
            action="version",
            version=f"%(prog)s {__version__}",
            help="show the %(prog)s version and exit.",
        )

    def __init_subcommand_parser(self) -> None:
        """
        此处初始化子命令解析器。

        过程是扫描commands目录里集成了CmdBase的子类，然后
        Args:
            subcommand:
            help:

        Returns:

        """
        import commands

        pkgs = [
            module.stem for module in Path(commands.__path__[0]).iterdir()
            if module.is_file() and module.suffix == '.py'
            and not module.name.startswith('_')
        ]  # 获取commands目录下的所有py文件
        for pkg in pkgs:  # TODO 这里的性能是硬性最大的地方，可以通过缓存或者打包的时候预定义方式优化
            module = importlib.import_module(f'commands.{pkg}')
            for clz_name, clz_obj in inspect.getmembers(module):
                if inspect.isclass(clz_obj) and issubclass(
                        clz_obj, CmdBase) and not inspect.isabstract(clz_obj):
                    cmd_clz = clz_obj()
                    subcmd_parser = cmd_clz.setup_parser(self.__subparsers)
                    subcmd_parser.set_defaults(
                        command_handler=cmd_clz.cmd_main)
                    subcmd_parser._optionals.title = "Command args"
                    subcmd_parser._positionals.title = "Positional arguments"
                    subcmd_parser.formatter_class = CustomHelpFormatter


def main():
    setup_loger()
    logger.remove(0)
    try:
        DSDLClient().execute()
    except KeyboardInterrupt as e:
        print_stderr("\nkeyboard interrupted, exit")
        exit(-1)
    except Exception as e:
        logger.exception(e)
        print_stderr("unknown error, please see log files at ~/.dsdl/logs")
        exit(-1)


if __name__ == "__main__":
    setup_loger()
    DSDLClient().execute()
