"""

cd function

Examples:
    $python cli.py studio --datasetname coco
    >> now you can open the dataset viewer on localhost:9192:
"""


from utils.views.view import View
from commands.cmdbase import CmdBase
from commons.argument_parser import EnvDefaultVar
from utils.admin import DBClient


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
        status_parser = subparsers.add_parser(
            "studio", help="view the specified dataset on webpage."
        )
        status_parser.add_argument(
            "-s",
            "--show",
            nargs="?",
            default="SHOW",
            help="show example",
            metavar="SHOW",
        )
        status_parser.add_argument(
            "-l",
            "--local",
            nargs="?",
            default="True",
            const="True",
            type=bool,
            help="view local[default] dataset.",
            metavar="SET to True to VIEW LOCAL DATASET",
        )
        status_parser.add_argument(
            "-r",
            "--remote",
            nargs="?",
            default="False",
            const="False",
            type=bool,
            help="view remote[when explicitly specified to true] dataset.",
            metavar="SET to True(default false) to VIEW REMOTE DATASET",
        )
        status_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar="DSDL_CLI_DATASET_NAME",
            nargs=1,
            type=str,
            help="dataset name",
            metavar="[DATASET NAME]",
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

        dataset_name = cmdargs.dataset_name[0]
        local = cmdargs.local
        remote = cmdargs.remote

        dbcli = DBClient()
        local_exists = dbcli.is_dataset_local_exist(dataset_name)

        # TODO support remote dataset exists or not in the future:
        # remote_exists = dbcli.is_dataset_remote_exist(dataset_name)

        view = View(dataset_name)

        print(f"local:{local}")
        print(f"remote:{str(remote)}")
        print(f"exists on localhost: {local_exists}")

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
                print(f"Dataset {dataset_name} is not exists on local.")
