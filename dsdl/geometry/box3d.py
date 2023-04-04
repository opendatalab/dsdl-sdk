from .base_geometry import BaseGeometry


class BBox3D(BaseGeometry):
    def __init__(self, value):
        self._data = value

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
    def alpha(self):
        return self._data[6]

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
