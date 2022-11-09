"""

References:
    https://developer.aliyun.com/article/740160
    https://docs.python.org/zh-cn/3/library/argparse.html
"""
import argparse
import os.path
import sys
from commands.cmdbase import CmdBase
import importlib
import inspect
from pathlib import Path
from commands.__version__ import __version__

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DSDLClient(object):
    """
    DSDL 命令行客户端
    """

    def __init__(self):
        """
        初始化命令行客户端
        """
        self.__config = self.__init_cli_config()
        self.__parser = argparse.ArgumentParser(prog='dsdl')
        self.__subparsers = self.__parser.add_subparsers(
            title='These are common DSDL commands used in various situations',
            metavar='command')
        self.__init_subcommand_parser()

        self.__init_global_flags() # 初始化全局参数
        self.__args = self.__parser.parse_args()

    def execute(self):
        """
        执行命令
        Returns:

        """
        if hasattr(self.__args, 'command_handler'):
            self.__args.command_handler(self.__args, self.__config)
        else:
            self.__parser.print_help()

    def __init_cli_config(self):
        """
        TODO 初始化命令行配置

        Returns:

        """
        return None

    def __init_global_flags(self):
        """
        初始化默认参数
        Returns:

        """
        self.__parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    def __init_subcommand_parser(self):
        """
        此处初始化子命令解析器。

        过程是扫描commands目录里集成了CmdBase的子类，然后
        Args:
            subcommand:
            help:

        Returns:

        """
        import commands
        pkgs = [module.stem for module in Path(commands.__path__[0]).iterdir() if module.is_file() and module.suffix == '.py' and not module.name.startswith('_')]  # 获取commands目录下的所有py文件
        for pkg in pkgs:
            module = importlib.import_module(f'commands.{pkg}')
            for clz_name, clz_obj in inspect.getmembers(module):
                if inspect.isclass(clz_obj) and issubclass(clz_obj, CmdBase) and not inspect.isabstract(clz_obj):
                    cmd_clz = clz_obj()
                    subcmd_parser = cmd_clz.init_parser(self.__subparsers)
                    subcmd_parser.set_defaults(command_handler=cmd_clz.cmd_entry)


if __name__ == '__main__':
    DSDLClient().execute()
