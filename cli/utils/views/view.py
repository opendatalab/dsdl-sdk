import os
import sys
from pathlib import Path
import signal

import commons.stdio as stdio
from commons.exceptions import CLIException, ExistCode
from loguru import logger


class View:
    def __init__(self, dataset_name: str, inspect: bool = False):
        if inspect is True:
            self.dataset_name = dataset_name
        else:
            self.dataset_name = dataset_name.lower()
        self.view_base_dir = Path(os.path.dirname(__file__))
        self.view_code_name = ".".join([self.dataset_name, "py"])
        self.view_code_abspath = Path.joinpath(
            self.view_base_dir, self.dataset_name, self.view_code_name
        )

    def view_from_inspect(self):
        """
        view the files which get from inspect command on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} inspect visulization..."
        )

        view_base_dir = Path(os.path.dirname(__file__))
        view_code_name = "view_from_inspect.py"
        view_code_abspath = Path.joinpath(view_base_dir, view_code_name)
        streamlit_cmd = (
            f"streamlit run {view_code_abspath} -- --dataset-name {self.dataset_name}"
        )
        try:
            signal.signal(signal.SIGINT, self.ctrl_c_handler)
            os.system(streamlit_cmd)
        except CLIException as e:
            stdio.print_stderr(e.message)
            logger.exception(e.message)
            raise CLIException(ExistCode.VIEW_FROM_INSPECT_FAILED, str(e))

    def view_local_dataset(self):
        """
        view the local dataset on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} visulization..."
        )

        for dir_name in self.view_base_dir.iterdir():
            if os.path.isdir(dir_name) and dir_name.name == self.dataset_name:
                for file in dir_name.iterdir():
                    if os.path.exists(self.view_code_abspath):
                        stdio.print_stdout(
                            f"Code for Dataset:{self.dataset_name} visualization has been found."
                        )
                        streamlit_cmd = f"streamlit run {self.view_code_abspath}"
                        try:
                            signal.signal(signal.SIGINT, self.ctrl_c_handler)
                            os.system(streamlit_cmd)
                        except CLIException as e:
                            logger.exception(e.message)
                            stdio.print_stderr(e.message)
                            raise CLIException(
                                ExistCode.VIEW_LOCAL_DATASET_FAILED, str(e)
                            )
                        break
                    else:
                        raise CLIException(
                            ExistCode.VIEW_LOCAL_DATASET_FAILED,
                            "Visulization of Dataset:{self.dataset_name} is to be supported in the near future.",
                        )

    def view_remote_dataset(self):
        """
        view the remote dataset on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stderr(
            f"[ TO BE DONE ] Processing remote dataset {self.dataset_name} visulization.\n Bye..."
        )

    def ctrl_c_handler(self, signum, frame):
        response = input("Are you sure you want to exit? (y/n): ")
        if response == "y":
            stdio.print_stderr("View cancelled")
            logger.exception("View cancelled")
            sys.exit(0)
