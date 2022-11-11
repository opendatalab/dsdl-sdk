import os, sys
from argparse import Action, HelpFormatter
import argparse


class EnvDefaultVar(Action):
    """
    默认参数使用环境变量。
    优先级为：
    显式设置的值 > default值 > 环境变量值
    """

    def __init__(self, envvar, required=False, default=None, **kwargs):
        if not default and envvar:  # 没有默认值，但是给了环境变量key
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:  # 一旦得到了默认值，那么改变required的值为False, 这样用户不必一定要在命令行显式敲出来--dataset-name这个选项
            required = False
        super(EnvDefaultVar, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class CustomHelpFormatter(HelpFormatter):
    """
    自定义命令输出格式
    """
    def _format_action(self, action):
        if type(action) == argparse._SubParsersAction:
            # inject new class variable for subcommand formatting
            subactions = action._get_subactions()
            invocations = [self._format_action_invocation(a) for a in subactions]
            self._subcommand_max_length = max(len(i) for i in invocations)

        if type(action) == argparse._SubParsersAction._ChoicesPseudoAction:
            # format subcommand help line
            subcommand = self._format_action_invocation(action)  # type: str
            width = self._subcommand_max_length
            help_text = ""
            if action.help:
                help_text = self._expand_help(action)
            return "  {:{width}} -  {}\n".format(subcommand, help_text, width=width)

        elif type(action) == argparse._SubParsersAction:
            # process subcommand help section
            msg = '\n'
            for subaction in action._get_subactions():
                msg += self._format_action(subaction)
            return msg
        else:
            return super(CustomHelpFormatter, self)._format_action(action)
