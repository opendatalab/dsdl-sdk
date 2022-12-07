"""
cd function
Examples:
    $python cli.py cd --datasetname coco
    >> now in the Coco dataset context, you can use the following commands:
    >> inspect select studio search
"""

import os
import psutil
import sys
import platform
from distutils.spawn import find_executable
from typing import Dict


from commands.cmdbase import CmdBase
from commons.argument_parser import EnvDefaultVar

from utils.admin import DBClient
import commons.stdio as stdio


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
        cd_parser = subparsers.add_parser(
            "cd",
            help="change the context to the specified dataset.",
            example="cd.example",
        )
        cd_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar="DSDL_CLI_DATASET_NAME",
            type=str,
            help="dataset name",
            metavar="[DATASET NAME]",
        )
        return cd_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command
        Args:
            self:
            cmdargs:
            config:
        Returns:
        """

        # _act = _Activator()
        # _act.environ.setdefault("DATASET_NAME", "")
        # _act.environ["DATASET_NAME"] = cmdargs.dataset_name[0]
        # dsname = _act.environ.get("DATASET_NAME", "default")

        dsname = ""

        if cmdargs.dataset_name:
            os.environ.setdefault("DATASET_NAME", "")
            os.environ["DATASET_NAME"] = cmdargs.dataset_name
            dsname = os.environ.get("DATASET_NAME", "default")
        else:
            pass

        dbcli = DBClient()
        is_exists = dbcli.is_dataset_local_exist(dsname)

        if "DATASET_NAME" in os.environ and is_exists:
            sysstr = platform.system()

            if sysstr == "Windows":
                stdio.print_stdout("Enter new Windows cmd command shell")
                shell_cmd = CmdExeActivator().activate_cmd
                os.system(shell_cmd)
            elif sysstr in ["Linux"]:
                stdio.print_stdout("Enter new Linux bash command shell")
                shell_cmd = PosixActivator().activate_cmd
                os.system(shell_cmd)
            elif sysstr in ["Darwin"]:
                stdio.print_stdout("Enter new Darwin bash command shell")
                shell_cmd = PosixActivator().activate_cmd
                os.system(shell_cmd)
            else:
                stdio.print_stderr("Other Systems hava not been supported yet!")
        else:
            stdio.print_stderr("Dataset is not exist, please check the dataset name.")


class _Activator:
    # cd command Activate have three tasks
    #   1. Set and unset environment variables
    #   2. Execute base bash/csh/cmd/powershell base scripts
    #   3. Update the default varible values in the new shell environment

    pathsep_join = None
    sep = None
    script_extension = None
    tempfile_extension = (
        None  # None means write instructions to stdout rather than a temp file
    )
    command_join: str

    run_script_tmpl = None

    def __init__(self, arguments=None):
        self._raw_arguments = arguments
        self.environ = os.environ.copy()
        self.on_linux = bool(sys.platform == "linux")
        self.on_win = bool(sys.platform == "win32")
        self.on_mac = bool(sys.platform == "darwin")
        self.activate_cmd = self._get_activate_cmd()

    def activate(self):
        builder_result = self.build_activate()
        return self._finalize(self._yield_commands(builder_result))

    def _finalize(self, commands):
        merged = {}
        for _cmds in commands:
            merged.update(_cmds)
        commands = merged

    def _yield_commands(self, cmds_dict):
        for key in cmds_dict.get("unset_vars", ()):
            yield self.unset_var_tmpl % key

        for key, value in cmds_dict.get("set_vars", {}).items():
            yield self.set_var_tmpl % (key, value)

        for key, value in cmds_dict.get("export_vars", {}).items():
            yield self.export_var_tmpl % (key, value)

        for script in cmds_dict.get("activate_scripts", ()):
            yield self.run_script_tmpl % script

    def build_activate(self):
        return self._build_activate_stack()

    def _build_activate_stack(self):
        # get environment prefix
        paths = self._get_env_paths()
        activate_cmd = self._get_activate_cmd(paths)

        return {
            # TODO
            # "unset_vars": unset_vars,
            # "set_vars": set_vars,
            # "export_vars": export_vars,
            "activate_scripts": activate_cmd,
        }

    def _get_env_paths(self):
        # include macos and windows
        clean_paths = {
            "darwin": "/usr/bin:/bin:/usr/sbin:/sbin",
            "win32": "C:\\Windows\\system32;"
            "C:\\Windows;"
            "C:\\Windows\\System32\\Wbem;"
            "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\",
        }
        path = self.environ.get(
            "PATH",
            clean_paths[sys.platform]
            if sys.platform in clean_paths
            else "/usr/bin",  # default is /usr/bin of unix/linux os
        )
        path_split = path.split(os.pathsep)
        return path_split

    def _get_activate_cmd(self) -> str:
        raise NotImplementedError


class PosixActivator(_Activator):
    def __init__(self, arguments=None):
        self.pathsep_join = ":".join
        self.sep = "/"
        self.script_extension = ".sh"
        self.command_join = "\n"

        self.unset_var_tmpl = "unset %s"
        self.set_var_tmpl = "%s='%s'"
        self.export_var_tmpl = "export %s='%s'"
        self.run_script_tmpl = '. "%s"'

        super().__init__(arguments)

    def _get_activate_cmd(self) -> str:
        parent_pid = os.getppid()
        proc = psutil.Process(parent_pid)
        shell_type = proc.name().split(".")[0]
        cmd_location = find_executable(shell_type)
        return f'"{cmd_location}"'


class CmdExeActivator(_Activator):
    def __init__(self, arguments=None):
        self.pathsep_join = ";".join
        self.sep = "\\"
        self.script_extension = ".bat"
        self.tempfile_extension = ".bat"
        self.command_join = "\n"

        self.unset_var_tmpl = "@SET %s="
        self.set_var_tmpl = (
            '@SET "%s=%s"'  # TODO: determine if different than export_var_tmpl
        )
        self.export_var_tmpl = '@SET "%s=%s"'
        self.run_script_tmpl = '@CALL "%s"'

        super().__init__(arguments)

    def _get_activate_cmd(self) -> str:
        parent_pid = os.getppid()
        proc = psutil.Process(parent_pid)
        parent_proc = proc.parent()
        shell_type = parent_proc.name().split(".")[0]
        cmd_location = find_executable(shell_type)
        return f'"{cmd_location}"'


class PowerShellActivator(_Activator):
    def __init__(self, arguments=None):
        self.pathsep_join = ";".join if self.on_win else ":".join
        self.sep = "\\" if self.on_win else "/"
        self.script_extension = ".ps1"
        self.tempfile_extension = (
            None  # write instructions to stdout rather than a temp file
        )
        self.command_join = "\n"

        self.unset_var_tmpl = '$Env:%s = ""'
        self.set_var_tmpl = '$Env:%s = "%s"'
        self.export_var_tmpl = '$Env:%s = "%s"'
        self.run_script_tmpl = '. "%s"'

        super().__init__(arguments)


class CshActivator(_Activator):
    def __init__(self, arguments=None):
        self.pathsep_join = ":".join
        self.sep = "/"
        self.script_extension = ".csh"
        self.tempfile_extension = (
            None  # write instructions to stdout rather than a temp file
        )
        self.command_join = ";\n"

        self.unset_var_tmpl = "unsetenv %s"
        self.set_var_tmpl = "set %s='%s'"
        self.export_var_tmpl = 'setenv %s "%s"'
        self.run_script_tmpl = 'source "%s"'

        super().__init__(arguments)


activator_map: Dict[str, _Activator] = {
    "posix": PosixActivator,
    "ash": PosixActivator,
    "bash": PosixActivator,
    "dash": PosixActivator,
    "zsh": PosixActivator,
    "csh": CshActivator,
    "tcsh": CshActivator,
    "cmd.exe": CmdExeActivator,
    "powershell": PowerShellActivator,
}
