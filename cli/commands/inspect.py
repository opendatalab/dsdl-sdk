"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""
import os

from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from tabulate import tabulate
from utils import admin, query, plot


class Inspect(CmdBase):
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
        inspect_parser = subparsers.add_parser('inspect', help='Inspect dataset info',
                                               example="inspect.example",
                                               description='Inspect dataset info', )  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个

        inspect_parser.add_argument("dataset_name", action=EnvDefaultVar, envvar=DSDL_CLI_DATASET_NAME,
                                    type=str,
                                    help='Dataset name. The arg is optional only when the default dataset name was set by cd command.',
                                    metavar='')

        group = inspect_parser.add_mutually_exclusive_group()

        group.add_argument("-d", "--description", action="store_true",
                           help='The split name of the dataset, such as train/test/unlabeled or user self-defined split.',
                           )
        group.add_argument("-s", "--statistics", action="store_true",
                           help='Some statistics of the dataset.',
                           )

        return inspect_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """

        dataset_name = cmdargs.dataset_name
        description = cmdargs.description
        statistics = cmdargs.statistics

        dataset_dict = query.get_dataset_info(dataset_name)

        if description:
            print("dataset description".center(100, "="))
            print(dataset_dict['dsdl_meta']['dataset']['meta']['description'])

        if statistics:
            print("dataset statistics".center(100, "="))
            print("# " + "basic indicators")
            print(tabulate([dataset_dict['statistics']['dataset_stat']], headers='keys', tablefmt='plain'))

            plot_list = dataset_dict['statistics']['plots']

            for p in plot_list:
                if p['type'] == 'bar':
                    name = p['name']
                    labels = p['data']['x_data']
                    y_data = p['data']['y_data']
                    data = list(zip(*[x['data'] for x in y_data]))
                    y_categories = [x['name'] for x in y_data]
                    y_colors = [x['color'] for x in y_data]
                    y_label = p['data']['y_label']
                    plot.plt_cli_bar(name, labels, data, y_categories, y_colors, y_label)
