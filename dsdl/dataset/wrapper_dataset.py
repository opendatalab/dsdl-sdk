import os
import json
import time
import psutil
import copy

import matplotlib.pyplot as plt
from .base_dataset import Dataset
from yaml import load as yaml_load
from typing import Sequence, Union, Iterable
from terminaltables import AsciiTable
try:
    from torch.utils.data import Dataset as _Dataset
    from torch.utils.data import DataLoader, ConcatDataset
except:
    from ..warning import ImportWarning
    ImportWarning("'torch' is not installed.")
    
    class _Dataset:
        def __init__(self, *args, **kwargs):
            pass
    class DataLoader:
        def __init__(self, *args, **kwargs):
            pass
    class ConcatDataset:
        def __init__(self, *args, **kwargs):
            pass

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader

from ..parser import dsdl_parse
from .utils.commons import Util
from ..geometry import CLASSDOMAIN


def process_logging(process_name):
    def run_time(func):
        def wrap(self, *args1, **args2):
            p = psutil.Process(os.getpid())
            
            mem_start = p.memory_full_info().uss
            time_start = time.time()
            
            res = func(self, *args1, **args2)
            
            time_end = time.time()
            mem_end = p.memory_full_info().uss
            
            new_log = DotDict({
                "time_cost": float(time_end - time_start), 
                "memory_cost": mem_end - mem_start
            })
            self.log.update(process_name, new_log)
            return res
        return wrap
    return run_time


