from .field import Field
from .struct import Struct
from ..exception import ValidationError


class BoolField(Field):
    def validate(self, value):
        if value not in [True, False]:
            raise ValidationError(f"expect True/False, got {value}")
        return value


class IntField(Field):
    def validate(self, value):
        try:
            return int(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"expect int, got {value}")


class NumField(Field):
    def validate(self, value):
        try:
            return float(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"expect num, got {value}")


class StrField(Field):
    def validate(self, value):
        try:
            return "" + value
        except TypeError as _:
            raise ValidationError(f"expect str, got {value}")


class ListField(Field):
    def __init__(self, ele_type, ordered=False):
        self.ordered = ordered
        self.ele_type = ele_type
        self._dataset = None
        super().__init__()

    def validate(self, value):
        if isinstance(self.ele_type, ListField):
            self.ele_type.set_dataset(self._dataset)
        if isinstance(self.ele_type, Field):
            value = [self.ele_type.validate(item) for item in value]
        elif isinstance(self.ele_type, Struct):
            value = [self.ele_type.__class__(dataset=self._dataset, **item) for item in value]
        return value

    def set_dataset(self, dataset):
        self._dataset = dataset
