"""

cd function

Examples:
    $python cli.py studio coco
    Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.
    You can now view your Streamlit app in your browser.
    Network URL: http://127.0.0.1:8501
    External URL: http://?.?.?.?:8501
"""


from utils.views.view import View
from commands.cmdbase import CmdBase
from commons.argument_parser import EnvDefaultVar
from utils.admin import DBClient
from commands.const import (
    DEFAULT_CLI_CONFIG_FILE,
    DEFAULT_CLI_LOG_FILE_PATH,
    DEFAULT_CONFIG_DIR,
    DEFAULT_LOCAL_STORAGE_PATH,
    PROG_NAME,
    SQLITE_DB_PATH,
)

import commons.stdio as stdio


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
        studio_parser = subparsers.add_parser(
            "studio",
            help="view the specified dataset on webpage.",
            example="studio.example",
        )

        studio_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar="DSDL_CLI_DATASET_NAME",
            type=str,
            help="dataset name",
            metavar="[DATASET NAME]",
        )

        studio_parser_group = studio_parser.add_mutually_exclusive_group()

        studio_parser_group.add_argument(
            "-l",
            "--local",
            nargs="?",
            default="True",
            const="True",
            type=bool,
            help="view local[default] dataset.",
            metavar="SET to True to VIEW LOCAL DATASET",
        )
        studio_parser_group.add_argument(
            "-r",
            "--remote",
            nargs="?",
            default="False",
            const="False",
            type=bool,
            help="view remote[when explicitly specified to true] dataset.",
            metavar="SET to True(default false) to VIEW REMOTE DATASET",
        )
        return studio_parser

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
        local = cmdargs.local
        remote = cmdargs.remote

        dbcli = DBClient()
        local_exists = dbcli.is_dataset_local_exist(dataset_name)

        # TODO support remote dataset exists or not in the future:
        # remote_exists = dbcli.is_dataset_remote_exist(dataset_name)

        view = View(dataset_name)

        # print(f"local:{local}")
        # print(f"remote:{str(remote)}")
        # print(f"exists on localhost: {local_exists}")

        if remote is True:
            if local_exists is True:
                use_local = input(
                    f"Dataset {dataset_name} already exists on local.\nDo you want view using local dataset:(y/n)?"
                )
                if use_local in ["y", "Y", "yes", "Yes"]:
                    view.view_local_dataset()
                elif use_local in ["n", "N", "no", "No"]:
                    view.view_remote_dataset()
            else:
                view.view_remote_dataset()
        elif local is True:
            if local_exists is True:
                view.view_local_dataset()
            else:
                stdio.print_stderr(f"Dataset {dataset_name} is not exists on local.")
