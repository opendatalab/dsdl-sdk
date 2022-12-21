"""

cd function

Examples:
    $python cli.py studio coco
    Collecting usage statistics. To deactivate, set browser.gatherUsageStats to False.
    You can now view your Streamlit app in your browser.
    Network URL: http://127.0.0.1:8501
    External URL: http://?.?.?.?:8501
"""

import sys

from utils.views.view import View
from commands.cmdbase import CmdBase
from commons.exceptions import CLIException, ExistCode
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
        studio_parser.add_argument(
            "-t",
            "--task",
            required=False,
            choices=["detection", "classification", "semantic-seg", "panoptic-seg"],
            help="task type [detection, classification, semantic-seg, panoptic-seg] of the dataset. ",
            metavar="[TASK TYPE]",
        )
        studio_parser.add_argument(
            "-n",
            "--number",
            required=False,
            type=int,
            help="number of images want to be viewed of the dataset.",
        )

        studio_parser_group = studio_parser.add_mutually_exclusive_group()

        studio_parser_group.add_argument(
            "-l",
            "--local",
            action="store_true",
            default=True,
            help="view local [ default ] dataset.",
        )
        studio_parser_group.add_argument(
            "-r",
            "--remote",
            action="store_true",
            default=False,
            help="view remote dataset.",
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
        task_type_name = cmdargs.task
        number = cmdargs.number
        local = cmdargs.local
        remote = cmdargs.remote

        dbcli = DBClient()
        local_exists = dbcli.is_dataset_local_exist(dataset_name)

        # TODO support remote dataset exists or not in the future:
        # remote_exists = dbcli.is_dataset_remote_exist(dataset_name)

        if task_type_name is None:
            # view = View(dataset_name, task=False)
            dataset_info = dbcli.get_dataset_info_by_name(dataset_name)
            if dataset_info is not None:
                task_type_name = dataset_info["task_type"]
                task_type_name_map = {
                    "ObjectDetection": "detection",
                    "Image Classification": "classification",
                    # "semantic-seg": "Segmentation", # TODO?
                    # "panoptic-seg": "Segmentation",
                }
                task_type_name = task_type_name_map[task_type_name]

            else:
                pass # TODO raise?

        if task_type_name not in [
            "detection",
            "classification",
            "semantic-seg",
            "panoptic-seg",
        ]:
            raise CLIException(
                ExistCode.VIEW_TASK_TYPE_ERROR,
                f"Task type {task_type_name} is not supported.",
            )
        else:
            view = View(
                dataset_name,
                task=True,
                task_type=task_type_name,
                number=number,
            )

        # print(f"local:{local}")
        # print(f"remote:{str(remote)}")
        # print(f"local_exists: {local_exists}")

        if remote is True:
            if local_exists is True:
                use_local = input(
                    f"Dataset {dataset_name} already exists on local.\nDo you want view using local dataset:(y/n)?"
                )
                if use_local in ["y", "Y", "yes", "Yes"]:
                    view.view_local_dataset()
                elif use_local in ["n", "N", "no", "No"]:
                    stdio.print_stdout(msg="Visualization terminated.")
                    sys.exit(0)
            else:
                stdio.print_stderr(
                    "Dataset not exists on local,try view remote dataset."
                )
                view.view_remote_dataset()
        elif local is True:
            if local_exists is True:
                view.view_local_dataset()
            else:
                stdio.print_stderr(f"Dataset {dataset_name} is not exists on local.")
