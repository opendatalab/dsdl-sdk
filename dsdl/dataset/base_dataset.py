import torch.utils.data
from yaml import load as yaml_load
from typing import Callable, Dict, Optional
from ..types import Struct, registry
from dsdl.dataset.utils import Util
import dsdl.objectio as objectio

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class Dataset(torch.utils.data.Dataset):
    # PALETTE用来存储每个类别的颜色（用于可视化）
    PALETTE = {}

    def __init__(
            self,
            sample_file: str,
            location_config: dict,
            pipeline: Optional[Callable[[Dict], Dict]] = None,
    ):
        self.location_config = location_config
        self.pipeline = pipeline  # 处理样本的函数
        self.sample_file = sample_file  # 样本所在的yaml文件路径
        self.file_reader = self._load_file_reader(location_config)  # 样本的路径配置（如本地路径或是阿里云路径）
        self.sample_list = self._load_sample()  # 将yaml文件中的样本内容加载到self.sample_list中

    @staticmethod
    def _load_file_reader(config):
        config = config.copy()
        type_ = config.pop("type")
        cls = getattr(objectio, type_)
        try:
            reader = cls(**config)
        except Exception as e:
            print(f"raise exception {e} whe parse the location config {config}.")
            raise e
        return reader

    def _load_sample(self):
        """
        该函数的作用是将yaml文件中的样本转换为Struct对象，并存储到sample_list列表中
        """
        sample_list = []
        with open(self.sample_file, "r") as f:
            data = yaml_load(f, Loader=YAMLSafeLoader)["data"]
            sample_type = Util.extract_sample_type(data["sample-type"])
            cls = registry.get_struct(sample_type)
            for item in data.items():
                if item[0] == "samples":
                    for sample in item[1]:
                        sample_list.append(self._parse_struct(cls(file_reader=self.file_reader, **sample)))
        return sample_list

    def _parse_struct(self, sample):
        if isinstance(sample, Struct):
            data_item = {"$extra": {}}
            struct_mapping = sample.get_mapping()
            for key in sample.keys():
                if key.startswith("_"):
                    continue
                if key not in struct_mapping:
                    data_item["$extra"][key] = sample[key]
                else:
                    field_key = Util.extract_key(struct_mapping[key])
                    if field_key in data_item:
                        data_item[field_key][key] = self._parse_struct(getattr(sample, key))
                    else:
                        data_item[field_key] = {key: self._parse_struct(getattr(sample, key))}
            return data_item

        elif isinstance(sample, list):
            return [self._parse_struct(item) for item in sample]
        else:
            return sample

    def process_sample(self, sample):
        return sample

    def __len__(self):
        return len(self.sample_list)

    def __getitem__(self, idx):
        sample = self.sample_list[idx]
        data = self.process_sample(sample)
        if self.pipeline is not None:
            data = self.pipeline(data)
        return data

    def get_sample_list(self):
        return self.sample_list

    @property
    def config(self):
        return self.location_config

    @staticmethod
    def format_sample(sample):
        raise NotImplementedError
