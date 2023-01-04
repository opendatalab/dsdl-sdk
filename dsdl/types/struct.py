import re
import os
from fnmatch import fnmatch
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
        struct_mappings = dict()  # 所有的Struct对象

        for k, v in attributes.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.is_attr:
                    attr[k] = v
                if v.is_optional:
                    optional[k] = v
                else:
                    required[k] = v
            elif isinstance(v, Struct):
                struct_mappings[k] = v

        for k in required.keys():
            attributes.pop(k)
        for k in optional.keys():
            attributes.pop(k)
        for k in struct_mappings.keys():
            attributes.pop(k)

        attributes["__required__"] = required
        attributes["__attr__"] = attr
        attributes["__optional__"] = optional
        attributes["__mappings__"] = mappings
        attributes["__struct_mappings__"] = struct_mappings

        new_class = super_new(mcs, name, bases, attributes)
        STRUCT.register(name, new_class)
        return new_class


class Struct(dict, metaclass=StructMetaclass):
    def __init__(self, file_reader=None, **kwargs):

        super().__init__()
        self.attributes = Attributes()
        self.file_reader = file_reader
        self._keys = []
        self._dict_format = None
        self._flatten_format = None
        self._raw_dict = kwargs
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
        for k in self.__struct_mappings__:
            if k not in kwargs:
                FieldNotFoundWarning(f"Required struct instance {k} is missing.")
                continue
            setattr(self, k, kwargs[k])
            self._keys.append(k)

        self["$attributes"] = self.attributes
        self._keys.append("$attributes")

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):

        if key in self.__mappings__:
            if hasattr(self.__mappings__[key], "set_file_reader"):
                self.__mappings__[key].set_file_reader(self.file_reader)
            try:
                if key in self.__attr__:
                    self.attributes[key] = self.__mappings__[key].validate(value)
                    return
                self[key] = self.__mappings__[key].validate(value)
            except ValidationError as error:
                raise ValidationError(f"Field '{key}' validation error: {error}.")
        elif key in self.__struct_mappings__:
            cls = self.__struct_mappings__[key].__class__
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Struct validation error: {cls.__name__} requires a dict to initiate, but got '{value}'.")
            self[key] = cls(file_reader=self.file_reader, **value)
        else:
            self[key] = value
            return

    def get_mapping(self):
        return self.__mappings__

    def get_struct_mapping(self):
        return self.__struct_mappings__

    def keys(self):
        return tuple(self._keys)

    def convert2dict(self):
        """
        Convert struct instance to a dict like:
             sample = {
                "$image": {"img2": img_obj, "img1":img_obj},
                "$list": {"objects": [{"$image": {"img1": img_obj}, "$bbox": {"box": box_obj}}],
                            "object2": [{"$bbox":{"box": box_obj}}, {"$bbox":{"box": box_obj}}], },
                "$struct": {
                    "struct1": {
                        "$image": {"img3": img_obj, "img4": img_obj}
                    "struct2": {
                        "$image": {"img4": img_obj}}
                    }
                }
            }
        """
        if self._dict_format is None:
            self._dict_format = self._parse_struct(self)
        return self._dict_format

    def extract_path_info(self, pattern, field_keys=None):
        magic_check = re.compile('([*?[])')
        if field_keys is None:
            if self._flatten_format is None:
                self._flatten_format = self.flatten_sample()
            flatten_sample = self._flatten_format
        else:
            if not isinstance(field_keys, list):
                field_keys = [field_keys]
            flatten_sample = dict()
            field_keys = [{_.lower()} for _ in field_keys if isinstance(_, str)]
            res = self.extract_field_info(field_keys)
            for field_info in res.values():
                flatten_sample.update(field_info)
        if magic_check.search(pattern) is None:  # 无通配
            if pattern in flatten_sample:
                return {pattern: flatten_sample[pattern]}
            else:
                return dict()
        res = dict()
        for path in flatten_sample.keys():
            if self._match(path, pattern):
                res[path] = flatten_sample[path]
        return res

    @staticmethod
    def _match(path, pattern):
        path = os.path.normpath(path)
        path_seg = path.split(os.sep)
        pattern = os.path.normpath(pattern)
        pattern_seg = pattern.split(os.sep)
        if len(path_seg) != len(pattern_seg):
            return False
        for pattern_, path_ in zip(pattern_seg, path_seg):
            if not fnmatch(path_, pattern_):
                return False
        return True

    def extract_field_info(self, field_lst):
        """
        Extract the field info given field list, for example, if field_lst is [bbox, image], the result will be:

            {
                ”image": {
                    "./img2": img_obj,
                    "./img1": img_obj,
                    "./objects/0/img1": img_obj,
                },
                "bbox": {
                    "./objects/0/box": box_obj,
                    "./object2/0/box": box_obj,
                    "./object2/1/box": box_obj
                }
            }
        """
        res = self.flatten_sample([f"${field_name}" for field_name in field_lst])
        result_dic = {k.strip("$"): v for k, v in res.items()}
        for field in field_lst:
            result_dic.setdefault(field, {})
        return result_dic

    def flatten_sample(self, field_name=None, parse_method=lambda _: _):
        result_dic = {}
        prefix = "."
        if isinstance(field_name, str):
            field_name = [field_name]
        assert field_name is None or (
                isinstance(field_name, list) and "$struct" not in field_name and "$list" not in field_name and all(
            [isinstance(_, str) for _ in field_name])), f"invalid fiend_name, got '{field_name}'."
        self._parse_helper(self.convert2dict(), result_dic, field_name, prefix, parse_method)
        return result_dic

    def convert2json(self):
        return self._raw_dict

    @classmethod
    def _parse_struct(cls, sample):
        if isinstance(sample, Struct):
            data_item = {}
            field_mapping = sample.get_mapping()  # all fields
            struct_mapping = sample.get_struct_mapping()  # all structs
            for key in sample.keys():
                if key.startswith("$"):  # attributes
                    field_key = key
                    key = key.replace("$", "")
                    if field_key in data_item:
                        data_item[field_key][key] = getattr(sample, field_key)
                    else:
                        data_item[field_key] = {key: getattr(sample, field_key)}
                elif key in field_mapping:  # fields
                    field_obj = getattr(sample, key)
                    field_key = field_mapping[key].extract_key()
                    if field_key in data_item:
                        data_item[field_key][key] = cls._parse_struct(field_obj)
                    else:
                        data_item[field_key] = {key: cls._parse_struct(field_obj)}
                elif key in struct_mapping:  # struct
                    struct_key = "$struct"
                    if struct_key in data_item:
                        data_item[struct_key][key] = cls._parse_struct(getattr(sample, key))
                    else:
                        data_item[struct_key] = {key: cls._parse_struct(getattr(sample, key))}

            return data_item

        elif isinstance(sample, list):
            return [cls._parse_struct(item) for item in sample]
        else:
            return sample

    @classmethod
    def _parse_helper(cls, sample, result_dic, field_name=None, prefix=".", parse_method=lambda _: _):

        if isinstance(sample, dict):
            for field_type in sample:
                if (field_name is None and field_type not in ("$struct", "$list")) or (
                        field_name is not None and field_type in field_name):
                    for key, value in sample[field_type].items():
                        k_ = f"{prefix}/{key}"
                        tmp_dic = result_dic.setdefault(field_type, {}) if field_name is not None else result_dic
                        tmp_dic[k_] = parse_method(value)
                elif field_type == "$list":
                    for key, value in sample[field_type].items():
                        k_ = f"{prefix}/{key}"
                        cls._parse_helper(value, result_dic, field_name=field_name, prefix=k_,
                                          parse_method=parse_method)
                elif field_type == "$struct":
                    for key, value in sample[field_type].items():
                        k_ = f"{prefix}/{key}"
                        cls._parse_helper(value, result_dic, field_name=field_name, prefix=k_,
                                          parse_method=parse_method)

        elif isinstance(sample, list):
            for id_, item in enumerate(sample):
                k_ = f"{prefix}/{id_}"
                cls._parse_helper(item, result_dic, field_name=field_name, prefix=k_, parse_method=parse_method)
