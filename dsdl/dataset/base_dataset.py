from torch.utils.data import Dataset
from yaml import load as yaml_load
from typing import Callable, Dict, Optional, Union, Tuple
from .. import types

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class BaseDataset(Dataset):
    # KEY_MAPPING: yaml文件中定义的字段名称和dataset内部字段名称的对应关系，
    # 比如下面的实例表示yaml中sample中的media字段对应了dataset中的$media字段
    KEY_MAPPING = {
        "$media": "media",
        "$annotation": "annotation"
    }
    # PALETTE用来存储每个类别的颜色（用于可视化）
    PALETTE = {}

    def __init__(
            self,
            sample_file: str,
            config: dict,
            key_mapping_file: Optional[Union[str, Dict]] = None,
            pipeline: Optional[Callable[[Dict], Dict]] = None,
            palette: Optional[Dict[str, Tuple]] = None):

        self.key_mapping = self.KEY_MAPPING.copy()
        self.pipeline = pipeline  # 处理样本的函数
        self._set_key_mapping(key_mapping_file)  # 将用户定义的key_mapping与默认的key_mapping融合
        self.sample_file = sample_file  # 样本所在的yaml文件路径
        self._config = config  # 样本的路径配置（如本地路径或是阿里云路径）
        self.sample_list = self._load_sample()  # 将yaml文件中的样本内容加载到self.sample_list中
        self.palette = self.PALETTE
        if palette:  # 如果用户自己定义了label调色盘，则更新默认的调色盘
            self.palette.update(palette)

    def _set_key_mapping(self, key_mapping_file):
        """
        该函数的作用是，如果用户自己提供了key_mapping_file，则需要用其更新self.key_mapping
        """
        BaseDataset._normalize_dict(self.key_mapping)
        if key_mapping_file is not None:
            if isinstance(key_mapping_file, str):
                with open(key_mapping_file, "r") as f:
                    key_mapping_new = yaml_load(f, Loader=YAMLSafeLoader)
            elif isinstance(key_mapping_file, dict):
                key_mapping_new = key_mapping_file
            else:
                raise ValueError("Wrong type! The key_mapping_file can only be a string or dict.")
            BaseDataset._normalize_dict(key_mapping_new)
            BaseDataset._update_dict(self.key_mapping, key_mapping_new)

    def _load_sample(self):
        """
        该函数的作用是将yaml文件中的样本转换为Struct对象，并存储到sample_list列表中
        """
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

    def visualize(self, sample):
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

    @staticmethod
    def _normalize_dict(dic):
        """
        该函数的作用是将{"mapping_key":"mapping_value"}转换为
        {"mapping_key":{"$key": "mapping_value"}}的标准形式
        """
        for k in dic:
            if k == "$key" and not isinstance(dic[k], str):
                raise ValueError("`$key`'s value must be a string!!")
            elif isinstance(dic[k], dict):
                BaseDataset._normalize_dict(dic[k])
            elif isinstance(dic[k], str) and k != "$key":
                dic[k] = {"$key": dic[k]}

    @staticmethod
    def _update_dict(dic_A, dic_B):
        """
        该函数的作用是将dic_B融合进dic_A当中，在融合前，需要调用_normalize_dict方法将dic_B和dic_A都进行标准化
        """
        for k_b in dic_B:
            if isinstance(dic_B[k_b], str):
                dic_A[k_b] = dic_B[k_b]
            elif isinstance(dic_B[k_b], dict):
                BaseDataset._update_dict(dic_A[k_b], dic_B[k_b])

    @staticmethod
    def format_sample(sample):
        raise NotImplementedError
