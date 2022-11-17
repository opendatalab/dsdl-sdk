import argparse
import os
import sys
from argparse import Action, HelpFormatter


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


class DsdlArgumentParser(argparse.ArgumentParser):
    """
    重写ArgumentParser的format_usage方法，使得usage信息可以自动换行。
    """

    def __init__(self, example='',  *args, **kwargs):
        self.__example = example
        super(DsdlArgumentParser, self).__init__(*args, **kwargs)

    def format_usage(self):
        if self.usage:
            return f"usage: {self.usage}"
        else:
            formatter = self._get_formatter()
            formatter.add_usage(self.usage, self._actions,
                                self._mutually_exclusive_groups)
            return formatter.format_help()

    def add_subparsers(self, **kwargs):
        """
        重写add_subparsers方法，使得help信息可以自动换行。
        """
        kwargs.setdefault('prog', self.prog)
        return super(DsdlArgumentParser, self).add_subparsers(**kwargs)

    def add_example(self, formatter):
        # example
        if self.__example:
            # read txt from resources/example.txt
            example_file = os.path.join(os.path.dirname(__file__), '../resources', self.__example)
            if os.path.exists(example_file):
                with open(example_file, 'r') as f:
                    example_str = f.read()
                    formatter.start_section("Examples")
                    formatter.add_raw_text(example_str)
                    formatter.end_section()

    def format_help(self) -> str:
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

        # example
        self.add_example(formatter)

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()


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
            subcommand = self._format_action_invocation(action)
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

    def format_help(self):
        return super().format_help()

    def add_raw_text(self, text):
        if text is not None:
            if '%(prog)' in text:
                text = text % dict(prog=self._prog)
            self._add_item(lambda t : t, [text])
