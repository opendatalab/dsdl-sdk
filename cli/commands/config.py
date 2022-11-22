import json
import os

from rich import print as rprint
from rich.console import Console
from rich.pretty import pprint
from rich.syntax import Syntax
from tabulate import tabulate

from .cmdbase import CmdBase
from .const import (DEFAULT_CLI_CONFIG_FILE, DEFAULT_CONFIG_DIR,
                    DEFAULT_LOCAL_STORAGE_PATH, PROG_NAME, SQLITE_DB_PATH)


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

        # config_parser = subparsers.add_parser('config', help='set dsdl configuration.', example='config.example')
        config_parser = subparsers.add_parser('config', help='set dsdl configuration.')

        
        config_parser.add_argument('-k',
                                   '--keys',
                                   action = 'store_true',
                                   help = 'show all the available keys',
                                   required = False)
        # config_parser.add_argument('-s',
        #                            '--setvalue',
        #                            type = str,
        #                            nargs = 2,
        #                            action = 'append',
        #                            help = 'Set key-value for a specific configuration.')
        config_parser.add_argument('-l',
                                   '--list',
                                   action = 'count',
                                   help = 'show all key value pairs',
                                   required = False)

        
        sub_config_parser = config_parser.add_subparsers(dest = 'command')
        repo_parser = sub_config_parser.add_parser('repo', help = 'set dsdl repo configuration')
        repo_parser.add_argument('--repo-name',
                                 help = 'set repo name')
        repo_parser.add_argument('--repo-username', 
                                 help = 'set repo user name')
        repo_parser.add_argument('--repo-userpswd', 
                                 help = 'set repo user password')
        repo_parser.add_argument('--repo-service', 
                                 help = 'set repo service url')

        
        storage_parser = sub_config_parser.add_parser('storage', help = 'set dsdl storage configuration')
        storage_parser.add_argument('--storage-name', 
                                    help = 'set storage name', 
                                    required = True)
        storage_parser.add_argument('--storage-path',
                                    help = 'set storage path',
                                    required = True)
        storage_parser.add_argument('--storage-username', 
                                    help = 'set storage user name')
        storage_parser.add_argument('--storage-credentials',
                                    action = 'extend',
                                    nargs = '+',
                                    help = 'set credentials' )
        storage_parser.add_argument('--storage-endpoint',
                                    help = 'set storage endpoint')        
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
        if args.command:
            # repo command handler
            if args.command == 'repo':
                if not args.repo_name:
                    rprint('please name a repo using [bold blue]--repo-name [/bold blue]before you can set its info!')
                else:
                    if args.repo_name not in config['repo'].keys():
                        config['repo'][args.repo_name] = {}
                        if args.repo_username:
                            config['repo'][args.repo_name]['user'] = args.repo_username
                        if args.repo_userpswd:
                            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
                        if args.repo_service:
                            config['repo'][args.repo_name]['service'] = args.repo_service
                    else:
                        if args.repo_username:
                            config['repo'][args.repo_name]['user'] = args.repo_username
                        if args.repo_userpswd:
                            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
                        if args.repo_service:
                            config['repo'][args.repo_name]['service'] = args.repo_service

            # storage command handler
            elif args.command == 'storage':
                if not args.storage_name:
                    rprint('please name a storage using [bold blue]--storage-name [/bold blue]before you can set its info!')
                else:
                    if args.storage_name not in config['storage'].keys():
                        config['storage'][args.storage_name] = {}
                        if args.storage_username:
                            config['storage'][args.storage_name]['user'] = args.storage_username
                        if args.storage_credentials:
                            if len(args.storage_credentials) > 2:
                                rprint('credentials requires [red]1 or 2 [/red]input!\n',
                                       '[yellow]1[/yellow] for password/ssh-key\n', 
                                       '[yellow]2[/yellow] for access-key & secret-key')
                            else:
                                config['storage'][args.storage_name]['credentials'] = args.storage_credentials
                        if args.storage_endpoint:
                            config['storage'][args.storage_name]['endpoint'] = args.storage_endpoint
                        if args.storage_path:
                            config['storage'][args.storage_name]['path'] = args.storage_path
                    else:
                        if args.storage_username:
                            config['storage'][args.storage_name]['user'] = args.storage_username
                        if args.storage_credentials:
                            if len(args.storage_credentials) > 2:
                                rprint('credentials requires [red]1 or 2 [/red]input!\n', 
                                       '[yellow]1[/yellow] for password/ssh-key\n', 
                                       '[yellow]2[/yellow] for access-key & secret-key')
                            else:
                                config['storage'][args.storage_name]['credentials'] = args.storage_credentials
                        if args.storage_endpoint:
                            config['storage'][args.storage_name]['endpoint'] = args.storage_endpoint
                        if args.storage_path:
                            config['storage'][args.storage_name]['path'] = args.storage_path
        
        
        if args.keys:
            snippet_keys = """
            The available keys are:
                repo-name               # set repo name
                repo-username           # set repo username
                repo-userpswd           # set repo password
                repo-service            # set repo service url
            
                storage-name            # storage name
                storage-path            # storage path
                storage-username        # storage username
                storage-credentials     # storage credentials (password, ssh-key, access-key, secret-key)
                storage-endpoint        # storage endpoint
            """
            rprint(snippet_keys)
        
        if args.list:
            if args.list == 1:
                pprint(config)
            else:
                pprint(config, expand_all = True)
        
        # # print(f"{args.setvalue}")
        # # command handler
         

        
        with open(DEFAULT_CLI_CONFIG_FILE, 'w') as file:
            return json.dump(config,file, indent=4)
