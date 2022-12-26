from .base_dataset import Dataset
from yaml import load as yaml_load
from typing import Sequence, Union

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
import os
import json
from ..parser import dsdl_parse
from .utils.commons import Util
from ..geometry import CLASSDOMAIN


class DSDLDataset(Dataset):
    YAML_VALID_SUFFIX = ('.yaml', '.YAML')
    JSON_VALID_SUFFIX = ('.json', '.JSON')
    VALID_SUFFIX = YAML_VALID_SUFFIX + JSON_VALID_SUFFIX

    def __init__(self, dsdl_yaml, location_config, import_dir=''):
        self._dsdl_yaml = dsdl_yaml
        self._location_config = location_config
        self._import_dir = import_dir

        self._yaml_info = self.extract_info_from_yml()
        dsdl_py, sample_type, samples, global_info_type, global_info = self._yaml_info["dsdl_py"], self._yaml_info[
            "sample_type"], self._yaml_info["samples"], self._yaml_info["global_info_type"], self._yaml_info[
                                                                           "global_info"]
        exec(dsdl_py, {})
        self.class_dom = Util.extract_class_dom(sample_type)
        for _arg in self.class_dom:
            for _dom_ind, class_dom in enumerate(self.class_dom[_arg]):
                self.class_dom[_arg][_dom_ind] = CLASSDOMAIN.get(class_dom)
        self.meta = self._yaml_info["meta"]
        self.version = self._yaml_info["version"]

        super().__init__(samples, sample_type, location_config, None, global_info_type, global_info)

    def extract_info_from_yml(self):
        dsdl_yaml = self._dsdl_yaml
        with open(dsdl_yaml, "r") as f:
            dsdl_all_info = yaml_load(f, Loader=YAMLSafeLoader)
        dsdl_info, dsdl_meta, dsdl_version = dsdl_all_info['data'], dsdl_all_info["meta"], dsdl_all_info[
            "$dsdl-version"]
        sample_type = dsdl_info['sample-type']
        global_info_type = dsdl_info.get("global-info-type", None)
        global_info = None
        if "sample-path" not in dsdl_info or dsdl_info["sample-path"] in ("local", "$local"):
            assert "samples" in dsdl_info, f"Key 'samples' is required in {dsdl_yaml}."
            samples = dsdl_info['samples']
        else:
            sample_path = dsdl_info["sample-path"]
            samples = self.load_samples(dsdl_yaml, sample_path)
        if global_info_type is not None:
            if "global-info-path" not in dsdl_info:
                assert "global-info" in dsdl_info, f"Key 'global-info' is required in {dsdl_yaml}."
                global_info = dsdl_info["global_info"]
            else:
                global_info_path = dsdl_info["global-info-path"]
                global_info = self.load_samples(dsdl_yaml, global_info_path, "global-info")[0]

        dsdl_py = dsdl_parse(dsdl_yaml, dsdl_library_path=self._import_dir)

        res = {
            "sample_type": sample_type,
            "global_info_type": global_info_type,
            "samples": samples,
            "global_info": global_info,
            "dsdl_py": dsdl_py,
            "version": dsdl_version,
            "meta": dsdl_meta
        }
        return res

    @classmethod
    def load_samples(cls, dsdl_path: str, path: Union[str, Sequence[str]], extract_key="samples"):
        samples = []
        paths = []
        dsdl_dir = os.path.split(dsdl_path)[0]
        if isinstance(path, str):
            path = os.path.join(dsdl_dir, path)
            if os.path.isdir(path):
                paths = [os.path.join(path, _) for _ in os.listdir(path) if _.endswith(cls.VALID_SUFFIX)]
            elif os.path.isfile(path):
                if path.endswith(cls.VALID_SUFFIX):
                    paths = [path]
        elif isinstance(path, (list, tuple)):
            paths = [os.path.join(dsdl_dir, _) for _ in path if os.path.isfile(_) and _.endswith(cls.VALID_SUFFIX)]
        for p in paths:
            if p.endswith(cls.YAML_VALID_SUFFIX):
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
