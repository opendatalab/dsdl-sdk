import click
from typing import Sequence, Union
import os
try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from yaml import load as yaml_load
import json



class OptionEatAll(click.Option):
    """
    implemented by https://stackoverflow.com/users/7311767/stephen-rauch in https://stackoverflow.com/questions/48391777/nargs-equivalent-for-options-in-click
    """

    def __init__(self, *args, **kwargs):
        self.save_other_options = kwargs.pop('save_other_options', True)
        nargs = kwargs.pop('nargs', -1)
        assert nargs == -1, 'nargs, if set, must be -1 not {}'.format(nargs)
        super(OptionEatAll, self).__init__(*args, **kwargs)
        self._previous_parser_process = None
        self._eat_all_parser = None

    def add_to_parser(self, parser, ctx):

        def parser_process(value, state):
            # method to hook to the parser.process
            done = False
            value = [value]
            if self.save_other_options:
                # grab everything up to the next option
                while state.rargs and not done:
                    for prefix in self._eat_all_parser.prefixes:
                        if state.rargs[0].startswith(prefix):
                            done = True
                    if not done:
                        value.append(state.rargs.pop(0))
            else:
                # grab everything remaining
                value += state.rargs
                state.rargs[:] = []
            value = tuple(value)

            # call the actual process
            self._previous_parser_process(value, state)

        retval = super(OptionEatAll, self).add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._eat_all_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break
        return retval


YAML_VALID_SUFFIX = ('.yaml', '.YAML')
JSON_VALID_SUFFIX = ('.json', '.JSON')
VALID_SUFFIX = YAML_VALID_SUFFIX + JSON_VALID_SUFFIX


def load_samples(dsdl_path: str, path: Union[str, Sequence[str]]):
    samples = []
    paths = []
    dsdl_dir = os.path.split(dsdl_path)[0]
    if isinstance(path, str):
        path = os.path.join(dsdl_dir, path)
        if os.path.isdir(path):
            paths = [os.path.join(path, _) for _ in os.listdir(path) if _.endswith(VALID_SUFFIX)]
        elif os.path.isfile(path):
            if path.endswith(VALID_SUFFIX):
                paths = [path]
    elif isinstance(path, (list, tuple)):
        paths = [os.path.join(dsdl_dir, _) for _ in path if os.path.isfile(_) and _.endswith(VALID_SUFFIX)]
    for p in paths:
        if p.endswith(YAML_VALID_SUFFIX):
            with open(p, "r") as f:
                data = yaml_load(f, YAMLSafeLoader)['samples']
            samples.extend(data)
        else:
            with open(p, "r") as f:
                data = json.load(f)['samples']
            samples.extend(data)
    return samples


