"""
DSDL Annotation Fields, Including:
1. CoordField
2. Coord3DField
3. IntervalField
4. BBoxField
5. RotatedBBoxField
6. PolygonField
7. KeypointField
8. LabelField
9. DateField
10. TimeField
11. TextField
12. ImageShapeField
13. InstanceIDField
14. UniqueIDField
"""
from .field import Field
from ..geometry import BBox, Polygon, PolygonItem, Coord2D, KeyPoints, Text, RBBox, ImageShape, UniqueID, ClassDomain, \
    Label
from ..exception import ValidationError
from datetime import date, time, datetime
import math
from typing import Iterable, Optional, Dict


def _validate_list_of_number(value, size_limit, item_type, field_name):
    if type(value) is not list:
        raise ValidationError(f"{field_name} Error: expect list of num, got {value}")
    if len(value) != size_limit:
        raise ValidationError(f"{field_name} Error: expect size of list is {size_limit}, got {len(value)}")
    try:
        return [item_type(item) for item in value]
    except (TypeError, ValueError) as _:
        raise ValidationError(f"{field_name} Error: expect type of list item is float, got {value}")


class CoordField(Field):
    """A DSDL Field to validate and return a 2D coordinate object.

    Examples:
        >>> coord_field = CoordField()
        >>> value = [10, 10]
        >>> coord_field.validate(value)
        [10.0, 10.0]
    """

    def validate(self, value: Iterable[float, float]) -> List[float, float]:
        """Validate whether the given value is valid to represent a 2D coordinate object.

        Args:
            value: A given value to represent a 2D coordinate object.

        Returns:
            The value which is valid to represent a 2D coordinate object.
        """
        return _validate_list_of_number(value, 2, float, "CoordField")


class Coord3DField(Field):
    """
    A DSDL Field to validate and return a 3D coordinate object.

    Examples:
        >>> coord3d_field = Coord3DField()
        >>> value = [10, 10, 10]
        >>> coord3d_field.validate(value)
        [10.0, 10.0, 10.0]
    """

    def validate(self, value: Iterable[float, float, float]) -> List[float, float, float]:
        """Validate whether the given value is valid to represent a 3D coordinate object.

        Args:
            value: A given value to represent a 3D coordinate object.

        Returns:
            The value which is valid to represent a 3D coordinate object.
        """
        return _validate_list_of_number(value, 3, float, "Coord3DField")


class IntervalField(Field):
    """
    A DSDL Field to validate and return an interval object.

    Examples:
        >>> interval_field = IntervalField()
        >>> value = [0, 10]
        >>> interval_field.validate(value)
        [0.0, 10.0]
    """

    def validate(self, value: Iterable[float, float]) -> List[float, float]:
        """Validate whether the given value is valid to represent an interval object.

        Args:
            value: A given value to represent an interval object.

        Returns:
            The value which is valid to represent an interval object.
        """
        value = _validate_list_of_number(value, 2, float, "IntervalField")
        if value[0] > value[1]:
            raise ValidationError(
                f"IntervalField Error: expect |begin| less than or equal to |end|, got {value}"
            )
        return value


class BBoxField(Field):
    """
    A DSDL Field to validate the given value and return a BBox object.

    Examples:
        >>> bbox_field = BBoxField()
        >>> value = [0, 10, 100, 100]  # [x, y, w, h]
        >>> bbox_obj = bbox_field.validate(value)
        >>> bbox_obj.__class__.__name__
        "BBox"
    """

    def validate(self, value: Iterable[float * 4]) -> BBox:
        """Validate whether the given value is valid to represent a bounding box object.

        Args:
            value: A given value to represent a bounding box.

        Returns:
            A `BBox` object.
        """
        x, y, w, h = _validate_list_of_number(value, 4, float, "BBoxField")
        return BBox(x, y, w, h)


