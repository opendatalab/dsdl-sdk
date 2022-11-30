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
from ..types import Struct
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
            sample_type: Union[str, Struct],
            location_config: dict,
            pipeline: Optional[Callable[[Dict], Dict]] = None,
    ):
        self.location_config = location_config
        self.pipeline = pipeline  # 处理样本的函数
        self.samples = samples  # 样本所在的yaml文件路径
        sample_type = Util.extract_sample_type(sample_type)
        if isinstance(sample_type, str):
            self.sample_type = STRUCT.get(sample_type)
        else:
            self.sample_type = sample_type
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
        for sample in self.samples:
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

    @property
    def config(self):
        return self.location_config

    @staticmethod
    def format_sample(sample):
        raise NotImplementedError
