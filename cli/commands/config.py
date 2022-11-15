import json
import os

from .cmdbase import CmdBase
from .const import DEFAULT_CONFIG_DIR


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

        available_keys ='''
        The available keys are:
            auth.username             # central repo username
            auth.password             # central repo password
            storage.name              # storage name
            storage.loc               # storage path
        '''
        config_parser = subparsers.add_parser('config', help='set dsdl configuration.', example="dsdl config -s auth.username  admin",)
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
        # print(f"{args.keys}")
        
        # print(f"{args.setvalue}")
        
        # command handler
        setvalue_list = args.setvalue
        # max length of setvalue list is 4
        user_dict = {}
        user_dict['storage.name'] = 'default'
        user_dict['storage.loc'] = DEFAULT_CONFIG_DIR
        for idx, element in enumerate(setvalue_list):
            if element[0] == 'auth.username':
                user_dict['auth.username'] = element[1]
            elif element[0] == 'auth.password':
                user_dict['auth.password'] = element[1]
        
        if os.path.exists(DEFAULT_CONFIG_DIR):
            with open(os.path.join(DEFAULT_CONFIG_DIR, 'config.json'), 'w') as file:
                json.dump(user_dict, file, indent=4)
            
            
        print(f"{args.__dict__}")


