"""
一个命令的实现例子

Examples:
    $python cli.py rm  -y  openmmlab/flying3d

"""

from commands.cmdbase import CmdBase
from commons.exceptions import CLIException, ExistCode
from commons.stdio import print_stdout
from commons.storage_builder import StorageBuilder
from utils.admin import DBClient

from dsdlsdk.exception.exception import DatasetPathNotExists
from dsdlsdk.storage import Storage


class Rm(CmdBase):

    def __init__(self):
        super().__init__()
        self.__config = None

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        rm_parser = subparsers.add_parser(
            "rm",
            help="remove dataset in a desired manner",
            example="rm.example")  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个
        rm_parser.add_argument(
            "-y",
            "--yes",
            default=False,
            help="remove without confirmation",
            action="store_true",
        )
        rm_parser.add_argument("--storage",
                               default="default",
                               type=str,
                               help="local storage name")
        rm_parser.add_argument("dataset_name", type=str, help="dataset name")
        return rm_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """
        self.__config = config
        yes = cmdargs.yes
        storage_name = cmdargs.storage
        dataset_name = cmdargs.dataset_name
        try:
            self.__process_dataset_del(dataset_name,
                                       storage_name,
                                       force_delete=yes)
        except DatasetPathNotExists as e:
            raise CLIException(ExistCode.DATASET_PATH_NOT_EXISTS, str(e))

    def __process_dataset_del(self,
                              dataset_name,
                              storage_name,
                              force_delete=False) -> None:
        """
        Delete one dataset

        Args:
            dataset_name:
            storage: local storage name
            force_delete:

        Returns:

        """
        dbcli = DBClient()
        dataset_path = dbcli.get_local_dataset_path(dataset_name)
        # 先查找这个数据集是否存在本地
        if not dataset_path:
            raise CLIException(
                ExistCode.DATASET_NOT_EXIST_LOCAL,
                "Dataset `{}` does not exist locally".format(dataset_name),
            )
        else:  # 存在，那么就删除
            if force_delete:
                self.__delete_dataset(dataset_name, dataset_path, storage_name)
            else:
                print_stdout(
                    "Are you sure to delete dataset {}? [y/n]".format(
                        dataset_name),
                    end="",
                )
                answer = input()
                if answer == "y":
                    self.__delete_dataset(dataset_name, dataset_path,
                                          storage_name)
                    dbcli.delete_dataset(dataset_name)
                else:
                    print_stdout("Delete cancelled")

    def __delete_dataset(self, dataset_name: str, dataset_path: str,
                         storage_name: str) -> None:
        """
        delete dataset from  storage

        Args:
            dataset_path:
            storage_name:

        Returns:

        """
        dbcli = DBClient()
        storage_cli = self.__get_storage_cli_by_name(storage_name)
        if storage_cli.remove_tree(dataset_path):
            dbcli.delete_dataset(dataset_name)
            print_stdout("Dataset {} deleted".format(dataset_path))

    def __get_storage_cli_by_name(self, storage_name) -> Storage:
        """
        Get storage client by name

        Args:
            storage_name:

        Returns:

        """
        s: Storage = StorageBuilder.build_by_name(storage_name, self.__config)
        return s
