from .base import BaseFileReader
from contextlib import contextmanager
import os


class CephFileReader(BaseFileReader):

    def __init__(self, working_dir):
        super().__init__(working_dir)
        try:
            import ceph
        except ImportError:
            raise ImportError('Please install ceph to enable CephBackend.')
        self._client = ceph.S3Client()

    @contextmanager
    def load(self, filepath):
        filepath = str(filepath)
        filepath = os.path.join(self.working_dir, filepath)
        value = self._client.Get(filepath)
        try:
            yield memoryview(value)
        finally:
            pass


class PetrelFileReader(BaseFileReader):
    def __init__(self, working_dir, enable_mc=True):
        super().__init__(working_dir)
        try:
            from petrel_client import client
        except ImportError:
            raise ImportError('Please install petrel_client to enable '
                              'PetrelBackend.')
        self._client = client.Client(enable_mc=enable_mc)

    def _format_path(self, filepath: str) -> str:
        """Convert a ``filepath`` to standard format of petrel oss.

        If the ``filepath`` is concatenated by ``os.path.join``, in a Windows
        environment, the ``filepath`` will be the format of
        's3://bucket_name\\image.jpg'. By invoking :meth:`_format_path`, the
        above ``filepath`` will be converted to 's3://bucket_name/image.jpg'.

        Args:
            filepath (str): Path to be formatted.
        """
        return re.sub(r'\\+', '/', filepath)

    def load(self, filepath):
        filepath = self._format_path(filepath)
        value = self._client.Get(filepath)
        try:
            yield memoryview(value)
        finally:
            pass
