"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""
from commands.cmdbase import CmdBase


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
        status_parser = subparsers.add_parser('example', help='Show the working tree status')
        status_parser.add_argument('--show', nargs='+', default='SHOW', help='show example')
        return status_parser

    def cmd_entry(self, args, config):
        """
        Entry point for the command

        Args:
            self:
            args:
            config:

        Returns:

        """
        print(args)
        print(f"{args.show}")
