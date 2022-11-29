import os
import sys
import platform
import pytest
from cli.commands import cd
from cli.commands.cd import (
    activator_map,
    PosixActivator,
    CmdExeActivator,
    CshActivator,
    PowerShellActivator,
)
from conftest import which

on_win = bool(sys.platform == "win32")
on_mac = bool(sys.platform == "darwin")
on_linux = bool(sys.platform == "linux")


class InteractiveShell:
    activator = None
    init_command = None
    print_env_var = None

    shells = {
        "posix": {
            "activator": "posix",
            "print_env_var": 'echo "$%s"',
        },
        "bash": {
            # MSYS2's login scripts handle mounting the filesystem. Without it, /c is /cygdrive.
            "args": ("-l",) if on_win else (),
            "base_shell": "posix",  # inheritance implemented in __init__
        },
        "dash": {
            "base_shell": "posix",  # inheritance implemented in __init__
        },
        "zsh": {
            "base_shell": "posix",  # inheritance implemented in __init__
        },
        "cmd.exe": {
            "activator": "cmd.exe",
            "print_env_var": "@echo %%%s%%",
        },
        "csh": {
            "activator": "csh",
            "print_env_var": 'echo "$%s"',
        },
        "tcsh": {
            "base_shell": "csh",
        },
        "powershell": {
            "activator": "powershell",
            "args": ("-NoProfile", "-NoLogo"),
            "print_env_var": "$Env:%s",
            "exit_cmd": "exit",
        },
        "pwsh": {"base_shell": "powershell"},
        "pwsh-preview": {"base_shell": "powershell"},
    }

    def __init__(self, shell_name):
        self.shell_name = shell_name
        base_shell = self.shells[shell_name].get("base_shell")
        shell_vals = self.shells.get(base_shell, {}).copy()
        shell_vals.update(self.shells[shell_name])
        for key, value in shell_vals.items():
            setattr(self, key, value)
        self.activator = activator_map[shell_vals["activator"]]()
        self.exit_cmd = self.shells[shell_name].get("exit_cmd", None)
