import os
from pathlib import Path

import commons.stdio as stdio


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
        # print("::: ", streamlit_cmd)
        try:
            os.system(streamlit_cmd)
        except Exception as e:
            print(e)

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
                        stdio.print_stderr(
                            f"Code for Dataset:{self.dataset_name} visualization has been found."
                        )
                        streamlit_cmd = f"streamlit run {self.view_code_abspath}"
                        try:
                            os.system(streamlit_cmd)
                        except Exception as e:
                            print(e)
                        break
                    else:
                        print(
                            "Visulization of Dataset:{self.dataset_name} is to be supported in the near future."
                        )

    def view_remote_dataset(self):
        """
        view the remote dataset on webpage.
        Returns: dataset visualization webpage url.
        """
        stdio.print_stderr(
            f"[ TO BE DONE ] Processing remote dataset {self.dataset_name} visulization.\n Bye..."
        )
