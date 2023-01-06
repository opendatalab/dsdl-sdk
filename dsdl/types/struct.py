import re
import os
from fnmatch import translate
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
        mappings = dict()  # 所有的field对象
        struct_mappings = dict()  # 所有的Struct对象

        for k, v in attributes.items():
            if isinstance(v, Field):
                mappings[k] = v
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
        attributes["__optional__"] = optional
        attributes["__mappings__"] = mappings
        attributes["__struct_mappings__"] = struct_mappings

        new_class = super_new(mcs, name, bases, attributes)
        STRUCT.register(name, new_class)
        return new_class


class Struct(dict, metaclass=StructMetaclass):
    def __init__(self, file_reader=None, prefix=".", **kwargs):

        super().__init__()
        self.attributes = Attributes()
        self.file_reader = file_reader
        self._keys = []
        self._dict_format = None
        self._flatten_format = dict()
        self._raw_dict = kwargs
        self._prefix = prefix

        for k in self.__required__:
            if k not in kwargs:
                FieldNotFoundWarning(f"Required field {k} is missing.")
                continue
            setattr(self, k, kwargs[k])
            self._keys.append(k)
        for k in self.__optional__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
                self._keys.append(k)
        for k in self.__struct_mappings__:
            if k not in kwargs:
                FieldNotFoundWarning(f"Required struct instance {k} is missing.")
                continue
            setattr(self, k, kwargs[k])
            self._keys.append(k)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):

        if key in self.__mappings__:  # field
            field_obj = self.__mappings__[key]
            if hasattr(field_obj, "set_file_reader"):
                field_obj.set_file_reader(self.file_reader)
            if hasattr(field_obj, "set_prefix"):
                field_obj.set_prefix(f"{self._prefix}/{key}")
            try:
                geometry_obj = field_obj.validate(value)
            except ValidationError as error:
                raise ValidationError(f"Field '{key}' validation error: {error}.")
            self[key] = geometry_obj
            field_key = field_obj.extract_key()
            if field_key != "$list":
                path = f"{self._prefix}/{key}"
                tmp_field_dic = self._flatten_format.setdefault(field_key, {})
                tmp_field_dic[path] = geometry_obj
                return
            if isinstance(field_obj.ele_type, Field):
                tmp_field_dic = self._flatten_format.setdefault(field_key, {})
                for ind, geometry_item in enumerate(geometry_obj):
                    path = f"{self._prefix}/{key}/{ind}"
                    tmp_field_dic[path] = geometry_item
                return
            if isinstance(field_obj.ele_type, Struct):
                for struct_item in geometry_obj:
                    this_flatten_format = struct_item.flatten_sample()
                    for this_field_key, this_field_value in this_flatten_format.items():
                        this_tmp_field_dic = self._flatten_format.setdefault(this_field_key, {})
                        this_tmp_field_dic.update(this_field_value)
                return

        elif key in self.__struct_mappings__:  # struct
            cls = self.__struct_mappings__[key].__class__
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Struct validation error: {cls.__name__} requires a dict to initiate, but got '{value}'.")
            struct_obj = cls(file_reader=self.file_reader, prefix=f"{self._prefix}/{key}", **value)
            self[key] = struct_obj
            this_flatten_format = struct_obj.flatten_sample()
            for this_field_key, this_field_value in this_flatten_format.items():
                this_tmp_field_dic = self._flatten_format.setdefault(this_field_key, {})
                this_tmp_field_dic.update(this_field_value)
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
        def _is_magic(p):
            return "[" in p or "]" in p or "*" in p or "?" in p

        if field_keys is None:
            flatten_sample = self.flatten_sample()
        else:
            if not isinstance(field_keys, list):
                field_keys = [field_keys]
            field_keys = [_.lower() for _ in field_keys if isinstance(_, str)]
            flatten_sample = self.extract_field_info(field_keys)
        if not _is_magic(pattern):  # 无通配
            for field_info in flatten_sample.values():
                if pattern in field_info:
                    return {pattern: field_info[pattern]}
            else:
                return dict()
        res = dict()
        # pattern = re.compile(translate(os.path.normcase(pattern))).match
        pattern = os.path.normpath(pattern)
        pattern_seg = pattern.split(os.sep)
        pattern_seg = [re.compile(translate(_)) if _is_magic(_) else _ for _ in pattern_seg]
        for field_info in flatten_sample.values():
            for path in field_info.keys():
                if self._match(path, pattern_seg):
                    res[path] = field_info[path]
        return res

    @staticmethod
    def _match(path, pattern_seg):
        path = os.path.normpath(path)
        path_seg = path.split(os.sep)

        if len(path_seg) != len(pattern_seg):
            return False
        for pattern_, path_ in zip(pattern_seg, path_seg):
            if ((not isinstance(pattern_, str)) and pattern_.match(path_) is None) or (
                    isinstance(pattern_, str) and pattern_ != path_):
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
        flatten_sample = self.flatten_sample()
        result_dic = {}
        for field in field_lst:
            result_dic[field] = flatten_sample.get(f"${field}", {})
        return result_dic

    def flatten_sample(self):
        if self._flatten_format:
            return self._flatten_format
        result_dic = {}
        self._parse_helper(self.convert2dict(), result_dic)
        self._flatten_format = result_dic
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

                if key in field_mapping:  # fields
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
                        tmp_dic = result_dic.setdefault(field_type, {})
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
