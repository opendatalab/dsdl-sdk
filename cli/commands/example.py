"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""

from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from commons.stdio import print_stdout


class Example(CmdBase):
    """
    Example command
    """

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        example_parser = subparsers.add_parser(
            'example',
            help='Show the working tree status',
            example="example.example"
        )  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个
        example_parser.add_argument("-s",
                                    '--show',
                                    nargs='?',
                                    default='SHOW',
                                    help='show example string.....',
                                    metavar='SS')
        example_parser.add_argument('--test1',
                                    nargs='?',
                                    default='x',
                                    help='show test1',
                                    metavar='a')
        example_parser.add_argument('--test-1234',
                                    nargs='?',
                                    default='t',
                                    help='show test-1234',
                                    metavar='c')
        example_parser.add_argument("dataset_name",
                                    action=EnvDefaultVar,
                                    envvar=DSDL_CLI_DATASET_NAME,
                                    nargs=1,
                                    type=str,
                                    help='dataset name',
                                    metavar='[dataset name]')
        return example_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """
        print_stdout(cmdargs)
        print_stdout(f"{cmdargs.show}")
        print_stdout(cmdargs.dataset_name)
