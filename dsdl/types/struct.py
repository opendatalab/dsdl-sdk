from .field import Field
from .unstructure import UnstructuredObjectField
from .registry import registry


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        mappings = dict()
        for k, v in attributes.items():
            if isinstance(v, Field):
                mappings[k] = v
        for k in mappings.keys():
            attributes.pop(k)
        attributes["__mappings__"] = mappings
        new_class = super_new(mcs, name, bases, attributes)
        registry.register(name, new_class)
        return new_class


class Struct(dict, metaclass=StructMetaclass):
    def __init__(self, dataset, **kwargs):
        super().__init__()
        self.dataset = dataset
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        if key not in self.__mappings__:
            self[key] = value
            return

        if isinstance(self.__mappings__[key], UnstructuredObjectField):
            self.__mappings__[key].set_dataset(self.dataset)
        self[key] = self.__mappings__[key].validate(value)
