from .field import Field
from ..geometry import Attributes
from .registry import STRUCT
from ..exception import ValidationError


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        required = dict()
        optional = dict()
        attr = dict()
        mappings = dict()

        for k, v in attributes.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.is_attr:
                    attr[k] = v
                if v.is_optional:
                    optional[k] = v
                else:
                    required[k] = v

        for k in required.keys():
            attributes.pop(k)
        for k in optional.keys():
            attributes.pop(k)

        attributes["__required__"] = required
        attributes["__attr__"] = attr
        attributes["__optional__"] = optional
        attributes["__mappings__"] = mappings

        new_class = super_new(mcs, name, bases, attributes)
        STRUCT.register(name, new_class)
        return new_class


class Struct(dict, metaclass=StructMetaclass):
    def __init__(self, file_reader=None, **kwargs):

        super().__init__()
        self.attributes = Attributes
        self.file_reader = file_reader
        self._keys = []
        for k in self.__required__:
            if k not in kwargs:
                raise AttributeError(f"The field {k} is required.")
            setattr(self, k, kwargs[k])
            self._keys.append(k)
        for k in self.__optional__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
                self._keys.append(k)

        setattr(self, "$attributes", self.attributes)
        self._keys.append("$attributes")

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):

        if hasattr(self.__mappings__[key], "set_file_reader"):
            self.__mappings__[key].set_file_reader(self.file_reader)
        try:
            if key in self.__attr__:
                setattr(self.attributes, key, self.__mappings__[key].validate(value))
                return
            self[key] = self.__mappings__[key].validate(value)
        except ValidationError as error:
            raise ValidationError(f"Field '{key}' validation error: {error}.")

    def get_mapping(self):
        return self.__mappings__

    def keys(self):
        return tuple(self._keys)
