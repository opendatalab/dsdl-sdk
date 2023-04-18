from .base_geometry import BaseGeometry
import numpy as np


class BBox3D(BaseGeometry):
    def __init__(self, value, mode):
        assert mode in ("indoor", "auto-drive")
        self._mode = mode
        if mode == "auto-drive":
            self._data = list(value) + [0., 0.]

    def to_array(self):
        if self.mode == "auto-drive":
            return np.array(self._data[:7])
        else:
            return np.array(self._data)

    @property
    def data(self):
        if self.mode == "auto-drive":
            return self._data[:7]
        else:
            return self._data

    @property
    def mode(self):
        return self._mode

    @property
    def x(self):
        return self._data[0]

    @property
    def y(self):
        return self._data[1]

    @property
    def z(self):
        return self._data[2]

    @property
    def length(self):
        return self._data[3]

    @property
    def width(self):
        return self._data[4]

    @property
    def height(self):
        return self._data[5]

    @property
    def yaw(self):
        return self._data[6]

    @property
    def pitch(self):
        return self._data[7]

    @property
    def roll(self):
        return self._data[8]

    @property
    def xmin(self):
        return self.x - self.length / 2

    @property
    def xmax(self):
        return self.x + self.length / 2

    @property
    def ymin(self):
        return self.y - self.width / 2

    @property
    def ymax(self):
        return self.y + self.width / 2

    @property
    def zmin(self):
        return self.z - self.height / 2

    @property
    def zmax(self):
        return self.z + self.height / 2

    @property
    def volumn(self):
        return self.length * self.width * self.height

    def __repr__(self):
        return f'BoundingBox3D(xmin={self.xmin}, ymin={self.ymin}, zmin={self.zmin}, xmax={self.xmax}, ymax={self.ymax}, zmax={self.zmax})'
