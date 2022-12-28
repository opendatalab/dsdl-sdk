from ...objectio import LocalFileReader
from .base_studio_view import BaseStudioView

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class LocalStudioView(BaseStudioView):
    def __init__(self, dataset_name, task_type, n=None, shuffle=False):
        super().__init__(dataset_name, task_type, n=n, shuffle=shuffle)

    def _init_file_reader(self):
        return LocalFileReader(self.media_dir)