class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super(DotDict, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        if key not in self.keys():
            return None
        value = self[key]
        if isinstance(value, dict):
            value = DotDict(value)
        return value
    
    def __setattr__(self, key, value):
        self[key] = value


class Logger:
    def __init__(self, *args, **kwargs):
        self.logger = DotDict(*args, **kwargs)
            
    def update(self, key, new_dict):
        if key not in self.logger.keys():
            self.logger[key] = DotDict(new_dict)
        else:
            for log_item in self.logger[key].keys():
                self.logger[key][log_item] += new_dict[log_item]

    @property
    def info(self):
        info = {}
        for key, val in self.logger.items():
            new_val = {}
            for log_item, log_val in val.items():
                new_val[log_item] = self.num2human(log_val, log_item)
            info[key] = new_val
        return DotDict(info)
    
    @property
    def total(self):
        total = {}
        for key, val in self.logger.items():
            for log_item in val.keys():
                if log_item not in total.keys():
                    total[log_item] = val[log_item]
                else:
                    total[log_item] += val[log_item]
        
        for log_item in total.keys():
            total[log_item] = self.num2human(total[log_item], log_item)
        return DotDict(total)
    
    def __repr__(self):
        return json.dumps(self.info, indent=2)
    
    def num2human(self, var, num_type):
        if num_type == "memory_cost":
            if var < 0:
                var = -var
                if var <= 1024:
                    return f"-{round(var/1024, 2)} KB"
                elif var <= 1024**2:
                    return f"-{round(var/(1024**2), 2)} MB"
                else:
                    return f"-{round(var/(1024**3), 2)} GB"
            else:
                if var <= 1024:
                    return f"{round(var/1024, 2)} KB"
                elif var <= 1024**2:
                    return f"{round(var/(1024**2), 2)} MB"
                else:
                    return f"{round(var/(1024**3), 2)} GB"
        elif num_type == "time_cost":
            return time.strftime("%H:%M:%S", time.gmtime(var))
        else:
            print(f"num_type `{num_type}` not implemented yet !")
            return var
        
    def human2num(self, var, num_type):
        if num_type == "memory_cost":
            num = float(var[0:-3])
            units = var[-2:]
            if units == "KB":
                return int(num*1024)
            elif units == "MB":
                return int(num*1024**2)
            else:
                return int(num*1024**3)
        elif num_type == "time_cost":
            h,m,s = var.split(":")
            return 60*60*int(h) + 60*int(m) + int(s)
        else:
            print(f"num_type `{num_type}` not implemented yet !")
            return var
    
    def save(self, save_dir):
        assert save_dir.endswith(".json"), "save_dir must end with '.json' !"
        with open(save_dir, 'w') as load_f:    
            json.dump(self.logger, load_f)
        
    def load(self, json_file):
        if isinstance(json_file, dict):
            self.logger = DotDict(json_file)
        else:
            with open(json_file, 'r') as load_f:    
                parameters = json.load(load_f)
            self.logger = DotDict(parameters)
        
    def vis(self):
        x_items = []
        time_value = []
        mem_value = []
        time_hval = []
        mem_hval = []

        for key in self.logger.keys():
            x_items.append(key)
            time_value.append(self.logger[key]['time_cost'])
            time_hval.append(self.info[key]['time_cost'])
            
            mem_value.append(self.logger[key]['memory_cost'])
            mem_hval.append(self.info[key]['memory_cost'])

        x_items.append('total')
        time_value.append(sum(time_value))
        time_hval.append(self.total['time_cost'])
        mem_value.append(sum(mem_value))
        mem_hval.append(self.total['memory_cost'])

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111)
        plt.title('cost visualize')
        ax1 = plt.gca()  

        ax1.bar(x=x_items, height=time_value, width=0.3, color="g")
        ax.set_ylim(0,time_value[-1]*1.1)
        plt.xlabel("main process")
        plt.ylabel("time cost/s")
        for index, (value, hval) in enumerate(zip(time_value, time_hval)):
            ax1.text(index-0.15, value, hval)
        plt.legend(['time cost'], loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(x_items, mem_value, "c*-")
        plt.ylabel("memory cost/byte")
        for index, (value, hval) in enumerate(zip(mem_value, mem_hval)):
            ax2.text(index, value, hval)
        plt.legend(['memory cost'], loc='upper left', bbox_to_anchor=(0.002, 0.9))
        plt.show()
        
        
    def get_tabel(self, log1, log2, subset_name):
        table_data = []
        process = list(set(log1.info.keys()).union(log2.info.keys()))
        process.append("total")
        table_data.append(["main process", "self", "target"])

        for key in process:
            next_row = [key]
            if key != "total":
                val1 = log1.info[key][subset_name] if key in log1.info.keys() else "nan"
                val2 = log2.info[key][subset_name] if key in log2.info.keys() else "nan"
                next_row.extend([val1, val2])
            else:
                next_row.extend([log1.total[subset_name], log2.total[subset_name]])
            table_data.append(next_row)
        result = AsciiTable(table_data)
        return result.table

    def compare(self, target_log):
        res = ""
        for subset_name in ["time_cost", "memory_cost"]:
            res += f"compare of {subset_name}: \n"
            res += self.get_tabel(self, target_log, subset_name)
            res += "\n\n"
        return res
    
    
class DSDLDataset(Dataset):
    
    """Dataset for dsdl detection.
    Args:
        required_fields (list): List of required keys during training.
        dsdl_yaml (str): dsdl yaml file path, such as {path to dsdl}/set-train/train.yaml.
        location_config (dict): location config from config.py. for example:
            loc_config = dict(type="LocalFileReader", 
                              working_dir=f"/nvme/share_data/data/{data_name}/original")
        transform (dict): a pipline for every field in required_fields, for example:
            {"Image": lambda x: x[0].to_image().convert(mode='RGB')}, defaults to be `{}`.
        specific_key_path (dict): Path of specific key which can not
            be loaded by it's field name.
        lazy_init (bool): init and extract required fiedls untill use them, defaults to be `True`. 
    """
    
    YAML_VALID_SUFFIX = ('.yaml', '.YAML')
    JSON_VALID_SUFFIX = ('.json', '.JSON')
    VALID_SUFFIX = YAML_VALID_SUFFIX + JSON_VALID_SUFFIX

    def __init__(self, 
                 required_fields: list = [],
                 dsdl_yaml: str = "", 
                 location_config: dict = {},
                 transform: dict = {},
                 specific_key_path: dict = {},
                 lazy_init=True):

        self.log = Logger()
        
        if required_fields:
            self.required_fields = required_fields
        else:
            self.required_fields = ["Image", "Label", "Bbox", "Polygon", "LabelMap"]
        self._dsdl_yaml = dsdl_yaml
        self._location_config = location_config
        self.transform = transform
        self.specific_key_path = specific_key_path
        self.lazy_init = lazy_init

        self._yaml_info = self.extract_info_from_yml()
        dsdl_py, sample_type, samples, global_info_type, global_info = self._yaml_info["dsdl_py"], self._yaml_info[
            "sample_type"], self._yaml_info["samples"], self._yaml_info["global_info_type"], self._yaml_info[
                                                                           "global_info"]
        exec(dsdl_py, {})
        all_class_dom = Util.extract_class_dom(sample_type)
        self.class_dom = None
        this_class_dom = None
        for _arg in all_class_dom:
            if isinstance(all_class_dom[_arg], list):
                for _dom_ind, class_dom in enumerate(all_class_dom[_arg]):
                    this_class_dom = CLASSDOMAIN.get(class_dom)
                    all_class_dom[_arg][_dom_ind] = this_class_dom
            else:
                this_class_dom = CLASSDOMAIN.get(all_class_dom[_arg])
                all_class_dom[_arg] = this_class_dom
        self.class_dom = this_class_dom
        self.meta = self._yaml_info["meta"]
        self.version = self._yaml_info["version"]

        if not self.required_fields: 
            self.lazy_init = False
        super().__init__(samples, sample_type, location_config, None, global_info_type, global_info, self.lazy_init)
        
        self.data_list = self._load_data_list()

    @process_logging("load_sample")
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

        dsdl_py = dsdl_parse(dsdl_yaml, dsdl_library_path='')

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

    @process_logging("load_sample")
    def _load_sample(self):
        """
        init SampleStruct from dict sample, and save in sample_list
        """
        sample_list = []
        for i, sample in enumerate(self._samples):
            struct_sample = self.sample_type(sample)
            sample_list.append(self.process_sample(i, struct_sample))
        return sample_list
    
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
    
    @property
    def class_names(self) -> list:
        return [i.category_name for i in self.class_dom.__list__]
        
    def _parse_data_info(self, sample) -> dict:
        sample_info = {}

        for key in self.required_fields:
            # extract info by field name.
            info = sample.extract_field_info([key])
            if info[key]:
                sample_info[key] = info[key]
            
        for key in self.specific_key_path.keys():
            # extract info by specific key path.
            info = sample.extract_path_info(self.specific_key_path[key])
            if info:
                sample_info[key] = info
                
        return DotDict(sample_info)
    
    @process_logging("extract_data")
    def _load_data_list(self) -> list:
        """
        extract required data from sample_list.
        """
        data_list = []
        for sample in self.sample_list:
            sample_info = self._parse_data_info(sample)
            data_list.append(sample_info)
        return data_list
    
    def __getitem__(self, idx):
        data = {}
        for key, val in self.data_list[idx].items():
            if key in self.transform.keys():
                data[key] = self.transform[key](val)
            else:
                data[key] = val
        return DotDict(data)
    
    def __len__(self): 
        return len(self.data_list)
    
    @process_logging("pre_transform")
    def pre_transform(self, pre_transform):
        for idx, data in enumerate(self.data_list):
            for key, T in pre_transform.items():
                T = pre_transform.get(key, None)
                self.data_list[idx][key] = T(data[key])
        
    def set_transform(self, transform):
        self.transform = transform
        
    def to_pytorch(self, **args):
        """
        return a pytorch DataLoader.
        """
        return DataLoader(self, **args)
    

class DSDLConcatDataset(ConcatDataset):
    
    def __init__(self, datasets: Iterable[_Dataset]) -> None:
        super().__init__(datasets)
        self.class_dom = self.combine_class_doms()
        self.update_samples()
        
    def combine_class_doms(self):
        """
        conbine different class_doms.
        """
        for ds in self.datasets:
            cdom = ds.class_dom
        return cdom
    
    def update_samples(self):
        """
        when concate datasets which have different class_doms, 
        samples property(such as `Label`) may need to be updated. 
        """
        pass
    
    @property
    def class_names(self) -> list:
        """
        get dataset's class names.
        """
        return [i.category_name for i in self.class_dom.__list__]
    
    def pre_transform(self, pre_transform):
        for ds in self.datasets:
            ds.pre_transform(pre_transform)
        
    def set_transform(self, transform):
        for ds in self.datasets:
            ds.set_transform(transform)
        
    def to_pytorch(self, **args):
        return DataLoader(self, **args)