from dsdl.geometry import PlaceHolder, STRUCT
from copy import deepcopy
from fnmatch import translate
from .base_field import BaseField
import os
import re
from dsdl.exception import ValidationError, InterruptError, FieldNotFoundError
from dsdl.warning import FieldNotFoundWarning


def _is_magic(p):
    return "[" in p or "]" in p or "*" in p or "?" in p


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
        if not _is_magic(pattern):
            return
        assert self.flatten_struct is not None
        if pattern in self.registered_patterns:
            return
        res_dic = self.registered_patterns.setdefault(pattern, {})
        pattern = os.path.normcase(pattern)
        pattern_seg = pattern.split(os.sep)
        pattern_seg = [(re.compile(translate(_)), _) if _is_magic(_) else _ for _ in pattern_seg]
        for field_key, field_info in self.flatten_struct.items():
            if field_key == "$field_mapping":
                continue
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


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):

        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)
        _fields = attributes.pop("__fields__", {})
        _optional_fields_name = attributes.pop("__optional__", [])
        param_names = attributes.pop("__params__", [])
        all_fields = dict()
        optional = []
        for k, v in _fields.items():
            if isinstance(v, (BaseField, Struct)):
                all_fields[k] = v
                if k in _optional_fields_name:
                    optional.append(k)

        attributes["__fields__"] = all_fields
        attributes["__optional__"] = optional
        attributes["__params__"] = param_names

        new_class = super_new(mcs, name, bases, attributes)
        STRUCT.register(name, new_class)
        return new_class


class Struct(object, metaclass=StructMetaclass):

    def __init__(self, **kwargs):
        super().__init__()
        self._rewrite_class_attr()
        self._FLATTEN_STRUCT = None
        self._REGISTER_PATTERN = RegisterPattern()
        self.file_reader = None
        self.namespace = None
        self.lazy_init = False
        self.strict_init = False
        self.params = dict()
        for k, v in kwargs.items():
            assert k in self.__class__.__params__, f"Invalid arguments '{k}'"
            self.params[k] = PlaceHolder(v)
        self._register_namespace()
        self.init_pattern_register()

    def get_struct_mapping(self):
        return self.__struct_mappings__

    def get_mapping(self):
        return self.__mappings__

    def _rewrite_class_attr(self):
        _fields = self.__class__.__fields__
        _optional_fields_name = getattr(self, "__optional__", [])

        required = dict()  # 所有必须填写的field对象
        optional = dict()  # 所有可不填写的field对象
        mappings = dict()  # 所有的field对象
        struct_mappings = dict()  # 所有的Struct对象

        for k, v in _fields.items():
            v = deepcopy(v)
            if isinstance(v, BaseField):
                mappings[k] = v
                if k in _optional_fields_name:
                    optional[k] = v
                else:
                    required[k] = v
            elif isinstance(v, Struct):
                struct_mappings[k] = v

        self.__required__ = required
        self.__optional__ = optional
        self.__mappings__ = mappings
        self.__struct_mappings__ = struct_mappings

    def _register_namespace(self):
        for sub_struct in self.__struct_mappings__.values():
            sub_struct.set_namespace(self)
        for field in self.__mappings__.values():
            if hasattr(field, "set_namespace"):
                field.set_namespace(self)

    def set_lazy_init(self, flag):
        self.lazy_init = flag
        if self.lazy_init and self.strict_init:
            raise InterruptError("You can't set lazy_init mode and strict_init mode on at the same time.")
        self._register_namespace()

    def set_strict_init(self, flag):
        self.strict_init = flag
        if self.lazy_init and self.strict_init:
            raise InterruptError("You can't set lazy_init mode and strict_init mode on at the same time.")
        self._register_namespace()

    def set_file_reader(self, file_reader):
        self.file_reader = file_reader
        self._register_namespace()

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        self.lazy_init = self.namespace.lazy_init
        self.strict_init = self.namespace.strict_init
        for d in self.params.values():
            d.set_namespace(struct_obj)
        self.file_reader = struct_obj.file_reader
        self._register_namespace()

    def validate(self, value):
        return self(value)

    def _flatten_struct(self):
        prefix = "."
        res_dic = dict()
        res_dic["$field_mapping"] = dict()
        field_mappings = self.get_mapping()
        struct_mappings = self.get_struct_mapping()

        def _helper(item, pre_path, key_name, flatten_dic):
            if isinstance(item, BaseField):
                field_key = item.extract_key()
                if field_key != "$list":
                    path = f"{pre_path}/{key_name}"
                    field_dic = flatten_dic.setdefault(field_key, [])
                    field_dic.append(path)
                    flatten_dic["$field_mapping"][path] = item
                else:
                    path = f"{pre_path}/{key_name}"
                    _helper(item.etype, path, "*", flatten_dic)
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

    def register_path_for_extract(self, pattern):
        self.init_pattern_register()
        if not self._REGISTER_PATTERN.has_registered(pattern):
            self._REGISTER_PATTERN.register_pattern(pattern)

    def init_pattern_register(self):
        if self._FLATTEN_STRUCT is None:
            self._FLATTEN_STRUCT = self._flatten_struct()
            self._REGISTER_PATTERN.set_flatten_struct(self._FLATTEN_STRUCT)

    def __call__(self, value):
        return StructObject(self, **value)


