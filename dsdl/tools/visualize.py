from ..dataset import Dataset, ImageVisualizePipeline, Util
from ..objectio import LocalFileReader
import click
import numpy as np
from random import randint
import cv2
import os
import json
import random
from ..warning import FieldNotFoundWarning

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from .commons import OptionEatAll, prepare_input, load_samples, TASK_FIELDS
from ..parser import dsdl_parse
from yaml import load as yaml_load
from ..geometry import LABEL, STRUCT, CLASSDOMAIN


@click.command(name="view")
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", "config", type=str, required=True, help="the path of the config file")
@click.option("-l", "--location", "location", type=click.Choice(["local", "ali-oss"]), required=True,
              help="the path of the config file")
@click.option("-n", "--num", "num", type=int, default=5, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-v", "--visualize", is_flag=True, help="whether to visualize the sample selected")
@click.option("-f", "--fields", cls=OptionEatAll, type=str, help="the task to visualize")
@click.option("-t", "--task", type=str, help="the task to visualize")
@click.option("-p", "--position", type=str, required=False, help='the directory of dsdl define file')
@click.option("-m", "--multistage", is_flag=True, help="whether to use the generated python file")
@prepare_input(output=None)
def view(dsdl_yaml, num, random, visualize, fields, config, position, multistage, **kwargs):
    # parse
    if multistage:
        dsdl_py = os.path.splitext(dsdl_yaml["yaml_file"])[0] + ".py"
        with open(dsdl_py, encoding='utf-8') as dsdl_file:
            exec(dsdl_file.read(), {})
    else:
        if position:
            dsdl_py = dsdl_parse(dsdl_yaml["yaml_file"], dsdl_library_path=position)
        else:
            dsdl_py = dsdl_parse(dsdl_yaml["yaml_file"], dsdl_library_path="")
        exec(dsdl_py, {})

    dataset = Dataset(dsdl_yaml["samples"], dsdl_yaml["sample_type"], config,
                      global_info=dsdl_yaml["global_info"], global_info_type=dsdl_yaml["global_info_type"])

    num = min(num, len(dataset))
    if not random:
        indices = list(range(num))
    else:
        indices = [randint(0, len(dataset) - 1) for _ in range(num)]

    samples = list()
    palette = dict()
    for ind in indices:
        samples.append(ImageVisualizePipeline(sample=dataset[ind], palette=palette, field_list=fields))

    print(Util.format_sample([s.format() for s in samples]))
    # 将读取的样本进行可视化
    if visualize:
        for sample in samples:
            vis_sample = sample.visualize()
            for vis_name, vis_item in vis_sample.items():
                cv2.imshow(vis_name, cv2.cvtColor(np.array(vis_item), cv2.COLOR_BGR2RGB))
                cv2.waitKey(0)


class StudioView:
    def __init__(self, dataset_name, task_type, n=None, shuffle=False):
        self.dataset_name = dataset_name
        assert task_type in TASK_FIELDS, f"invalid task, you can only choose in {list(TASK_FIELDS.keys())}"
        self.fields = TASK_FIELDS[task_type]
        self.task_type = task_type
        self.sample_num = n
        self.shuffle = shuffle
        self.yaml_paths, self.media_dir = self.get_yaml_for_cli(dataset_name)
        self.file_reader = self._init_file_reader()
        self._length = None
        self._palette = dict()
        self._ind = 0
        self._generator = self._init_generator()

    def reinit(self):
        self._palette = dict()
        self._ind = 0
        self._generator = self._init_generator()

    def __iter__(self):
        return self

    def __next__(self):
        if self.sample_num is not None:
            if self._ind < self.sample_num:
                return next(self._generator)
            else:
                raise StopIteration
        else:
            return next(self._generator)

    def __len__(self):
        if self._length is None:
            self._length = self._parse_length()
        return self._length

    def _init_generator(self):
        for dsdl_yaml in self.yaml_paths:
            # print(f"Parsing {dsdl_yaml} ...")
            self.clear_registry()
            yaml_info = self.extract_info_from_yml(dsdl_yaml, shuffle=self.shuffle)
            dsdl_py, sample_type, samples, global_info_type, global_info = yaml_info["dsdl_py"], yaml_info[
                "sample_type"], yaml_info["samples"], yaml_info["global_info_type"], yaml_info["global_info"]
            exec(dsdl_py, {})
            sample_type = self.parse_sample_type(sample_type)
            for sample in samples:
                sample = sample_type(file_reader=self.file_reader, **sample)
                sample = ImageVisualizePipeline(sample=sample, palette=self._palette, field_list=self.fields)
                vis_sample = sample.visualize()
                for _, vis_item in vis_sample.items():
                    self._ind += 1
                    yield vis_item

    def _init_file_reader(self):
        return LocalFileReader(self.media_dir)

    def _parse_length(self):
        res = 0
        for dsdl_yaml in self.yaml_paths:
            with open(dsdl_yaml, "r") as f:
                dsdl_info = yaml_load(f, Loader=YAMLSafeLoader)['data']
            if "sample-path" not in dsdl_info or dsdl_info["sample-path"] in ("local", "$local"):
                assert "samples" in dsdl_info, f"Key 'samples' is required in {dsdl_yaml}."
                samples = dsdl_info['samples']
            else:
                sample_path = dsdl_info["sample-path"]
                samples = load_samples(dsdl_yaml, sample_path)
            res += len(samples)
        return res

    @staticmethod
    def parse_sample_type(sample_type):
        sample_type = Util.extract_sample_type(sample_type)
        sample_type = STRUCT.get(sample_type)
        return sample_type

    @staticmethod
    def clear_registry():
        LABEL.clear()
        STRUCT.clear()
        CLASSDOMAIN.clear()

    @staticmethod
    def extract_info_from_yml(dsdl_yaml, shuffle=False):
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

        dsdl_py = dsdl_parse(dsdl_yaml, dsdl_library_path="")
        None if not shuffle else random.shuffle(samples)
        res = {
            "sample_type": sample_type,
            "global_info_type": global_info_type,
            "samples": samples,
            "global_info": global_info,
            "dsdl_py": dsdl_py
        }
        return res

    @staticmethod
    def get_yaml_for_cli(dataset_name):
        SPLIT_PREFIX = "set-"
        config_path = os.path.join(os.path.expanduser("~"), ".dsdl", "dsdl.json")
        with open(config_path, "r") as f:
            storage_info = json.load(f)["storage"]
        dataset_dir = None
        for storage in storage_info.values():
            if "path" not in storage:
                continue
            parent_dir = storage["path"]
            _dataset_dir = os.path.join(parent_dir, dataset_name)
            if os.path.isdir(_dataset_dir):
                dataset_dir = _dataset_dir
                break
        if dataset_dir is None:
            raise RuntimeError(
                f"Dataset '{dataset_name}' doesn't exist local, please download it use command 'odl-cli get'.")
        yml_dir = os.path.join(dataset_dir, "yml")
        if os.path.isdir(yml_dir) and len(os.listdir(yml_dir)) > 0:
            split_dir_names = [str(_) for _ in os.listdir(yml_dir) if
                               os.path.isdir(os.path.join(yml_dir, _)) and str(_).startswith(SPLIT_PREFIX)]
        else:
            FieldNotFoundWarning(f"'{yml_dir}' is not a directory or is empty, please check again.")
            return [], dataset_dir

        split_names = [_[len(SPLIT_PREFIX):] for _ in split_dir_names]
        yaml_names = [f"{_}.yaml" for _ in split_names]
        yaml_paths = [os.path.join(yml_dir, d, y) for d, y in zip(split_dir_names, yaml_names)]

        res = []
        for yml_path in yaml_paths:
            if not os.path.isfile(yml_path):
                FieldNotFoundWarning(f"'{yml_path}' not found, please check again.")
                continue
            res.append(yml_path)

        return res, dataset_dir


def studio_view(dataset_name, task_type):
    palette = dict()
    assert task_type in TASK_FIELDS, f"invalid task, you can only choose in {list(TASK_FIELDS.keys())}"
    fields = TASK_FIELDS[task_type]
    yaml_paths, media_dir = StudioView.get_yaml_for_cli(dataset_name)

    for dsdl_yaml in yaml_paths:
        print(f"Parsing {dsdl_yaml} ...")
        LABEL.clear()
        STRUCT.clear()
        CLASSDOMAIN.clear()
        config_dic = dict(type="LocalFileReader", working_dir=media_dir)
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

        dsdl_py = dsdl_parse(dsdl_yaml, dsdl_library_path="")
        exec(dsdl_py, {})

        dataset = Dataset(samples, sample_type, config_dic, global_info=global_info, global_info_type=global_info_type)
        for ind in range(len(dataset)):
            sample = ImageVisualizePipeline(sample=dataset[ind], palette=palette, field_list=fields)
            vis_sample = sample.visualize()
            for _, vis_item in vis_sample.items():
                yield vis_item
