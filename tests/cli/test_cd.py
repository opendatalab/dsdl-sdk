import os
import sys
import json
import pprint
import shlex
import subprocess
from subprocess import Popen
from pathlib import Path
import psutil
import platform
import select
import termios
import tty
import pty
import pexpect
import pytest


from distutils.spawn import find_executable
from typing import Dict
from dotenv import (
    find_dotenv,
    load_dotenv,
    set_key,
    get_key,
    unset_key,
)

from cli.commands.cd import Cd



cd = Cd()
cd_parser = cd.init_parser(self, subparsers)

@pytest.mark.parametrize("option", ("-h", "--help"))
def test_help(capsys, option):
    try:
        main([option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "change the context to the specified dataset." in output

@pytest.mark.parametrize("dataset_name", ("CIFAR-10-Auto", "CIFAR-10"))
def test_cd_windows_cmd(dataset_name):
    cd_parser.parse_args(["cd", dataset_name])
    cd_parser.parse_args(["cd", "-h"])
    cd_parser.parse_args(["cd", "--help"])

@pytest.mark.parametrize("dataset_name", ("CIFAR-10-Auto", "CIFAR-10"))
def test_cd_darwin_bash(dataset_name):
    cd_parser.parse_args(["cd", dataset_name])
    cd_parser.parse_args(["cd", "-h"])
    cd_parser.parse_args(["cd", "--help"])

@pytest.mark.parametrize("dataset_name", ("CIFAR-10-Auto", "CIFAR-10"))
def test_cd_centos_bash(dataset_name):
    cd_parser.parse_args(["cd", dataset_name])
    cd_parser.parse_args(["cd", "-h"])
    cd_parser.parse_args(["cd", "--help"])


def func1():
    # command = shlex.split("env -i bash -c 'source ~/.dsdl/.env'")
    command = shlex.split("env -i 'source ~/.dsdl/.env'")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        os.environ[key] = value
    proc.communicate()

    pprint.pprint(dict(os.environ))


def func2():
    source = "souece ~/.dsdl/.env"
    dump = '/usr/bin/python -c "import os, json;print json.dumps(dict(os.environ))"'
    pipe = sp.Popen(["/bin/bash", "-c", "%s && %s" % (source, dump)], stdout=sp.PIPE)
    env = json.loads(pipe.stdout.read())
    os.environ = env


def func3():
    dotenv_path = Path("/root/.dsdl/.env")

    # write a=b to .env
    dsname = "test-1"
    set_key(dotenv_path, "NAME_1", dsname)

    load_dotenv(dotenv_path)

    NAME = os.getenv("DS_NAME")
    print(NAME)

    NAME = os.getenv("NAME_1")
    print(NAME)



def func4():

    command = "bash"
    # command = 'docker run -it --rm centos /bin/bash'.split()

    # save original tty setting then set it to raw mode
    old_tty = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())

    # open pseudo-terminal to interact with subprocess
    master_fd, slave_fd = pty.openpty()

    # use os.setsid() make it run in a new process group, or bash job control will not be enabled
    p = Popen(
        command,
        preexec_fn=os.setsid,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        universal_newlines=True,
    )

    while p.poll() is None:
        r, w, e = select.select([sys.stdin, master_fd], [], [])
        if sys.stdin in r:
            d = os.read(sys.stdin.fileno(), 10240)
            os.write(master_fd, d)
        elif master_fd in r:
            o = os.read(master_fd, 10240)
            if o:
                os.write(sys.stdout.fileno(), o)

    # restore tty settings back
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)


def func5():
    import pathlib

    # change to this file's paprent directory
    current_dir = pathlib.Path(__file__).parent.absolute()
    os.chdir(current_dir)
    print(os.getcwd())
    # os.chdir(__file__/)
    cmd = "source {current_dir}/test_cd.sh".format(current_dir=current_dir)
    print(cmd)
    os.system(cmd)
    sys.stdout.write("export DATASET_NAME='CIFAR-10-Auto'>>sys.stdin")


def func6():

    env_dist = os.environ  # environ是在os.py中定义的一个dict environ = {}

    # # 打印所有环境变量，遍历字典
    # for key in env_dist:
    #     print(key + " : " + env_dist[key])

    # write all key value paires to .env file
    dotenv_path = Path("/root/.dsdl/.env")
    for key in env_dist:
        set_key(dotenv_path, key, env_dist[key])

    dsname = "CIFAR-10-Auto"
    set_key(dotenv_path, "DATASET_NAME", dsname)

    load_dotenv(dotenv_path)


def func7():
    # print(pexpect.run("echo hello"))
    print(pexpect.run("bash -c 'export foo=bar; echo $foo'"))


def func8():
    import pty

    pty.spawn("/bin/bash")


def main():
    # func1()
    # func2()
    # func3()
    # func4()
    # func5()
    # func6()
    # func7()
    # func8()



if __name__ == "__main__":
    main()
