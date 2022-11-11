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
        super().__init__(*args, **kwargs)

    def validate(self, value):
        if hasattr(self.ele_type, "set_file_reader"):
            self.ele_type.set_file_reader(self.file_reader)
        if isinstance(self.ele_type, Field):
            value = [self.ele_type.validate(item) for item in value]
        elif isinstance(self.ele_type, Struct):
            value = [self.ele_type.__class__(file_reader=self.file_reader, **item) for item in value]
        return value

    def set_file_reader(self, file_reader):
        self.file_reader = file_reader


class DictField(Field):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError(f"DictField Error: expect dict value, got {value.__class__}")
        return value
