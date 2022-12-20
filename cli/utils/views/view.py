import os
import signal
import sys
from pathlib import Path
from subprocess import Popen

from loguru import logger

import commons.stdio as stdio
from commons.exceptions import CLIException, ExistCode


class View:
    original_sigint = signal.getsignal(signal.SIGINT)

    def __init__(
        self,
        dataset_name: str = None,
        task: bool = False,
        task_type: str = None,
        info: bool = False,
        number: int = 500,
    ):
        self.dataset_name = dataset_name
        self.task = task
        self.task_type = task_type
        self.info = info
        self.number = number

        if info is True:  # case 'odl-cli info --dataset-name ?? --preview' command
            self.dataset_name = dataset_name
        elif info is False:  # case 'odl-cli studio --dataset-name ?? ...' command
            if (
                task is True
            ):  # case: 'odl-cli studio --dataset-name ?? --task ?? --number ??' command
                self.dataset_name = dataset_name
                self.task_type = task_type
                self.number = number
            else:  # case: 'odl-cli studio dataset_name' command
                self.dataset_name = dataset_name.lower()

        self.view_base_dir = Path(os.path.dirname(__file__))
        self.view_code_name = ".".join([self.dataset_name, "py"])
        self.view_code_abspath = Path.joinpath(
            self.view_base_dir, self.dataset_name, self.view_code_name
        )

    def view_local_dataset(self):
        """
        view the local dataset on webpage.

        returns:
            dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} visulization..."
        )
        viewed = False
        if self.task is True:
            self.view_local_dataset_with_task_type(
                self.dataset_name, self.task_type, self.number
            )
        else:
            self.view_local_dataset_without_task_type(self.dataset_name)

    def view_local_dataset_with_task_type(self, dataset_name, task_type, number):
        """
        view the general dataset on webpage.

        args:
            dataset_name: dataset name.
            task_type: task type name.
            number: number of samples to be viewed.
        returns:
            dataset visualization webpage url.
        """
        viewed = False
        signal.signal(signal.SIGINT, self.ctrl_c_handler)

        view_code_name = "general_app.py"
        view_base_dir = Path(os.path.dirname(__file__))
        view_code_abspath = Path.joinpath(view_base_dir, view_code_name)
        streamlit_cmd = f"streamlit run {view_code_abspath} -- --dataset-name {dataset_name} --task-type {task_type} --number={number}"
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

    def view_local_dataset_without_task_type(self, dataset_name):
        """
        view the local dataset on webpage.

        args:
            dataset_name: dataset name.
        returns:
            dataset visualization webpage url.
        """
        viewed = False
        signal.signal(signal.SIGINT, self.ctrl_c_handler)
        for dir_name in self.view_base_dir.iterdir():
            if os.path.isdir(dir_name) and dir_name.name == dataset_name:
                for file in dir_name.iterdir():
                    if os.path.exists(self.view_code_abspath):
                        viewed = True
                        stdio.print_stdout(
                            f"Code for Dataset:{dataset_name} visualization has been found."
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
                            "Visulization of Dataset:{dataset_name} is to be supported in the future.",
                        )
            else:
                continue

        if viewed is False:
            stdio.print_stdout(
                f"Code for Dataset:{dataset_name} visualization has not been found, to be done."
            )

    def view_remote_dataset(self):
        """
        view the remote dataset on webpage.

        returns:
            dataset visualization webpage url.
        """
        stdio.print_stderr(
            f"[ TO BE DONE ] Remote dataset {self.dataset_name} visualization.\n Bye..."
        )

    def view_from_info(self, split_name):
        """
        view the files which get from inspect command on webpage.

        returns:
            dataset visualization webpage url.
        """
        stdio.print_stdout(
            f"Processing local dataset {self.dataset_name} inspect visulization..."
        )

        viewed = False
        signal.signal(signal.SIGINT, self.ctrl_c_handler)

        view_code_name = "view_from_info.py"
        view_base_dir = Path(os.path.dirname(__file__))
        view_code_abspath = Path.joinpath(view_base_dir, view_code_name)
        streamlit_cmd = f"streamlit run {view_code_abspath} -- --dataset-name {self.dataset_name} --split-name {split_name}"
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

    def ctrl_c_handler(self, signum, frame):
        signal.signal(signal.SIGINT, self.original_sigint)
        stdio.print_stderr("View cancelled")
        logger.exception("View cancelled")
        sys.exit(0)
