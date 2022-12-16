import click
from typing import Sequence, Union
import os

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from yaml import load as yaml_load
import json

TASK_FIELDS = {
    "detection": ["image", "label", "bbox", "polygon", "keypoint", "rotatedbbox"],
    "classification": ["image", "label"],
    "semantic-seg": ["image", "labelmap"],
    "panoptic-seg": ["image", "labelmap", "instancemap"],
    "ocr": ["image", "rotatedbbox", "text", "polygon"]
}


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


def load_samples(dsdl_path: str, path: Union[str, Sequence[str]], extract_key="samples"):
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
                data = yaml_load(f, YAMLSafeLoader)[extract_key]
            if isinstance(data, list):
                samples.extend(data)
            else:
                samples.append(data)
        else:
            with open(p, "r") as f:
                data = json.load(f)[extract_key]
            if isinstance(data, list):
                samples.extend(data)
            else:
                samples.append(data)
    return samples


def prepare_input(**kwargs):
    def _decorator(func):
        def process(dsdl_yaml, config, location, num, random, fields, task, position, **kwargs2):
            result = {
                "dsdl_yaml": dsdl_yaml,
                "config": config,
                "location": location,
                "num": num,
                "random": random,
                "fields": fields,
                "task": task,
                "position": position,
                **kwargs2
            }

            # parse samples and global-info
            with open(dsdl_yaml, "r") as f:
                dsdl_info = yaml_load(f, Loader=YAMLSafeLoader)['data']
                sample_type = dsdl_info['sample-type']
                global_info_type = dsdl_info.get("global-info-type", None)
                global_info = None
                if "sample-path" not in dsdl_info or dsdl_info["sample-path"] in ("local", "$local"):
                    assert "samples" in dsdl_info, f"Key 'samples' is required in {dsdl_yaml}."
                    samples = dsdl_info['samples']
                else:
                    sample_path = dsdl_info["sample-path"]
                    samples = load_samples(dsdl_yaml, sample_path)
                if global_info_type is not None:
                    if "global-info-path" not in dsdl_info:
                        assert "global-info" in dsdl_info, f"Key 'global-info' is required in {dsdl_yaml}."
                        global_info = dsdl_info["global_info"]
                    else:
                        global_info_path = dsdl_info["global-info-path"]
                        global_info = load_samples(dsdl_yaml, global_info_path, "global-info")[0]
            result["dsdl_yaml"] = {"samples": samples, "global_info": global_info, "sample_type": sample_type,
                                   "global_info_type": global_info_type, "yaml_file": dsdl_yaml}

            # parse location config
            config_dic = {}
            with open(config, encoding='utf-8') as config_file:
                exec(config_file.read(), config_dic)
            location_config = config_dic["local" if location == "local" else "ali_oss"]
            result["config"] = location_config

            # parse field list
            if task:
                assert task in TASK_FIELDS, f"invalid task, you can only choose in {list(TASK_FIELDS.keys())}"
                fields = TASK_FIELDS[task]
            else:
                if fields is None:
                    fields = []
                else:
                    local_dic = {}
                    exec(f"f = list({fields})", {}, local_dic)
                    fields = local_dic['f']
                fields = list(set(fields + ["image", "dict"]))
            fields = [_.lower() for _ in fields]

            result["fields"] = fields

            return result

        def wrapper(*args, **kwargs3):
            ret = process(*args, **kwargs3, **kwargs)
            ret = func(**ret)
            return ret

        return wrapper

    return _decorator
