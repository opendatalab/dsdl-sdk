import json
import os
import shutil

from commons.stdio import print_stderr, print_stdout
from loguru import logger
from rich import print as rprint
from rich.pretty import pprint

from .cmdbase import CmdBase
from .const import DEFAULT_CLI_CONFIG_FILE


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

        config_parser = subparsers.add_parser(
            'config',
            help='set odl-cli configuration.',
            example='config.example')
        config_parser.add_argument('-k',
                                   '--keys',
                                   action='store_true',
                                   help='show all the available keys',
                                   required=False)
        config_parser.add_argument('-l',
                                   '--list',
                                   action='count',
                                   help='show all key value pairs',
                                   required=False)

        sub_config_parser = config_parser.add_subparsers(dest='command')
        repo_parser = sub_config_parser.add_parser(
            'repo', help='set repo configuration')
        repo_parser.add_argument('--repo-name',
                                 help='set repo name',
                                 required=True)
        repo_parser.add_argument('--repo-username', help='set repo user name')
        repo_parser.add_argument('--repo-userpswd',
                                 help='set repo user password')
        repo_parser.add_argument('--repo-service', help='set repo service url')
        repo_parser.add_argument('--repo-remove',
                                 action='store_true',
                                 help='remove specific configuration',
                                 required=False)

        storage_parser = sub_config_parser.add_parser(
            'storage',
            help='set storage configuration, only support local/s3/sftp for now'
        )
        storage_parser.add_argument('--storage-name',
                                    help='set storage name',
                                    required=True)
        storage_parser.add_argument('--storage-path',
                                    help='set storage path',
                                    required=True)
        storage_parser.add_argument('--storage-credentials',
                                    action='append',
                                    nargs=2,
                                    help='set credentials',
                                    required=False)
        storage_parser.add_argument('--storage-endpoint',
                                    help='set storage endpoint',
                                    default='',
                                    required=False)
        storage_parser.add_argument(
            '--storage-remove',
            action='store_true',
            help='remove specific storage configuration',
            required=False)
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
        # if not args.repo_name:
        #             logger.exception('Please name a repo using {} before you can set is info'.format('--repo-name'))
        if args.command:
            # repo command handler
            if args.command == 'repo':
                if args.repo_remove:
                    try:
                        self.__repo_delete(config, args)
                        self.__config_writter(config)
                        print_stdout('REPO config for {} was removed !'.format(
                            args.repo_name))
                        logger.info('REPO config for {} was removed !'.format(
                            args.repo_name))
                    except KeyError as err:
                        print_stdout('No repo named {}!'.format(
                            args.repo_name))
                        logger.exception('No repo named {}'.format(
                            args.repo_name))
                elif (not args.repo_remove) & (args.repo_name
                                               not in config['repo'].keys()):
                    # new repo
                    self.__repo_new(config, args)
                    print_stdout('Your repo config for {} success !'.format(
                        args.repo_name))
                    logger.info('REPO: {} config success !'.format(
                        args.repo_name))
                    self.__config_writter(config)
                else:
                    print_stdout(
                        'REPO config for {} already exists, please remove and re-configure it !'
                        .format(args.repo_name))
                    logger.error(
                        'REPO config for {} already exists, please remove and re-configure it !'
                        .format(args.repo_name))

            elif args.command == 'storage':
                if args.storage_remove:
                    try:
                        self.__storage_delete(config, args)
                        self.__config_writter(config)
                        print_stdout(
                            'STORAGE config for {} was removed !'.format(
                                args.storage_name))
                        logger.info(
                            'STORAGE config for {} was removed !'.format(
                                args.storage_name))
                    except KeyError as err:
                        print_stdout('No storage named {} !'.format(
                            args.storage_name))
                        logger.exception('No storage named {} !'.format(
                            args.storage_name))

                # new storage entry
                elif (not args.storage_remove) & (
                        args.storage_name not in config['storage'].keys()):
                    self.__storage_new(config, args)
                    self.__config_writter(config)
                # old storage update
                else:
                    print_stdout(
                        'STORAGE config for {} already exists, please remove and re-configure it !'
                        .format(args.storage_name))
                    logger.error(
                        'STORAGE config for {} already exists, please remove and re-configure it !'
                        .format(args.storage_name))
        else:
            if args.keys:
                snippet_keys = """The available keys are:
                \nrepo-name           # set repo name\nrepo-username       # set repo username\nrepo-userpswd       # set repo password\nrepo-service        # set repo service url
                \nstorage-name        # storage name\nstorage-path        # storage path\nstorage-credentials # storage credentials S3:(access-key, secret-key), SFTP:(username,password)\nstorage-endpoint    # storage endpoint
                """
                rprint(snippet_keys)

            if args.list:
                if args.list == 1:
                    pprint(config)
                else:
                    pprint(config, expand_all=True)

            if not (args.keys or args.list):
                helper_str = """Please use -h to get more information. """
                # rprint(helper_str)
                self._parser.print_help()

    def __get_space(self, path: str):
        """
        return free space (GB) on local disk
        Args:
            path:

        Returns:

        """
        _, _, free = shutil.disk_usage(path)
        space = free / 1024 / 1024 / 1024
        return space

    def __config_writter(self, config):
        with open(DEFAULT_CLI_CONFIG_FILE, 'w') as file:
            return json.dump(config, file, indent=4)

    def __repo_new(self, config, args):
        config['repo'][args.repo_name] = {}
        if args.repo_username:
            config['repo'][args.repo_name]['user'] = args.repo_username
        if args.repo_userpswd:
            config['repo'][args.repo_name]['passwd'] = args.repo_userpswd
        if args.repo_service:
            config['repo'][args.repo_name]['service'] = args.repo_service

    def __repo_delete(self, config, args):
        del config['repo'][args.repo_name]

    def __storage_new(self, config, args):

        if args.storage_path[:2] not in ['s3', 'sf']:
            # local store not exists: --new
            if os.path.exists(args.storage_path) is False:
                try:
                    os.mkdir(args.storage_path)
                    config['storage'][args.storage_name] = {}

                    config['storage'][
                        args.storage_name]['path'] = args.storage_path
                    space = self.__get_space(args.storage_path)
                    print_stdout(
                        'STORAGE LOCAL: The path {} configuration is successful, current path have {:.4}GB left!'
                        .format(args.storage_path, space))
                    logger.info(
                        'STORAGE LOCAL: The path {} configuration is successful, current path have {:.4}GB left!'
                        .format(args.storage_path, space))
                except OSError as e:
                    print_stderr(
                        'STORAGE LOCAL: unable to create path {}'.format(
                            args.storage_path))
                    logger.error(
                        'STORAGE LOCAL: unable to create path {}'.format(
                            args.storage_path))
            # local store exists and empty: --continue
            elif len(os.listdir(args.storage_path)) == 0:
                config['storage'][args.storage_name] = {}
                config['storage'][
                    args.storage_name]['path'] = args.storage_path
                space = self.__get_space(args.storage_path)
                print_stdout(
                    'STORAGE LOCAL: The path {} configuration is successful, current path have {:.4}GB left!'
                    .format(args.storage_path, space))
                logger.info(
                    'STORAGE LOCAL: The path {} configuration is successful, current path have {:.4}GB left!'
                    .format(args.storage_path, space))
            # local store exists and not empty:
            elif len(os.listdir(args.storage_path)) > 0:
                print_stderr(
                    'STORAGE LOCAL: The path {} is not empty, please check before configuration'
                    .format(args.storage_path))
                logger.error(
                    'STORAGE LOCAL: The path {} is not empty, please check before configuration'
                    .format(args.storage_path))

        elif args.storage_path[:2] == 's3':
            try:
                config['storage'][
                    args.storage_name]['ak'] = args.storage_credentials[0][0]
                config['storage'][
                    args.storage_name]['sk'] = args.storage_credentials[0][1]
                config['storage'][
                    args.storage_name]['endpoint'] = args.storage_endpoint
                config['storage'][
                    args.storage_name]['path'] = args.storage_path
                print_stdout('STORAGE S3: {} config success !'.format(
                    args.storage_name))
                logger.info('STORAGE S3: {} config success !'.format(
                    args.storage_name))
            except TypeError as e:
                print_stderr(
                    'STORAGE S3: config incomplete! access-key,secret-key and endpoint are required !'
                )
                logger.error(
                    'STORAGE S3: config incomplete! access-key,secret-key and endpoint are required !'
                )

        elif args.storage_path[:4] == 'sftp':
            try:
                config['storage'][
                    args.storage_name]['user'] = args.storage_credentials[0][0]
                config['storage'][args.storage_name][
                    'password'] = args.storage_credentials[0][1]
                config['storage'][
                    args.storage_name]['path'] = args.storage_path

                print_stdout('STORAGE SFTP: {} config success !'.format(
                    args.storage_name))
                logger.info('STORAGE STFP: {} config success !'.format(
                    args.storage_name))
            except TypeError as e:
                print_stderr(
                    'STORAGE SFTP: config incomplete! username and password are required !'
                )
                logger.error(
                    'STORAGE SFTP: config incomplete! username and password are required !'
                )

    def __storage_delete(self, config, args):
        del config['storage'][args.storage_name]
