import os
from pathlib import Path


class View:
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name.lower()
        self.view_base_dir = Path(os.path.dirname(__file__))
        self.view_code_name = ".".join([self.dataset_name, 'py'])
        self.view_code_abspath = Path.joinpath(self.view_base_dir, self.dataset_name, self.view_code_name)

    def view_local_dataset(self):
        """
        view the local dataset on webpage.
        Args:
            dataset_view_filepath:
        Returns: dataset visualization webpage url.
        """
        print(f"Processing local dataset {self.dataset_name} visulization...")

        for dir_name in self.view_base_dir.iterdir():
            if os.path.isdir(dir_name) and dir_name.name == self.dataset_name:
                for file in dir_name.iterdir():
                    if os.path.exists(self.view_code_abspath):
                        print(f"Code for Dataset:{self.dataset_name} visualization has been found.")
                        streamlit_cmd = f"streamlit run {self.view_code_abspath}"
                        try:
                            os.system(streamlit_cmd)
                        except Exception as e:
                            print(e)
                        break
                    else:
                        print("Visulization of Dataset:{self.dataset_name} is to be supported in the near future.")

    def view_remote_dataset(self):
        """
        view the remote dataset on webpage.
        Args:
            dataset_view_filepath:
        Returns: dataset visualization webpage url.
        """
        print(f"[ TO BE DONE ] Processing remote dataset {self.dataset_name} visulization.\n Bye...")