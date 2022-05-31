from .field import Field
from ..exception import ValidationError


class CoordField(Field):
    def validate(self, value):
        if type(value) is not list:
            raise ValidationError(f"expect list of num, got {value}")
        if len(value) != 2:
            raise ValidationError(f"expect size of list is 2, got {len(value)}")
        try:
            value[0] = float(value[0])
            value[1] = float(value[1])
            return value
        except (TypeError, ValueError) as _:
            raise ValidationError(f"expect type of list item is float, got {value}")


class LabelField(Field):
    def __init__(self, dom):
        super(LabelField, self).__init__()