class StructObject(dict):

    def __init__(self, struct_obj, **kwargs):
        super().__init__()
        self['namespace'] = struct_obj
        self["lazy_init"] = struct_obj.lazy_init
        self["strict_init"] = struct_obj.strict_init
        self['_raw_dict'] = kwargs

        if not self.lazy_init:
            if self.strict_init:
                self.strict_setup()
            else:
                self.setup()

    def setup(self):
        kwargs = self._raw_dict
        for k in self.namespace.__required__:
            if k not in kwargs:
                FieldNotFoundWarning(f"Required field {k} is missing.")
                continue
            setattr(self, k, kwargs[k])
        for k in self.namespace.__optional__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
        for k in self.namespace.get_struct_mapping():
            if k not in kwargs:
                FieldNotFoundWarning(f"Required struct instance {k} is missing.")
                continue
            setattr(self, k, kwargs[k])

    def strict_setup(self):
        kwargs = self._raw_dict
        extra_keys = list(kwargs.keys())
        missing_fields = list()
        missing_structs = list()
        for k in self.namespace.__required__:
            if k not in kwargs:
                missing_fields.append(k)
            else:
                setattr(self, k, kwargs[k])
                extra_keys.remove(k)
        for k in self.namespace.__optional__:
            if k in kwargs:
                setattr(self, k, kwargs[k])
                extra_keys.remove(k)
        for k in self.namespace.get_struct_mapping():
            if k not in kwargs:
                missing_structs.append(k)
            else:
                setattr(self, k, kwargs[k])
                extra_keys.remove(k)

        if extra_keys or missing_structs or missing_fields:
            msg = f"Interrupt happens when initial the struct, "
            if extra_keys:
                msg += f"the keys {extra_keys} in the sample are redundant, please remove them. "
            if missing_structs:
                msg += f"the required structs {missing_structs} should be defined in the sample. "
            if missing_fields:
                msg += f"the required fields {missing_fields} should be defined in the sample. "
            raise InterruptError(msg)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            if not self["lazy_init"]:
                raise AttributeError(r"'Model' object has no attribute '%s'" % key)
            else:
                try:
                    value = self["_raw_dict"][key]
                except KeyError:
                    raise AttributeError(f"Key '{key}' doesn't exist in the current sample.")
                field = self.namespace.get_mapping().get(key, None)
                if field is not None:
                    return field.validate(value)
                struct = self.namespace.get_struct_mapping().get(key, None)
                if struct is not None:
                    return struct(**value)
                return value

    def __setattr__(self, key, value):
        all_mappings = self.namespace.get_mapping()
        all_struct_mappings = self.namespace.get_struct_mapping()
        if key in all_mappings:  # field
            field_obj = all_mappings[key]
            try:
                geometry_obj = field_obj.validate(value)
            except ValidationError as error:
                raise ValidationError(f"Field '{key}' validation error: {error}.")
            self[key] = geometry_obj

        elif key in all_struct_mappings:  # struct
            struct_cls = all_struct_mappings[key]
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Struct validation error: {struct_cls.__class__.__name__} requires a dict to initiate, "
                    f"but got '{value}'.")
            struct_obj = struct_cls(value)
            self[key] = struct_obj
        else:
            self[key] = value

    def extract_path_info(self, pattern, field_keys=None, verbose=False):
        if field_keys is not None:
            if not isinstance(field_keys, list):
                field_keys = [field_keys]
            field_keys = [f"${_.lower()}" for _ in field_keys if isinstance(_, str)]

        if not _is_magic(pattern):  # 无通配
            res = self.extract_path_value(pattern, field_keys)
            if res is not None:
                return res if verbose else list(res.values())
            return dict() if verbose else []

        self.namespace.register_path_for_extract(pattern)
        all_parsed_pattern = self.namespace._REGISTER_PATTERN.get_parsed_pattern(pattern, field_keys)
        res = dict()
        for field_key in field_keys or all_parsed_pattern.keys():
            pattern_field_info = all_parsed_pattern.get(field_key, None)
            if pattern_field_info is None:
                continue
            for this_pattern in pattern_field_info:
                this_res = self.extract_path_value(this_pattern[0].replace("%d", "*"), [field_key])
                if this_res is not None:
                    res.update(this_res)
        if not verbose:
            res = list(res.values())
        return res

    def extract_field_info(self, field_lst, nest_flag=True, verbose=False):
        ori_field_lst = field_lst
        # {field_type: [pattern1, pattern2, ...]}
        field_paths = {_: self.namespace._FLATTEN_STRUCT.get(f"${_.lower()}", []) for i, _ in enumerate(ori_field_lst)}
        res = dict()
        for field, pattern_lst in field_paths.items():
            if verbose:
                this_res = res.setdefault(field, dict())
            else:
                this_res = res.setdefault(field, list())
            for pattern in pattern_lst:
                extract_res = self.extract_path_value(pattern, field_keys=[f"${field.lower()}"])
                if extract_res is not None:
                    if verbose:
                        this_res.update(extract_res)
                    else:
                        this_res.extend(extract_res.values())
        return res

    def extract_path_value(self, path, field_keys=None):

        def _extract_value_from_pattern(p_segs, value_dic, ret_dic, prefix="."):
            if len(p_segs) == 0:
                ret_dic[prefix] = field_obj.validate(value_dic)
                return
            p = p_segs[0]
            if p.isdigit():
                p = int(p)
            if p != "*":
                _extract_value_from_pattern(p_segs[1:], value_dic[p], ret_dic, f"{prefix}/{p}")
            else:
                for i, v in enumerate(value_dic):  # list
                    _extract_value_from_pattern(p_segs[1:], v, ret_dic, f"{prefix}/{i}")

        path_segs = path.split("/")
        field_path = "/".join([_ if not _.isdigit() else "*" for _ in path_segs])
        try:
            field_obj = self.namespace._FLATTEN_STRUCT["$field_mapping"][field_path]
            if field_keys is not None and field_obj.extract_key() not in field_keys:
                return None
        except KeyError as e:
            FieldNotFoundWarning(f"No field of path '{field_path}' exists in this struct.")
            return None
        value = self._raw_dict
        res = dict()
        try:
            _extract_value_from_pattern(path_segs[1:], value, res)
        except KeyError as e:
            return None
        except IndexError as e:
            return None
        except ValidationError as e:
            raise e  # not valid
        return res
