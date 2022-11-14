"""

cd function

Examples:
    $python cli.py cd --datasetname coco
    >> now in the Coco dataset context, you can use the following commands:
    >> inspect select studio search
"""
import os
import platform

from commands.cmdbase import CmdBase
from commons.argument_parser import EnvDefaultVar


class Cd(CmdBase):
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
        status_parser = subparsers.add_parser('cd', help='change the context to the specified dataset.')
        status_parser.add_argument("-s", '--show', nargs='?', default='SHOW', help='show example', metavar='METAVAR')
        status_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar="DSDL_CLI_DATASET_NAME",
            nargs=1,
            type=str,
            help='dataset name',
            metavar='[dataset name]',
        )
        return status_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """
        print("------------cmdargs----------------")
        print(f"\n {cmdargs} \n ")
        print("------------cmdargs----------------")

        os.environ.setdefault('DATASET_NAME', '')
        os.environ['DATASET_NAME'] = cmdargs.dataset_name[0]

        dsname = os.environ.get('DATASET_NAME', "default")
        print("\n DATASET_NAME : ", dsname)

        if 'DATASET_NAME' in os.environ:
            print(f"\n Dataset {dsname} exists")

        sysstr = platform.system()
        if sysstr == "Windows":
            print("Call Windows cmd command shell")
            os.system("\n C:\Windows\System32\cmd.exe")
        elif sysstr == "Linux":
            print("\n Call Linux bash command shell")
            os.system("/usr/bin/env bash ")
        else:
            print("\n Other System tasks")
