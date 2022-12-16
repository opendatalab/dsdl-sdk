from .field import Field
from ..geometry import BBox, Polygon, PolygonItem, Coord2D, KeyPoints, Text, RBBox, ImageShape, InstanceID
from ..exception import ValidationError
from datetime import date, time, datetime
import math


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


class RotatedBBoxField(Field):
    def __init__(self, mode="xywht", measure="radian", *args, **kwargs):
        super(RotatedBBoxField, self).__init__(*args, **kwargs)
        try:
            assert mode in ("xywht", "xyxy")
            self.mode = mode
        except AssertionError as e:
            raise ValidationError("RotateBBox Error: invalid mode, only mode='xywht' or 'xyxy' are permitted.")
        try:
            assert measure in ("radian", "degree")
            self.measure = measure
        except AssertionError as e:
            raise ValidationError("RotateBBox Error: invalid measure, only measure='radian' or 'degree' are permitted.")

    def validate(self, value):
        if self.mode == "xywht":
            value = validate_list_of_number(value, 5, float, "RotateBBoxField")
            if self.measure == "degree":
                value[-1] = value[-1] / 180 * math.pi  # convert to radian
        else:
            value = validate_list_of_number(value, 8, float, "RotateBBoxField")
            value = [value[i:i+2] for i in (0, 2, 4, 6)]
        return RBBox(value, self.mode)


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
        if not isinstance(dom, list):
            self.dom_lst = [dom]
        self.dom_dic = {_.__name__: _ for _ in self.dom_lst}
        self.dom = dom

    def validate(self, value):

        if not isinstance(value, (int, str)):
            raise TypeError(
                f"LabelField Error: invalid class label type. Expected 'int' or 'str' value, got '{value.__class__.__name__}'.")

        if (isinstance(value, int) or (isinstance(value, str) and "::" not in value)):
            if len(self.dom_lst) > 1:
                raise RuntimeError(
                    "LabelField Error: there are more than 1 domains in the struct, you need to specify the label's class domain explicitly.")
            else:
                try:
                    return self.dom.get_label(value)
                except Exception as e:
                    raise RuntimeError(f"LabelField Error: The label '{value}' is not valid. {e}")

        if isinstance(value, str) and "::" in value:
            domain_name, label_name = value.split("::")[:2]

            if domain_name not in self.dom_dic:
                raise RuntimeError(
                    f"LabelField Error: the class domain '{domain_name}' is not provided for the struct."
                )
            else:
                try:
                    return self.dom_dic[domain_name].get_label(label_name)
                except Exception as e:
                    raise RuntimeError(f"LabelField Error: The label '{value}' is not valid. {e}")


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


class TextField(Field):
    def validate(self, value):
        try:
            return Text("" + value)
        except TypeError as _:
            raise ValidationError(f"TextField Error: expect str value, got {value}")


class ImageShapeField(Field):
    def __init__(self, mode="hw", *args, **kwargs):
        super(ImageShapeField, self).__init__(*args, **kwargs)
        mode = mode.lower()
        assert mode in ("hw", "wh"), f"the mode of 'ImageShapeField' must be in {('hw', 'wh')}"
        self.mode = mode

    def validate(self, value):
        value = validate_list_of_number(value, 2, int, "ImageShapeField")
        return ImageShape(value=value, mode=self.mode)


class InstanceIDField(Field):
    def validate(self, value):
        try:
            return InstanceID("" + value)
        except TypeError as _:
            raise ValidationError(f"InstanceIDField Error: expect str value, got {value}")
