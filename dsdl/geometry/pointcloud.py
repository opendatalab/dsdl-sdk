import io
from .base_geometry import BaseGeometry
import numpy as np


class PointCloud(BaseGeometry):

    def __init__(self, value, file_reader, load_dim):
        self.load_dim = load_dim
        self._loc = value
        self._reader = file_reader
        self.namespace = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        self._reader = struct_obj.file_reader

    @property
    def location(self):
        return self._loc

    def to_bytes(self):
        return io.BytesIO(self._reader.read(self._loc))

    def to_array(self):
        points = np.frombuffer(self.to_bytes().read(), dtype=np.float32)
        return points.reshape(-1, self.load_dim)

    def __repr__(self):
        return f"point cloud path: {self.location}"