class RotatedBBoxField(Field):
    def __init__(self, mode: str = "xywht", measure: str = "radian", *args, **kwargs):
        """A DSDL Field to validate the given value and return a RBBox object.

        Examples:
            >>> rotatedbbox_field = RotatedBBoxField(measure="degree")
            >>> value = [1, 10, 100, 100, 180]
            >>> rotatedbbox_obj = rotatedbbox_field.validate(value)
            >>> rotatedbbox_obj.__class__.__name__
            "RBBox"

        Args:
            mode: The format in which the value to be validated is given. Only `"xywht"` and `"xyxy"` are permitted,
                  which respectly means the value is given by [x, y, w, h, theta] and [x1, y1, x2, y2, x3, y3, x4, y4].
            measure: The uint in which the angle value is given. Only `"radian"` and `"degree"` are permitted.
                     This parameter takes effect only when `mode=="xywht"`.

        Attributes:
            mode: The format in which the value to be validated is given. Only `"xywht"` and `"xyxy"` are permitted,
                  which respectly means the value is given by [x, y, w, h, theta] and [x1, y1, x2, y2, x3, y3, x4, y4].
            measure: The uint in which the angle value is given. Only `"radian"` and `"degree"` are permitted.
                     This parameter takes effect only when `mode=="xywht"`.
        """
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

    def validate(self, value: Optional[Iterable[float * 5], Iterable[float * 8]]) -> RBBox:
        """Validate whether the given value is valid to represent a rotated bounding box object.

        Args:
            value: A given value to represent a rotated bounding box.

        Returns:
            A `RBBox` object.
        """
        if self.mode == "xywht":
            value = _validate_list_of_number(value, 5, float, "RotateBBoxField")
            if self.measure == "degree":
                value[-1] = value[-1] / 180 * math.pi  # convert to radian
        else:
            value = _validate_list_of_number(value, 8, float, "RotateBBoxField")
            value = [value[i:i + 2] for i in (0, 2, 4, 6)]
        return RBBox(value, self.mode)


class PolygonField(Field):
    """
    A DSDL Field to validate the given value and return a polygon object.

    Examples:
        >>> polygon_field = PolygonField()
        >>> value = [[[0, 0], [0, 100], [100, 100], [100, 0]], [[0, 0], [0, 50], [50, 50], [50, 0]]]
        >>> polygon_obj = polygon_field.validate(value)
        >>> polygon_obj.__class__.__name__
        "Polygon"
    """

    def validate(self, value: Iterable[float]) -> Polygon:
        """Validate whether the given value is valid to represent a polygon object.

        Args:
            value: A given value to represent a polygon object.

        Returns:
            A `Polygon` object.
        """
        polygon_lst = []
        for idx, points in enumerate(value):
            for point in points:
                _validate_list_of_number(point, 2, float, "PolygonField")
            polygon_lst.append(PolygonItem(points))
        return Polygon(polygon_lst)


class KeypointField(Field):
    def __init__(self, dom: ClassDomain, *args, **kwargs):
        """A DSDL Field to validate the given value and return a Keypoints object.

        Args:
            dom: The class domain which the current keypoints object belongs to.

        Attributes:
            dom(ClassDomain): The class domain which the current keypoints object belongs to.
        """
        super(KeypointField, self).__init__(*args, **kwargs)
        self.dom = dom

    def validate(self, value: Iterable[Iterable[float]]) -> KeyPoints:
        """Validate whether the given value is valid to represent a keypoints object.

        Args:
            value: A given value to represent a keypoints object.

        Returns:
            A `KeyPoints` object.
        """
        value = _validate_list_of_number(value, len(self.dom), list, "KeypointField")
        keypoints = []
        for class_ind, p in enumerate(value, start=1):
            p = _validate_list_of_number(p, 3, float, "KeypointField")
            label = self.dom.get_label(class_ind)
            coord2d = Coord2D(x=p[0], y=p[1], visiable=int(p[2]), label=label)
            keypoints.append(coord2d)

        return KeyPoints(keypoints=keypoints, domain=self.dom)


class LabelField(Field):
    def __init__(self, dom: Union[ClassDomain, List[ClassDomain]], *args, **kwargs):
        """A DSDL Field to validate the given value and return a Label object.

        Args:
            dom: The class domain which the current keypoints object belongs to.

        Attributes:
            dom(ClassDomain): The class domain which the current keypoints object belongs to.
            dom_dic(Dict[str, ClassDomain]): The class domain which the current keypoints object belongs to. The format is `{<domain name>: class_domain}`
            dom_lst(List[ClassDomain]): The class domain which the current keypoints object belongs to. The format is `[class_domain1, class_domain2, ...]`
        """
        super(LabelField, self).__init__(*args, **kwargs)
        if not isinstance(dom, list):
            self.dom_lst = [dom]
        self.dom_dic = {_.__name__: _ for _ in self.dom_lst}
        self.dom = dom

    def validate(self, value: Optional[int, str]) -> Label:
        """Validate whether the given value is valid to represent a Label object.

        Args:
            value: A given value to represent a label object.

        Returns:
            A `Label` object.
        """
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
        """A DSDL Field to validate the given value and return a datetime object.

        Examples:
            >>> date_field = DateField(fmt="%Y-%m-%d")
            >>> value = "2020-06-06"
            >>> date_obj = data_field.validate(value)
            >>> data_obj.__class__.__name__
            "datetime"

        Args:
            fmt: The datetime format of the given value.

        Attributes:
            fmt(str): The datetime format of the given value.
        """
        super(DateField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value: str) -> datetime:
        """Validate whether the given value is valid to represent a datetime object.

        Args:
            value: A given value to represent a datetime object.

        Returns:
            A `datetime` object.
        """
        try:
            if self.fmt == "":
                return date.fromisoformat(value)
            return datetime.strptime(value, self.fmt).date()
        except Exception as e:
            raise RuntimeError(f"DateField Error: {e}")


