"""

cd function

Examples:
    $python cli.py studio --datasetname coco
    >> now you can open the dataset viewer on localhost:9192:
"""

import os
from pathlib import Path

import utils.views as views
from commands.cmdbase import CmdBase
from commons.argument_parser import EnvDefaultVar


class Studio(CmdBase):
    """
    cd command
    """

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        status_parser = subparsers.add_parser('studio', help='view the specified dataset on webpage.')
        status_parser.add_argument("-s", '--show', nargs='?', default='SHOW', help='show example', metavar='METAVAR')
        status_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar="DSDL_CLI_DATASET_NAME",
            nargs=1,
            type=str,
            help='dataset name',
            metavar='[dataset name]',
        )
        return status_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """

        dataset_view_dir_name = cmdargs.dataset_name[0]
        dataset_view_filepath = ".".join([cmdargs.dataset_name[0], 'py'])

        for dir in Path(views.__path__[0]).iterdir():
            if dataset_view_dir_name == dir.name:
                print(f"streamlit view directory {dataset_view_dir_name} found.")
                for file in dir.iterdir():
                    if dataset_view_filepath == file.name:
                        print(f"streamlit view file {dataset_view_filepath} found.")
                        streamlit_cmd = f"streamlit run {dir}/{dataset_view_filepath}"
                        os.system(streamlit_cmd)
                        break
