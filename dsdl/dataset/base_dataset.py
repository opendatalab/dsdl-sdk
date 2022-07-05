import re
from torch.utils.data import Dataset
from yaml import load as yaml_load
from typing import Callable, Dict, Optional, Tuple
from .. import types
from ..types import Struct
from ..types.field import Field

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class BaseDataset(Dataset):
    # PALETTE用来存储每个类别的颜色（用于可视化）
    PALETTE = {}

    def __init__(
            self,
            sample_file: str,
            config: dict,
            pipeline: Optional[Callable[[Dict], Dict]] = None,
            palette: Optional[Dict[str, Tuple]] = None):

        self.pipeline = pipeline  # 处理样本的函数
        self.sample_file = sample_file  # 样本所在的yaml文件路径
        self._config = config  # 样本的路径配置（如本地路径或是阿里云路径）
        self.sample_list = self._load_sample()  # 将yaml文件中的样本内容加载到self.sample_list中
        self.palette = self.PALETTE
        if palette:  # 如果用户自己定义了label调色盘，则更新默认的调色盘
            self.palette.update(palette)

    def _load_sample(self):
        """
        该函数的作用是将yaml文件中的样本转换为Struct对象，并存储到sample_list列表中
        """
        sample_list = []
        with open(self.sample_file, "r") as f:
            data = yaml_load(f, Loader=YAMLSafeLoader)["data"]
            sample_type = BaseDataset.extract_sample_type(data["sample-type"])
            cls = types.registry.get_struct(sample_type)
            for item in data.items():
                if item[0] == "samples":
                    for sample in item[1]:
                        sample_list.append(self._parse_struct(cls(dataset=self, **sample)))
        return sample_list

    @staticmethod
    def _parse_struct(sample):
        if isinstance(sample, Struct):
            data_item = {"extra": {}}
            struct_mapping = sample.get_mapping()
            for key in sample.keys():
                if key.startswith("_"):
                    continue
                if key not in struct_mapping:
                    data_item["extra"][key] = sample[key]
                else:
                    field_key = BaseDataset._extract_key(struct_mapping[key])
                    if field_key in data_item:
                        data_item[field_key][key] = BaseDataset._parse_struct(getattr(sample, key))
                    else:
                        data_item[field_key] = {key: BaseDataset._parse_struct(getattr(sample, key))}
            return data_item

        elif isinstance(sample, list):
            return [BaseDataset._parse_struct(item) for item in sample]
        else:
            return sample

    @staticmethod
    def _extract_key(field_obj: Field):
        field_cls_name = field_obj.__class__.__name__
        return field_cls_name.replace("Field", "").lower()

    def process_sample(self, sample):
        raise NotImplementedError

    def visualize(self, sample):
        raise NotImplementedError

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

    @staticmethod
    def _get_first_value(dic):
        if len(dic) == 0:
            return None
        for k in dic:
            return dic[k]

    @property
    def config(self):
        return self._config

    @staticmethod
    def format_sample(sample):
        raise NotImplementedError

    @staticmethod
    def extract_sample_type(sample_type):
        c_dom = re.findall(r"\[(.*?)\]", sample_type)
        if c_dom:
            return sample_type.replace("[" + c_dom[0] + "]", "", 1).strip()
        else:
            return sample_type
