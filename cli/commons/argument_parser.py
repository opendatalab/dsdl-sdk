import os, sys
from argparse import Action


class EnvDefaultVar(Action):
    """
    默认参数使用环境变量。
    优先级为：
    显式设置的值 > default值 > 环境变量值
    """

    def __init__(self, envvar, required=False, default=None, **kwargs):
        if not default and envvar: # 没有默认值，但是给了环境变量key
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:  # 一旦得到了默认值，那么改变required的值为False, 这样用户不必一定要在命令行显式敲出来--dataset-name这个选项
            required = False
        super(EnvDefaultVar, self).__init__(default=default, required=required,
                                            **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
