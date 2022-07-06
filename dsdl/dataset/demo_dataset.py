from .base_dataset import BaseDataset


try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class DemoDataset(BaseDataset):

    def __getitem__(self, idx):
        return self.sample_list[idx]

    @staticmethod
    def _parse_struct(sample):
        return sample
