from .field import Field
from ..exception import ValidationError


def validate_list_of_number(value, size_limit, item_type):
    if type(value) is not list:
        raise ValidationError(f"expect list of num, got {value}")
    if len(value) != size_limit:
        raise ValidationError(f"expect size of list is {size_limit}, got {len(value)}")
    try:
        return [item_type(item) for item in value]
    except (TypeError, ValueError) as _:
        raise ValidationError(f"expect type of list item is float, got {value}")


class CoordField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 2, float)


class Coord3DField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 3, float)


class IntervalField(Field):
    def validate(self, value):
        value = validate_list_of_number(value, 2, float)
        if value[0] > value[1]:
            raise ValidationError(
                f"expect |begin| less than or equal to |end|, got {value}"
            )
        return value


class BBoxField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 4, float)


class LabelField(Field):
    def __init__(self, dom):
        super(LabelField, self).__init__()
        self.dom = dom
