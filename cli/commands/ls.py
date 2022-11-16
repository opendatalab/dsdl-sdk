"""

ls function

Examples:
    $python cli.py ls
    >> show all the available datasets and its storage path
        1    flying3D            100GB    d:/mydata
        2    coco                100MB    s3://mybucket/coco
        3    imageNet            1TB      d:/mydata/twitter

"""
from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from tabulate import tabulate
from utils import admin


class Ls(CmdBase):
    """Show all the available datasets and its storage path.

    Args:
        CmdBase (_type_): _description_
    """
    def init_parser(self, subparsers):
        """_summary_

        Args:
            subparsers (_type_): _description_
        """
        
        status_parser = subparsers.add_parser('ls', help = 'Show available datasets')
        
        return status_parser
    
    def get_dataset_df(self):
        sql = 'select * from dataset'
        dataset = admin.get_sqlite_dict_list(sql,admin.get_sqlite_table_header('dataset'))
        return dataset
    
    def cmd_entry(self, cmdargs, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        dataset = self.get_dataset_df()
        print(tabulate(dataset, headers='keys', tablefmt='psql'))
