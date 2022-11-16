import json
import os

from rich.console import Console
from rich.syntax import Syntax
from tabulate import tabulate

from .cmdbase import CmdBase
from .const import DEFAULT_CLI_CONFIG_FILE, DEFAULT_CONFIG_DIR, DEFAULT_LOCAL_STORAGE_PATH, PROG_NAME, SQLITE_DB_PATH


class Config(CmdBase):
    """Set dsdl configuration {file path, user login info}.

    Args:
        CmdBase (_type_): _description_
    """
    def init_parser(self, subparsers):
        """_summary_

        _extended_summary_

        Args:
            subparsers (_type_): _description_
        """

        available_keys ='The available keys are:'
        config_parser = subparsers.add_parser('config', help='set dsdl configuration.', example='config.example')
        config_parser.add_argument('-k',
                                   '--keys',
                                   action='store_const',
                                   const=available_keys,
                                   help='show all the available keys',
                                   required=False)
        config_parser.add_argument('-s',
                                   '--setvalue',
                                   type=str,
                                   nargs=2,
                                   action='append',
                                   help='Set key-value for a specific configuration.')
        config_parser.add_argument('-l',
                                   '--list',
                                   help='show all key value pairs')
        config_parser.add_argument('-c',
                                   '--credentials',
                                   type=str,
                                   nargs=2,
                                   metavar = 'ak & sk')
        return config_parser

    def cmd_entry(self, args, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        # print(args)
        setvalue_list = args.setvalue
        credentials = args.credentials
        
        if args.keys is not None:
            key_str = args.keys
            # type(config) is dict
            snippet_keys = ''' 
                auth.username             # central repo username
                auth.password             # central repo password
                storage.name              # storage name
                storage.loc               # storage path
            '''
            syntax = Syntax(key_str+snippet_keys, 'pyhton')
            console = Console()
            console.print(syntax)
        
        # print(f"{args.setvalue}")
        # command handler
        

        #update user input of auth.xx & storage.xx
        if setvalue_list is not None:
            for idx, element in enumerate(setvalue_list):
                if element[0] == 'auth.username':
                    config['repo']['central']['user'] = element[1]
                elif element[0] == 'auth.password':
                    config['repo']['central']['passwd'] = element[1]
                elif element[0] == 'storage.name':
                    config['storage'][element[1]] = {}
                elif element[0] == 'storage.loc':
                    config['storage'][list(config['storage'].keys())[1]]['path'] = element[1]
        
        #update credentials
        # print(config['storage'].keys)
        if credentials is not None:
            # print(config['storage'].keys())
            config['storage'][list(config['storage'].keys())[1]]['ak'] = credentials[0]
            config['storage'][list(config['storage'].keys())[1]]['sk'] = credentials[1]
        
        with open(DEFAULT_CLI_CONFIG_FILE, 'w') as file:
            return json.dump(config,file, indent=4)
        # print(f"{args.__dict__}")
        # print(f"{args.credentials}")
        # FIX multiinput