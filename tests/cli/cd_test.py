from cli.commands import cd
import pytest


# cd_cmd.cmd_entry(cmdargs, config)


from 
cmd_entry = cd.Cd().cmd_entry(cmdargs, config)

@pytest.mark.windows_cd_cmd
def test_windows_cd_cmd():
    """
    test cd command in Windows System
    """
    cd_cmd = Cd()
