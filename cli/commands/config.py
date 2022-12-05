import json
import os

from loguru import logger
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
        repo_parser.add_augument('--repo-remove',
                                 help = 'remove specific configuration')
        
        storage_parser = sub_config_parser.add_parser('storage', help = 'set dsdl storage configuration')
        storage_parser.add_argument('--storage-name', 
                                    help = 'set storage name', 
                                    required = True)
        storage_parser.add_argument('--storage-path',
                                    help = 'set storage path',
                                    required = True)
        # storage_parser.add_argument('--storage-username', 
        #                             help = 'set storage user name')
        storage_parser.add_argument('--storage-credentials',
                                    action = 'append',
                                    nargs = 2,
                                    help = 'set credentials',
                                    required = False)
        storage_parser.add_argument('--storage-endpoint',
                                    help = 'set storage endpoint',
                                    default = '',
                                    required = False)
        storage_parser.add_argument('--storage-remove',
                                    help = 'remove specific storage configuration')
        return config_parser

    @logger.catch
    def cmd_entry(self, args, config):
        """
        Entry point for the command.

        Args:
            self:
            args:
            config:

        Returns:

        """
        # print(args.storage_credentials)
        
        
        
        if args.command:
            # repo command handler
            if args.command == 'repo':
                if not args.repo_name:
                    logger.exception('Please name a repo using {} before you can set is info'.format('--repo-name'))
                else:
                    if args.repo_name not in config['repo'].keys():
                        # new repo
                        self.__repo_new(config, args)
                    else:
                        # update repo
                        self.__repo_update(config, args)
                        if args.repo_username:
                            config['repo'][args.repo_name]['user'] = args.repo_username
                        if args.repo_userpswd:
                            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
                        if args.repo_service:
                            config['repo'][args.repo_name]['service'] = args.repo_service

            elif args.command == 'storage':
                # new storage entry
                if args.storage_name not in config['storage'].keys():
                    config['storage'][args.storage_name] = {}
                    if args.storage_path[:2] not in ['s3','sf']:
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        rprint('Your local storage was switched to {}!'.format(args.storage_path))
                    elif args.storage_path[:2] == 's3':
                        config['storage'][args.storage_name]['ak'] = args.storage_credentials[0][0]
                        config['storage'][args.storage_name]['sk'] = args.storage_credentials[0][1]
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        config['storage'][args.storage_name]['endpoint'] = args.storage_endpoint
                        rprint('Your [yellow]s3[/yellow] config for [yellow]{}[/yellow] success !'.format(args.storage_name))
                    elif args.storage_path[:4] == 'sftp':
                        config['storage'][args.storage_name]['user'] = args.storage_credentials[0][0]
                        config['storage'][args.storage_name]['password'] = args.storage_credentials[0][1]
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        rprint('Your [yellow]sftp[/yellow] config for [yellow]{}[/yellow] success !'.format(args.storage_name))
                
                # old storage update
                else:
                    if args.storage_path[:2] not in ['s3','sf']:
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        rprint('Your local storage was switched to {}!'.format(args.storage_path))
                    elif args.storage_path[:2] == 's3':
                        config['storage'][args.storage_name]['ak'] = args.storage_credentials[0][0]
                        config['storage'][args.storage_name]['sk'] = args.storage_credentials[0][1]
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        config['storage'][args.storage_name]['endpoint'] = args.storage_endpoint
                        rprint('Your update for [yellow]s3[/yellow] config [yellow]{}[/yellow] success !'.format(args.storage_name))

                    elif args.storage_path[:4] == 'sftp':
                        config['storage'][args.storage_name]['user'] = args.storage_credentials[0][0]
                        config['storage'][args.storage_name]['password'] = args.storage_credentials[0][1]
                        config['storage'][args.storage_name]['path'] = args.storage_path
                        rprint('Your update for [yellow]sftp[/yellow] config [yellow]{}[/yellow] success !'.format(args.storage_name))

        if args.keys:
            snippet_keys = """
            The available keys are:
                repo-name               # set repo name
                repo-username           # set repo username
                repo-userpswd           # set repo password
                repo-service            # set repo service url
            
                storage-name            # storage name
                storage-path            # storage path
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

    @logger.catch
    def __repo_new(self, config, args):
        config['repo'][args.repo_name] = {}
        if args.repo_username:
            config['repo'][args.repo_name]['user'] = args.repo_username
        if args.repo_userpswd:
            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
        if args.repo_service:
            config['repo'][args.repo_name]['service'] = args.repo_service
    
    def __repo_update(self, config, args):
        if args.repo_username:
            config['repo'][args.repo_name]['user'] = args.repo_username
        if args.repo_userpswd:
            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
        if args.repo_service:
            config['repo'][args.repo_name]['service'] = args.repo_service
        pass
    
    def __repo_delete(self, config, args):
        pass
    
    def __storage_new(self, config, args):
        pass
    
    def __storage_update(self, config, args):
        pass
    
    def __storage_delete(self, config, args):
        pass