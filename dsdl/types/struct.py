from .field import Field
from ..geometry import Attributes, STRUCT
from ..exception import ValidationError
from ..warning import FieldNotFoundWarning


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        required = dict()  # 所有必须填写的field对象
        optional = dict()  # 所有可不填写的field对象
        attr = dict()  # 所有是attribute的field对象
        mappings = dict()  # 所有的field对象

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
        self.attributes = Attributes()
        self.file_reader = file_reader
        self._keys = []
        if file_reader is not None:  # 说明是在赋值
            for k in self.__required__:
                if k not in kwargs:
                    FieldNotFoundWarning(f"Required field {k} is missing.")
                    continue
                setattr(self, k, kwargs[k])
                if k not in self.__attr__:
                    self._keys.append(k)
        for k in self.__optional__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
                if k not in self.__attr__:
                    self._keys.append(k)

        self["$attributes"] = self.attributes
        self._keys.append("$attributes")

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        if key not in self.__mappings__:
            self[key] = value
            return

        if hasattr(self.__mappings__[key], "set_file_reader"):
            self.__mappings__[key].set_file_reader(self.file_reader)
        try:
            if key in self.__attr__:
                self.attributes[key] = self.__mappings__[key].validate(value)
                return
            self[key] = self.__mappings__[key].validate(value)
        except ValidationError as error:
            raise ValidationError(f"Field '{key}' validation error: {error}.")

    def get_mapping(self):
        return self.__mappings__

    def keys(self):
        return tuple(self._keys)