class TimeField(Field):
    def __init__(self, fmt: str = "", *args, **kwargs):
        """A DSDL Field to validate the given value and return a time object.

        Examples:
            >>> time_field = TimeField(fmt="%Y-%m-%d %H:%M:%S")
            >>> value = "2020-06-06 23:03:15"
            >>> time_obj = time_field.validate(value)
            >>> time_obj.__class__.__name__
            "time"

        Args:
            fmt: The time format of the given value.

        Attributes:
            fmt(str): The time format of the given value.
        """
        super(TimeField, self).__init__(*args, **kwargs)
        self.fmt = fmt

    def validate(self, value: str) -> datetime.time:
        """Validate whether the given value is valid to represent a time object.

        Args:
            value: A given value to represent a time object.

        Returns:
            A `datetime.time` object.
        """
        try:
            if self.fmt == "":
                return time.fromisoformat(value)
            return datetime.strptime(value, self.fmt).time()
        except Exception as e:
            raise RuntimeError(f"TimeField Error: {e}")


class TextField(Field):
    """A DSDL Field to validate the given value and return a Text object.

    Examples:
        >>> txt_field = TextField()
        >>> value = "some text annotation"
        >>> txt_obj = txt_field.validate(value)
        >>> txt_obj.__class__.__name__
        "Text"
    """

    def validate(self, value: str) -> Text:
        """Validate whether the given value is valid to represent a text object.

        Args:
            value: A given value to represent a text object.

        Returns:
            A `Text` object.
        """
        try:
            return Text("" + value)
        except TypeError as _:
            raise ValidationError(f"TextField Error: expect str value, got {value}")


class ImageShapeField(Field):
    def __init__(self, mode: str = "hw", *args, **kwargs):
        """A DSDL Field to validate the given value and return an ImageShape object.

        Examples:
            >>> shape_field = ImageShapeField()
            >>> value = [360, 540]
            >>> shape_obj = shape_field.validate(value)
            >>> shape_obj.__class__.__name__
            "ImageShape"

        Args:
            mode: The format in which the value to be validated is given. Only `"wh"` and `"hw"` are permitted,
                  which respectly means the value is given by [width, height] and [height, width].

        Attributes:
            mode(str): The format in which the value to be validated is given. Only `"wh"` and `"hw"` are permitted,
                  which respectly means the value is given by [width, height] and [height, width].
        """
        super(ImageShapeField, self).__init__(*args, **kwargs)
        mode = mode.lower()
        assert mode in ("hw", "wh"), f"the mode of 'ImageShapeField' must be in {('hw', 'wh')}"
        self.mode = mode

    def validate(self, value: Iterable[int, int]) -> ImageShape:
        """Validate whether the given value is valid to represent an image shape object.

        Args:
            value: A given value to represent an image shape object.

        Returns:
            A `ImageShape` object.
        """
        value = _validate_list_of_number(value, 2, int, "ImageShapeField")
        return ImageShape(value=value, mode=self.mode)


class InstanceIDField(Field):
    """A DSDL Field to validate the given value and return a UniqueID object to represent an instance id.

    Examples:
        >>> ins_field = InstanceIDField()
        >>> value = "instance_100"
        >>> ins_obj = ins_field.validate(value)
        >>> ins_obj.__class__.__name__
        "UniqueID"
    """

    def validate(self, value: str) -> UniqueID:
        """Validate whether the given value is valid to represent an instance id object.

        Args:
            value: A given value to represent an instance id object.

        Returns:
            An `UniqueID` object.
        """
        try:
            return UniqueID("" + value, "InstanceID")
        except TypeError as _:
            raise ValidationError(f"InstanceIDField Error: expect str value, got {value}")


class UniqueIDField(Field):
    def __init__(self, id_type: Optional[str] = None, *args, **kwargs):
        """A DSDL Field to validate the given value and return an UniqueID object.

        Examples:
            >>> id_field = UniqueIDField(id_type="image_id")
            >>> value = "00000001"
            >>> id_obj = id_field.validate(value)
            >>> id_obj.__class__.__name__
            "UniqueID"

        Args:
            id_type: What the current unique id describes.

        Attributes:
            id_type(str): What the current unique id describes.
        """
        super().__init__(*args, **kwargs)
        self.id_type = id_type

    def validate(self, value: str) -> UniqueID:
        """Validate whether the given value is valid to represent an unique id object.

        Args:
            value: A given value to represent an unique id object.

        Returns:
            An `UniqueID` object.
        """
        try:
            return UniqueID("" + value, self.id_type)
        except TypeError as _:
            raise ValidationError(f"UniqueIDField Error: expect str value, got {value}")
