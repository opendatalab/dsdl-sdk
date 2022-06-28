from yaml import load as yaml_load
from dsdl import types


try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class Dataset(object):
    def __init__(self, sample_file: str, config: dict):
        self.sample_file = sample_file
        self._config = config
        self._load_sample()

    def _load_sample(self):
        sample_list = []
        with open(self.sample_file, "r") as f:
            data = yaml_load(f, Loader=YAMLSafeLoader)["data"]
            sample_type = data["sample-type"]
            for item in data.items():
                if item[0] == "samples":
                    for sample in item[1]:
                        cls = types.registry.get_struct(sample_type)
                        sample_list.append(cls(dataset=self, **sample))
        self.sample_list = sample_list

    def __len__(self):
        return len(self.sample_list)

    def __getitem__(self, idx):
        return self.sample_list[idx]

    def get_sample_list(self):
        return self.sample_list

    @property
    def config(self):
        return self._config
