"""
一个命令的实现例子

Examples:
    $python cli.py rm  -y  openmmlab/flying3d

"""

from commands.cmdbase import CmdBase
from commons.stdio import print_stdout


class Search(CmdBase):

    def __init__(self):
        super().__init__()
        self.__config = None

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        search_parser = subparsers.add_parser(
            'search',
            help='search dataset in a desired manner',
        )  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个

        return search_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:
        old data:
        CIFAR-10-Auto                   21M
        CIFAR-10                        241M
        CIFAR-100                       243M
        Fashion-MNIST                   281M
        STL-10                          2.1G
        """
        print_stdout("""
PascalVOC2007-detection         835M
PascalVOC2012-detection         2.4G
CIFAR10                         129M
Oxford_102_Flowers              331M
PascalVOC2012-segmentation      487M
PascalVOC2007-segmentation      58M
MPII                            11.3G
COCO2017Keypoints               10.2G
""")
