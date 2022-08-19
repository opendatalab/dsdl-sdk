from .field import Field
from ..geometry import BBox, Polygon, PolygonItem
from ..exception import ValidationError
from datetime import date, time, datetime


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
        return BBox(*validate_list_of_number(value, 4, float))


class PolygonField(Field):
    def validate(self, value):
        polygon_lst = []
        for idx, points in enumerate(value):
            for point in points:
                validate_list_of_number(point, 2, float)
            polygon_lst.append(PolygonItem(points))
        return Polygon(polygon_lst)


class LabelField(Field):
    def __init__(self, dom, *args, **kwargs):
        super(LabelField, self).__init__(*args, **kwargs)
        self.dom = dom

    def validate(self, value):
        try:
            if isinstance(value, (int, str)):
                return self.dom.get_label(value)
            else:
                raise TypeError("invalid class label type.")
        except:
            raise RuntimeError(f"The label {value} is not valid.")


class DateField(Field):
    def __init__(self, fmt: str = "", *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value):
        if self.fmt == "":
            return date.fromisoformat(value)
        return datetime.strptime(value, self.fmt).date()


class TimeField(Field):
    def __init__(self, fmt: str = "", *args, **kwargs):
        super(TimeField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value):
        if self.fmt == "":
            return time.fromisoformat(value)
        return datetime.strptime(value, self.fmt).time()

