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
from commons.argument_parser import EnvDefaultVar

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
        
        config_parser = subparsers.add_parser('ls', help = 'Show available datasets')
        
        return config_parser
    
    def cmd_entry(self, cmdargs, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        print(cmdargs)
