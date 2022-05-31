from .field import Field
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
