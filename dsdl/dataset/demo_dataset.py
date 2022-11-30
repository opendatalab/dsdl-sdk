from .base_dataset import Dataset


class DemoDataset(Dataset):

    def __getitem__(self, idx):
        return self.sample_list[idx]
