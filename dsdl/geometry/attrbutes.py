from .base_geometry import BaseGeometry

class Attributes(BaseGeometry):
    def __init__(self, **kwargs):
        self.container = {}
        for k, v in kwargs.items():
            self.container[k] = v

    def __setitem__(self, key, value):
        self.container[key] = value

    def __getitem__(self, item):
        return self.container[item]

    def __contains__(self, item):
        return item in self.container

    def keys(self):
        return self.container.keys()

    def values(self):
        return self.container.values()

    def __repr__(self):
        return self.container.__repr__()

    @property
    def field_key(self):
        return "Attributes"
