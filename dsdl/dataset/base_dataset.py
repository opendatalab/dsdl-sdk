from torch.utils.data import Dataset
from yaml import load as yaml_load
from typing import Callable, Dict, Optional, Union
from .. import types

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class BaseDataset(Dataset):
    KEY_MAPPING = {
        "$media": "media",
        "$annotation": "annotation"
    }

    def __init__(
            self,
            sample_file: str,
            config: dict,
            key_mapping_file: Optional[Union[str, Dict]] = None,
            pipeline: Optional[Callable[[Dict], Dict]] = None):

        self.key_mapping = self.KEY_MAPPING.copy()
        self.pipeline = pipeline
        self._set_key_mapping(key_mapping_file)
        self.sample_file = sample_file
        self._config = config
        self.sample_list = self._load_sample()

    def _set_key_mapping(self, key_mapping_file):
        if key_mapping_file is not None:
            if isinstance(key_mapping_file, str):
                with open(key_mapping_file, "r") as f:
                    self.key_mapping.update(yaml_load(f, Loader=YAMLSafeLoader))
            elif isinstance(key_mapping_file, dict):
                self.key_mapping.update(key_mapping_file)
            else:
                raise ValueError("Wrong type! The key_mapping_file can only be a string or dict.")

    def _load_sample(self):
        sample_list = []
        with open(self.sample_file, "r") as f:
            data = yaml_load(f, Loader=YAMLSafeLoader)["data"]
            sample_type = data["sample-type"]
            cls = types.registry.get_struct(sample_type)
            for item in data.items():
                if item[0] == "samples":
                    for sample in item[1]:
                        sample_list.append(cls(dataset=self, **sample))
        return sample_list

    def parse_struct(self, sample):
        raise NotImplementedError

    @staticmethod
    def visualize(sample):
        raise NotImplementedError

    def __len__(self):
        return len(self.sample_list)

    def __getitem__(self, idx):
        sample = self.sample_list[idx]
        data = self.parse_struct(sample)
        if self.pipeline is not None:
            data = self.pipeline(data)
        return data

    def get_sample_list(self):
        return self.sample_list

    @staticmethod
    def get_field_name(value):
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return value["$key"]
        else:
            raise ValueError("Wrong type! The field information can only be a string or a dict.")

    @property
    def config(self):
        return self._config
