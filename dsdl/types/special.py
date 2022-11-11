from .field import Field
from ..geometry import BBox, Polygon, PolygonItem, Coord2D, KeyPoints
from ..exception import ValidationError
from datetime import date, time, datetime


def validate_list_of_number(value, size_limit, item_type, field_name):
    if type(value) is not list:
        raise ValidationError(f"{field_name} Error: expect list of num, got {value}")
    if len(value) != size_limit:
        raise ValidationError(f"{field_name} Error: expect size of list is {size_limit}, got {len(value)}")
    try:
        return [item_type(item) for item in value]
    except (TypeError, ValueError) as _:
        raise ValidationError(f"{field_name} Error: expect type of list item is float, got {value}")


class CoordField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 2, float, "CoordField")


class Coord3DField(Field):
    def validate(self, value):
        return validate_list_of_number(value, 3, float, "Coord3DField")


class IntervalField(Field):
    def validate(self, value):
        value = validate_list_of_number(value, 2, float, "IntervalField")
        if value[0] > value[1]:
            raise ValidationError(
                f"IntervalField Error: expect |begin| less than or equal to |end|, got {value}"
            )
        return value


class BBoxField(Field):
    def validate(self, value):
        x, y, w, h = validate_list_of_number(value, 4, float, "BBoxField")
        return BBox(x, y, w, h)


class PolygonField(Field):
    def validate(self, value):
        polygon_lst = []
        for idx, points in enumerate(value):
            for point in points:
                validate_list_of_number(point, 2, float, "PolygonField")
            polygon_lst.append(PolygonItem(points))
        return Polygon(polygon_lst)


class KeypointField(Field):

    def __init__(self, dom, *args, **kwargs):
        super(KeypointField, self).__init__(*args, **kwargs)
        self.dom = dom

    def validate(self, value):
        value = validate_list_of_number(value, len(self.dom), list, "KeypointField")
        keypoints = []
        for class_ind, p in enumerate(value, start=1):
            p = validate_list_of_number(p, 3, float, "KeypointField")
            label = self.dom.get_label(class_ind)
            coord2d = Coord2D(x=p[0], y=p[1], visiable=int(p[2]), label=label)
            keypoints.append(coord2d)

        return KeyPoints(keypoints=keypoints, domain=self.dom)


class LabelField(Field):
    def __init__(self, dom, *args, **kwargs):
        super(LabelField, self).__init__(*args, **kwargs)
        self.dom = dom

    def validate(self, value):
        try:
            if isinstance(value, (int, str)):
                return self.dom.get_label(value)
            else:
                raise TypeError(f"LabelField Error: invalid class label type. Expected 'int' or 'str' value, got '{value.__class__.__name__}'.")
        except:
            raise RuntimeError(f"LabelField Error: The label '{value}' is not valid.")


class DateField(Field):
    def __init__(self, fmt: str = "", *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value):
        try:
            if self.fmt == "":
                return date.fromisoformat(value)
            return datetime.strptime(value, self.fmt).date()
        except Exception as e:
            raise RuntimeError(f"DateField Error: {e}")


class TimeField(Field):
    def __init__(self, fmt: str = "", *args, **kwargs):
        super(TimeField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value):
        try:
            if self.fmt == "":
                return time.fromisoformat(value)
            return datetime.strptime(value, self.fmt).time()
        except Exception as e:
            raise RuntimeError(f"TimeField Error: {e}")

