import re
import os
from fnmatch import translate
from .field import Field
from ..geometry import Attributes, STRUCT
from ..exception import ValidationError
from ..warning import FieldNotFoundWarning


class RegisterPattern:
    """
    {
        './a/b/*/[1-9]/*': {
            "$bbox": [('./a/b/det/%d/box', 1), ('./a/b/ann/%d/box', 1)]
            "$label": [('./a/b/det/[1-9]/cate', 1), ('./a/b/ann/[1-9]/cate', 1)]
        }
    }
    """

    def __init__(self):
        self.flatten_struct = None
        self.registered_patterns = dict()

    def set_flatten_struct(self, flatten_struct):
        self.flatten_struct = flatten_struct

    def register_pattern(self, pattern):
        if not self._is_magic(pattern):
            return
        assert self.flatten_struct is not None
        if pattern in self.registered_patterns:
            return
        res_dic = self.registered_patterns.setdefault(pattern, {})
        pattern = os.path.normcase(pattern)
        pattern_seg = pattern.split(os.sep)
        pattern_seg = [(re.compile(translate(_)), _) if self._is_magic(_) else _ for _ in pattern_seg]
        for field_key, field_info in self.flatten_struct.items():
            field_lst = res_dic.setdefault(field_key, [])
            for field_path in field_info:
                match_res = self._match(field_path, pattern_seg)
                field_lst.append(match_res) if match_res else None

    def get_parsed_pattern(self, pattern, field_keys=None):
        patterns_res = self.registered_patterns[pattern]
        if field_keys is None:
            return patterns_res

        res = dict()
        for field_key in field_keys:
            field_info = patterns_res.get(field_key, None)
            if field_info is not None:
                res[field_key] = field_info
        return res

    def has_registered(self, pattern):
        return pattern in self.registered_patterns

    @staticmethod
    def _match(path, pattern_seg):
        path = os.path.normcase(path)
        path_seg = path.split(os.sep)
        magic_num = 0
        if len(path_seg) != len(pattern_seg):
            return False
        for i, (pattern_, path_) in enumerate(zip(pattern_seg, path_seg)):
            if path_ != "*":  # not list
                if isinstance(pattern_, tuple):
                    p_compile, p_str = pattern_
                    if p_compile.match(path_) is None:
                        return False
                else:
                    if pattern_ != path_:
                        return False
            else:  # list
                if isinstance(pattern_, tuple):
                    path_seg[i] = "%d"
                    magic_num += 1
                else:
                    if pattern_.isdigit():
                        path_seg[i] = pattern_
                    else:
                        return False

        return "/".join(path_seg), magic_num

    @staticmethod
    def _is_magic(p):
        return "[" in p or "]" in p or "*" in p or "?" in p


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
    _FLATTEN_STRUCT = None
    _REGISTER_PATTERN = RegisterPattern()

    def __init__(self, file_reader=None, prefix=None, flatten_dic=None, **kwargs):

        super().__init__()
        assert flatten_dic is None or isinstance(flatten_dic, dict)
        self.attributes = Attributes()
        self.file_reader = file_reader
        self._keys = []
        self._dict_format = None
        self._flatten_format = dict() if flatten_dic is None else flatten_dic
        self._raw_dict = kwargs
        self._prefix = prefix or "."

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
            if hasattr(field_obj, "set_flatten_dic"):
                field_obj.set_flatten_dic(self._flatten_format)
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

        elif key in self.__struct_mappings__:  # struct
            cls = self.__struct_mappings__[key].__class__
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Struct validation error: {cls.__name__} requires a dict to initiate, but got '{value}'.")
            struct_obj = cls(
                file_reader=self.file_reader,
                prefix=f"{self._prefix}/{key}",
                flatten_dic=self._flatten_format, **value)
            self[key] = struct_obj
        else:
            self[key] = value

    @classmethod
    def get_mapping(cls):
        return cls.__mappings__

    @classmethod
    def get_struct_mapping(cls):
        return cls.__struct_mappings__

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

    def extract_path_info(self, pattern, field_keys=None, verbose=False):
        def _is_magic(p):
            return "[" in p or "]" in p or "*" in p or "?" in p

        if field_keys is None:
            flatten_sample = self.flatten_sample()
        else:
            if not isinstance(field_keys, list):
                field_keys = [field_keys]
            field_keys = [f"${_.lower()}" for _ in field_keys if isinstance(_, str)]
            all_flatten_sample = self.flatten_sample()
            flatten_sample = dict()
            for field_key in field_keys:
                field_info = all_flatten_sample.get(field_key, None)
                if field_info is not None:
                    flatten_sample[field_key] = field_info
        if not _is_magic(pattern):  # 无通配
            for field_info in flatten_sample.values():
                res = field_info.get(pattern, None)
                if res is not None:
                    return {pattern: res} if verbose else res
            return dict() if verbose else None

        self.register_path_for_extract(pattern)

        all_parsed_pattern = self._REGISTER_PATTERN.get_parsed_pattern(pattern, field_keys)
        res = dict()
        for field_key in field_keys or all_parsed_pattern.keys():
            pattern_field_info = all_parsed_pattern.get(field_key, None)
            field_info = flatten_sample.get(field_key, None)
            if field_info is None or field_info is None:
                continue
            for this_pattern in pattern_field_info:
                self._match(this_pattern, field_info, res)
        if not verbose:
            res = list(res.values())
            if len(res) == 0:
                res = None
            elif len(res) == 1:
                res = res[0]
        return res

    @staticmethod
    def _match(pattern, all_sample, result_dic):
        pattern, digit_num = pattern
        if digit_num == 0:
            result_dic[pattern] = all_sample[pattern]
            return

        def _helper(prefix, idx_num):
            if idx_num == 0:
                this_pattern = pattern % tuple(prefix)
                item = all_sample.get(this_pattern, None)
                if item is not None:
                    result_dic[this_pattern] = item
                    return True
                else:
                    return False
            start_idx = 0
            while 1:
                res = _helper(prefix + [start_idx], idx_num - 1)
                if res:
                    start_idx += 1
                else:
                    break
            return start_idx > 0

        _helper([], digit_num)

    def extract_field_info(self, field_lst, nest_flag=True, verbose=False):
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
        ori_field_lst = field_lst
        field_lst = [_.lower() for _ in ori_field_lst]
        for ori_field, field in zip(ori_field_lst, field_lst):
            if nest_flag:
                if verbose:
                    result_dic[ori_field] = flatten_sample.get(f"${field}", {})
                else:
                    field_info = list(flatten_sample.get(f"${field}", {}).values())
                    if len(field_info) == 0:
                        field_info = None
                    elif len(field_info) == 1:
                        field_info = field_info[0]
                    result_dic[ori_field] = field_info
            else:
                result_dic.update(flatten_sample.get(f"${field}", {}))
        if not nest_flag and not verbose:
            result_dic = list(result_dic.values())
            if len(result_dic) == 0:
                result_dic = None
            elif len(result_dic) == 1:
                result_dic = result_dic[0]
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
    def _flatten_struct(cls):
        prefix = "."
        res_dic = dict()
        field_mappings = cls.get_mapping()
        struct_mappings = cls.get_struct_mapping()

        def _helper(item, pre_path, key_name, flatten_dic):
            if isinstance(item, Field):
                field_key = item.extract_key()
                if field_key != "$list":
                    path = f"{pre_path}/{key_name}"
                    field_dic = flatten_dic.setdefault(field_key, [])
                    field_dic.append(path)
                else:
                    path = f"{pre_path}/{key_name}"
                    _helper(item.ele_type, path, "*", flatten_dic)
            elif isinstance(item, Struct):
                path = f"{pre_path}/{key_name}"
                this_mapping = item.get_mapping()
                this_struct_mapping = item.get_struct_mapping()
                for this_key, this_item in this_mapping.items():
                    _helper(this_item, path, this_key, flatten_dic)
                for this_key, this_item in this_struct_mapping.items():
                    _helper(this_item, path, this_key, flatten_dic)

        for field_name, field_obj in field_mappings.items():
            _helper(field_obj, prefix, field_name, res_dic)
        for struct_name, struct_obj in struct_mappings.items():
            _helper(struct_obj, prefix, struct_name, res_dic)

        return res_dic

    @classmethod
    def register_path_for_extract(cls, pattern):
        if getattr(cls, "_FLATTEN_STRUCT", None) is None:
            cls._FLATTEN_STRUCT = cls._flatten_struct()
            cls._REGISTER_PATTERN.set_flatten_struct(cls._FLATTEN_STRUCT)
        if not cls._REGISTER_PATTERN.has_registered(pattern):
            cls._REGISTER_PATTERN.register_pattern(pattern)

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
