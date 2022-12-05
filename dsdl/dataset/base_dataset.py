try:
    from torch.utils.data import Dataset as Dataset_
except ImportError:
    from ..warning import ImportWarning

    ImportWarning("'torch' is not installed.")


    class Dataset_:
        def __len__(self):
            pass

        def __getitem__(self, item):
            pass
from ..types import Struct, StructMetaclass
from ..geometry import STRUCT
from dsdl.dataset.utils import Util
import dsdl.objectio as objectio
from typing import List, Dict, Any, Callable, Optional, Union

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class Dataset(Dataset_):
    # PALETTE用来存储每个类别的颜色（用于可视化）
    PALETTE = {}

    def __init__(
            self,
            samples: List[Dict[str, Any]],
            sample_type: Union[str, StructMetaclass],
            location_config: dict,
            pipeline: Optional[Callable[[Dict], Dict]] = None,
            global_info_type: Union[str, StructMetaclass] = None,
            global_info: Dict[str, Any] = None
    ):
        self.location_config = location_config
        self.pipeline = pipeline  # 处理样本的函数
        self._samples = samples  # 样本所在的yaml文件路径
        self._global_info = global_info

        if isinstance(sample_type, str):
            sample_type = Util.extract_sample_type(sample_type)
            self.sample_type = STRUCT.get(sample_type)
        elif issubclass(sample_type, Struct):
            self.sample_type = sample_type
        else:
            raise RuntimeError("sample_type must be a string or a Struct class")

        if global_info_type is not None:
            if isinstance(global_info_type, str):
                global_info_type = Util.extract_sample_type(global_info_type)
                self.global_info_type = STRUCT.get(global_info_type)
            elif issubclass(global_info_type, Struct):
                self.global_info_type = global_info_type
            else:
                raise RuntimeError("global_info_type must be a string or a Struct class")
        else:
            self.global_info_type = None

        self.file_reader = self._load_file_reader(location_config)  # 样本的路径配置（如本地路径或是阿里云路径）
        self.global_info = self._load_global_info()
        self.sample_list = self._load_sample()  # 将yaml文件中的样本内容加载到self.sample_list中
        self._has_global_info = self.global_info is not None

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

    def has_global_info(self):
        return self._has_global_info

    def _load_global_info(self):
        if self.global_info_type is not None and self._global_info is not None:
            global_info = self.global_info_type(file_reader=self.file_reader, **self._global_info)
            return global_info
        else:
            return None

    def _load_sample(self):
        """
        该函数的作用是将yaml文件中的样本转换为Struct对象，并存储到sample_list列表中
        """
        sample_list = []
        for sample in self._samples:
            sample_list.append(self.sample_type(file_reader=self.file_reader, **sample))
        return sample_list

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

    def get_global_info(self):
        return self.global_info

    @property
    def config(self):
        return self.location_config

    @staticmethod
    def format_sample(sample):
        raise NotImplementedError
