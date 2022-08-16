from .base_dataset import Dataset

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class DemoDataset(Dataset):

    def __getitem__(self, idx):
        return self.sample_list[idx]

    def _parse_struct(self, sample):
        return sample
