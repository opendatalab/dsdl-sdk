import os
import sys
from pathlib import Path
import signal
from subprocess import Popen, PIPE
import asyncio


import commons.stdio as stdio
from commons.exceptions import CLIException, ExistCode
from loguru import logger


class View:
    original_sigint = signal.getsignal(signal.SIGINT)

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

    def view_from_inspect(self, split_name):
        """
        view the files which get from inspect command on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} inspect visulization..."
        )

        viewed = False
        signal.signal(signal.SIGINT, self.ctrl_c_handler)

        view_base_dir = Path(os.path.dirname(__file__))
        view_code_name = "view_from_inspect.py"
        view_code_abspath = Path.joinpath(view_base_dir, view_code_name)
        streamlit_cmd = (
            f"streamlit run {view_code_abspath} -- --dataset-name {self.dataset_name} --split-name {split_name}"
        )
        try:
            process = Popen(
                streamlit_cmd,
                shell=True,
            ).wait()
        except KeyboardInterrupt:
            process.send_signal(signal.SIGINT)
            process.wait()
        except CLIException as e:
            stdio.print_stderr(e.message)
            logger.exception(e.message)
            raise CLIException(ExistCode.VIEW_FROM_INSPECT_FAILED, str(e))

        if viewed is False:
            stdio.print_stdout(
                f"Code for Dataset:{self.dataset_name} visualization has not been found, to be done."
            )

    def view_local_dataset(self):
        """
        view the local dataset on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} visulization..."
        )
        viewed = False
        signal.signal(signal.SIGINT, self.ctrl_c_handler)
        for dir_name in self.view_base_dir.iterdir():
            if os.path.isdir(dir_name) and dir_name.name == self.dataset_name:
                for file in dir_name.iterdir():
                    if os.path.exists(self.view_code_abspath):
                        viewed = True
                        stdio.print_stdout(
                            f"Code for Dataset:{self.dataset_name} visualization has been found."
                        )
                        streamlit_cmd = f"streamlit run {self.view_code_abspath}"
                        try:
                            process = Popen(
                                streamlit_cmd,
                                shell=True,
                            ).wait()
                        except KeyboardInterrupt:
                            process.send_signal(signal.SIGINT)
                            process.wait()
                        except CLIException as e:
                            stdio.print_stderr(e.message)
                            logger.exception(e.message)
                            raise CLIException(
                                ExistCode.VIEW_FROM_INSPECT_FAILED, str(e)
                            )
                        break
                    else:
                        raise CLIException(
                            ExistCode.VIEW_LOCAL_DATASET_FAILED,
                            "Visulization of Dataset:{self.dataset_name} is to be supported in the future.",
                        )
            else:
                continue

        if viewed is False:
            stdio.print_stdout(
                f"Code for Dataset:{self.dataset_name} visualization has not been found, to be done."
            )

    def view_remote_dataset(self):
        """
        view the remote dataset on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stderr(
            f"[ TO BE DONE ] Remote dataset {self.dataset_name} visualization.\n Bye..."
        )

    def ctrl_c_handler(self, signum, frame):
        signal.signal(signal.SIGINT, self.original_sigint)
        stdio.print_stderr("View cancelled")
        logger.exception("View cancelled")
        sys.exit(0)

        # if input("\nReally quit? (y/n)> ").lower().startswith("y"):
        #     stdio.print_stderr("View cancelled")
        #     logger.exception("View cancelled")
        #     sys.exit(1)
        # try:
        #     if input("\nReally quit? (y/n)> ").lower().startswith("y"):
        #         stdio.print_stderr("View cancelled")
        #         logger.exception("View cancelled")
        #         sys.exit(1)
        # except KeyboardInterrupt:
        #     sys.exit(1)
