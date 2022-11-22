"""
一个命令的实现例子

Examples:
    $python cli.py rm  -y  openmmlab/flying3d

"""

from commands.cmdbase import CmdBase
from utils.admin import DBClient


class Rm(CmdBase):
    """
    Example command
    """

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        example_parser = subparsers.add_parser(
            'rm',
            help='Remove dataset in a desired manner',
            example="example.example"
        )  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个
        example_parser.add_argument("-y",
                                    '--yes',
                                    default=False,
                                    help='remove without confirmation',
                                    action="store_true")
        example_parser.add_argument('--storage',
                                    default='default',
                                    type=str,
                                    help='local storage name')
        example_parser.add_argument("dataset_name",
                                    type=str,
                                    help='dataset name')
        return example_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """
        yes = cmdargs.yes
        storage_name = cmdargs.storage
        dataset_name = cmdargs.dataset_name
        self.__process_dataset_del(dataset_name,
                                   storage_name,
                                   force_delete=yes)

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
            print("Dataset `{}` does not exist locally".format(dataset_name))
        else:  # 存在，那么就删除
            if force_delete:
                self.__delete_dataset(dataset_name, storage_name)
            else:
                print("Are you sure to delete dataset {}? [y/n]".format(
                    dataset_name))
                answer = input()
                if answer == "y":
                    self.__delete_dataset(dataset_path, storage_name)
                    dbcli.delete_dataset(dataset_name)
                else:
                    print("Delete cancelled")

    def __delete_dataset(self, dataset_path: str, storage_name: str) -> None:
        """
        TODO delete dataset from local storage
        Args:
            dataset_path:
            storage_name:

        Returns:

        """
        storage_cli = self.__get_storage_cli_by_name(storage_name)
        storage_cli.delete(dataset_path)  # TODO

    def __get_storage_cli_by_name(self, storage_name):
        """
        Get storage client by name
        TODO
        Args:
            storage_name:

        Returns:

        """
        pass
