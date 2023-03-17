""""
定义输出到控制台的函数。
包含标准流输出、错误流输出
"""
import sys


def print_stdout(msg, *args, sep=' ', end='\n'):
    """标准输出"""
    print(msg, *args, sep=sep, end=end, file=sys.stdout)


def print_stderr(msg, *args, sep=' ', end='\n'):
    """错误输出"""
    print(msg, *args, sep=sep, end=end, file=sys.stderr)
