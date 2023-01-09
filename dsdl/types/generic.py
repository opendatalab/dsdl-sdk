from .field import Field
from .struct import Struct
from ..exception import ValidationError


class BoolField(Field):
    def validate(self, value):
        if value not in [True, False]:
            raise ValidationError(f"BoolField Error: expect True/False, got {value}")
        return value


class IntField(Field):
    def validate(self, value):
        try:
            return int(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"IntField Error: expect int, got {value}")


class NumField(Field):
    def validate(self, value):
        try:
            return float(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"NumField Error: expect num, got {value}")


class StrField(Field):
    def validate(self, value):
        try:
            return "" + value
        except TypeError as _:
            raise ValidationError(f"StrField Error: expect str value, got {value}")


class ListField(Field):
    def __init__(self, ele_type, ordered=False, *args, **kwargs):
        self.ordered = ordered
        self.ele_type = ele_type
        self.file_reader = None
        self.prefix = None
        self.flatten_dic = None
        super().__init__(*args, **kwargs)

    def validate(self, value):
        if hasattr(self.ele_type, "set_file_reader"):
            self.ele_type.set_file_reader(self.file_reader)
        if isinstance(self.ele_type, Field):
            if self.prefix is not None and self.flatten_dic is not None:
                field_key = self.ele_type.extract_key()
                field_dic = self.flatten_dic.setdefault(field_key, {})
                res = [self.ele_type.validate(_) for _ in value]
                paths = [f"{self.prefix}/{ind}" for ind in range(len(res))]
                _ = [field_dic.update({k: v}) for k, v in zip(paths, res)]
            else:
                res = [self.ele_type.validate(_) for _ in value]

        elif isinstance(self.ele_type, Struct):
            res = [
                self.ele_type.__class__(
                    file_reader=self.file_reader,
                    prefix=f"{self.prefix}/{i}",
                    flatten_dic=self.flatten_dic, **item)
                for i, item in enumerate(value)
            ]
        else:
            raise ValidationError(
                f"Wrong ele_type in ListField, only 'Struct' or 'Field' are permitted, but got '{type(self.ele_type)}'")
        return res

    def set_file_reader(self, file_reader):
        self.file_reader = file_reader

    def set_prefix(self, prefix):
        self.prefix = prefix

    def set_flatten_dic(self, dic):
        self.flatten_dic = dic


class DictField(Field):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError(f"DictField Error: expect dict value, got {value.__class__}")
        return value
