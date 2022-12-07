"""

Examples:

class Example(CmdBase):
    def init_parser(self, subparsers):
        status_parser = subparsers.add_parser('example', help='Show the working tree status')
        status_parser.add_argument('show', nargs='?', default='SHOW', help='show example')
        return status_parser

    def cmd_entry(self, args, config):
        print(args)
        print(config)

"""
from abc import ABC, abstractmethod
from argparse import ArgumentParser, _SubParsersAction

from commons.exceptions import CLIException
from commons.stdio import print_stderr
from loguru import logger


class CmdBase(ABC):
    """
    Base class for all commands

    Args:
        ABC:

    Returns:

    """

    def __init__(self):
        self._parser: ArgumentParser = None

    def cmd_main(self, cmdargs, config, *args, **kwargs):
        try:
            self.cmd_entry(cmdargs, config, *args, **kwargs)
        except CLIException as e:
            logger.exception(e.message)
            print_stderr(e.message)
            exit(e.errcode)
        except Exception as e:
            # TODO log
            logger.exception(e)
            print_stderr("unknown error, please see log files at ~/.dsdl/logs")
            exit(-1)
        exit(0)

    def setup_parser(self, subparsers: _SubParsersAction) -> ArgumentParser:
        self._parser = self.init_parser(subparsers)
        return self._parser

    @abstractmethod
    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            args:
            config:

        Returns:

        """
        raise NotImplementedError

    @abstractmethod
    def init_parser(self, subparsers: _SubParsersAction) -> ArgumentParser:
        """
        Initialize the parser for the command

        Args:
            self:
            subparsers:

        Returns:

        """
        raise NotImplementedError
