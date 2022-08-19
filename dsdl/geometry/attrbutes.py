class Attributes:
    def __init__(self, **kwargs):
        self.container = {}
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        self.container[key] = value

    def __getattr__(self, key):
        try:
            return self.container[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __getitem__(self, item):
        return self.container[item]

    def keys(self):
        return self.container.keys()

    def values(self):
        return self.container.values()

    def __repr__(self):
        return self.container.__repr__()
