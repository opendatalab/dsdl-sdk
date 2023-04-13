from .base_field import BaseField, BaseFieldWithDomain
from datetime import date, time, datetime
from dsdl.geometry import LABEL


class Coord(BaseField):
    """A DSDL Field to validate and return a 2D coordinate object.

    Examples:
        >>> coord_field = Coord()
        >>> value = [10, 10]
        >>> coord_field.validate(value)
        [10.0, 10.0]
    """
    data_schema = {
        "$id": "/special/coord",
        "title": "CoordField",
        "description": "Coord 2D field in dsdl.",
        "type": "array",
        "items": {
            "type": "number",
        },
        "minItems": 2,
        "maxItems": 2
    }


class Coord3D(BaseField):
    """
    A DSDL Field to validate and return a 3D coordinate object.

    Examples:
        >>> coord3d_field = Coord3D()
        >>> value = [10, 10, 10]
        >>> coord3d_field.validate(value)
        [10.0, 10.0, 10.0]
    """
    data_schema = {
        "$id": "/special/coord3d",
        "title": "Coord3DField",
        "description": "Coord 3D field in dsdl.",
        "type": "array",
        "items": {
            "type": "number",
        },
        "minItems": 3,
        "maxItems": 3
    }


class Interval(BaseField):
    """
    A DSDL Field to validate and return an interval object.

    Examples:
        >>> interval_field = Interval()
        >>> value = [0, 10]
        >>> interval_field.validate(value)
        [0.0, 10.0]
    """
    data_schema = {  # 无法定义顺序
        "$id": "/special/interval",
        "title": "IntervalField",
        "description": "Interval field in dsdl.",
        "type": "array",
        "items": {
            "type": "number",
        },
        "minItems": 2,
        "maxItems": 2,
    }

    def additional_validate(self, value):
        assert value[0] <= value[1]
        return value


class BBox(BaseField):
    """
    A DSDL Field to validate the given value and return a BBox object.

    Examples:
        >>> bbox_field = BBox()
        >>> value = [0, 10, 100, 100]  # [x, y, w, h]
        >>> bbox_obj = bbox_field.validate(value)
        >>> bbox_obj.__class__.__name__
        "BBox"
    """
    default_args = {
        "mode": "xywh"
    }

    args_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["xywh", "xyxy"]}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["mode"]
    }

    data_schema = {
        "$id": "/special/bbox",
        "title": "BBoxField",
        "description": "Bounding box field in dsdl.",
        "type": "array",
        "items": {"type": "number"},
        "minItems": 4,
        "maxItems": 4,
    }

    whole_schema = {
        "type": "object",
        "oneOf": [
            {
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "enum": ["xywh"]}
                        },
                        "minProperties": 1,
                        "maxProperties": 1,
                        "required": ["mode"]
                    },
                    "value": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": [{"type": "number"}, {"type": "number"}, {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0}]
                    }
                }
            },

            {
                "properties": {
                    "args": {"type": "object",
                             "properties": {
                                 "mode": {"type": "string", "enum": ["xyxy"]}
                             },
                             "minProperties": 1,
                             "maxProperties": 1,
                             "required": ["mode"]},
                    "value": {"type": "array", "minItems": 4, "maxItems": 4, "items": {"type": "number"}}
                }
            }
        ],
        "required": ["args", "value"]
    }

    geometry_class = "BBox"


class RotatedBBox(BaseField):
    """A DSDL Field to validate the given value and return a RBBox object.

    Examples:
        >>> rotatedbbox_field = RotatedBBox(measure="degree")
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
    default_args = {
        "mode": "xywht",
        "measure": "radian"
    }

    data_schema = {
        "$id": "/special/rotatedbbox",
        "title": "RotatedBBoxField",
        "description": "Rotated bounding box field in dsdl.",
        "type": "array",
        "oneOf": [
            {"minItems": 5, "maxItems": 5,
             "items": [{"type": "number"}, {"type": "number"}, {"type": "number", "minimum": 0},
                       {"type": "number", "minimum": 0}, {"type": "number"}]},
            {"minItems": 8, "maxItems": 8, "items": {"type": "number"}}
        ]
    }

    args_schema = {
        "type": "object",
        "properties": {
            "measure": {"type": "string", "enum": ["radian", "degree"]},
            "mode": {"type": "string", "enum": ["xywht", "xyxy"]}
        },
        "minProperties": 2,
        "maxProperties": 2,
        "required": ["measure", "mode"]
    }

    whole_schema = {
        "type": "object",
        "oneOf": [
            {
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "measure": {"type": "string", "enum": ["radian", "degree"]},
                            "mode": {"type": "string", "enum": ["xywht"]}
                        },
                        "minProperties": 2,
                        "maxProperties": 2,
                        "required": ["measure", "mode"]
                    },
                    "value": {
                        "type": "array",
                        "minItems": 5,
                        "maxItems": 5,
                        "items": [{"type": "number"}, {"type": "number"}, {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0}, {"type": "number"}]
                    }
                }
            },

            {
                "properties": {
                    "args": {"type": "object",
                             "properties": {
                                 "measure": {"type": "string", "enum": ["radian", "degree"]},
                                 "mode": {"type": "string", "enum": ["xyxy"]}
                             },
                             "minProperties": 2,
                             "maxProperties": 2,
                             "required": ["measure", "mode"]},
                    "value": {"type": "array", "minItems": 8, "maxItems": 8, "items": {"type": "number"}}
                }
            }
        ],
        "required": ["args", "value"]
    }

    geometry_class = "RBBox"


class Polygon(BaseField):
    """
    A DSDL Field to validate the given value and return a polygon object.

    Examples:
        >>> polygon_field = Polygon()
        >>> value = [[[0, 0], [0, 100], [100, 100], [100, 0]], [[0, 0], [0, 50], [50, 50], [50, 0]]]
        >>> polygon_obj = polygon_field.validate(value)
        >>> polygon_obj.__class__.__name__
        "Polygon"
    """
    data_schema = {
        "$id": "/special/polygon",
        "title": "PolygonField",
        "description": "Polygon field in dsdl.",
        "type": "array",
        "items": {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "number"},
                "minItems": 2,
                "maxItems": 2,
            }
        }
    }

    geometry_class = "Polygon"


class Label(BaseFieldWithDomain):
    """A DSDL Field to validate the given value and return a Label object.

    Args:
        dom: The class domain which the current keypoints object belongs to.

    Attributes:
        dom(ClassDomain): The class domain which the current keypoints object belongs to.
        dom_dic(Dict[str, ClassDomain]): The class domain which the current keypoints object belongs to. The format is `{<domain name>: class_domain}`
        dom_lst(List[ClassDomain]): The class domain which the current keypoints object belongs to. The format is `[class_domain1, class_domain2, ...]`
    """
    data_schema = {
        "$id": "/special/label",
        "title": "LabelField",
        "description": "Label field in dsdl.",
        "type": ["string", "integer"]
    }

    def load_value(self, value):
        assert self.actural_dom is not None, "You should set namespace before validating."
        if (isinstance(value, int) or (isinstance(value, str) and "::" not in value)):
            assert not isinstance(self.actural_dom, list) or \
                   (isinstance(self.actural_dom, list) and len(self.actural_dom) == 1), \
                "LabelField Error: there are more than 1 domains in the struct, " \
                "you need to specify the label's class domain explicitly."
            domain = self.actural_dom[0] if isinstance(self.actural_dom, list) else self.actural_dom
            label_name = value
            return domain.get_label(label_name)
        if isinstance(value, str) and "::" in value:
            label_registry_name = value.replace("::", "__")
            assert label_registry_name in LABEL, f"Label '{label_registry_name}' is not valid."
            return LABEL.get(label_registry_name)


class BBox3D(BaseField):
    default_args = {"mode": "auto-drive"}

    args_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["auto-drive", "indoor"]}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["mode"]
    }

    data_schema = {
        "$id": "/special/bbox3d",
        "title": "BBox3DField",
        "description": "BBox3D Field in dsdl.",
        "type": "array",
        "oneOf": [
            {"minItems": 7, "maxItems": 7,
             "items": [{"type": "number"},
                       {"type": "number"},
                       {"type": "number"},
                       {"type": "number", "minimum": 0},
                       {"type": "number", "minimum": 0},
                       {"type": "number", "minimum": 0},
                       {"type": "number"}]},
            {"minItems": 9, "maxItems": 9,
             "items": [{"type": "number"},
                       {"type": "number"},
                       {"type": "number"},
                       {"type": "number", "minimum": 0},
                       {"type": "number", "minimum": 0},
                       {"type": "number", "minimum": 0},
                       {"type": "number"},
                       {"type": "number"},
                       {"type": "number"}]}
        ]
    }

    whole_schema = {
        "type": "object",
        "oneOf": [
            {
                "properties": {
                    "args": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "enum": ["auto-drive"]}
                        },
                        "minProperties": 1,
                        "maxProperties": 1,
                        "required": ["mode"]
                    },
                    "value": {
                        "type": "array",
                        "minItems": 7, "maxItems": 7,
                        "items": [{"type": "number"},
                                  {"type": "number"},
                                  {"type": "number"},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number"}]
                    }
                }
            },

            {
                "properties": {
                    "args": {"type": "object",
                             "properties": {
                                 "mode": {"type": "string", "enum": ["indoor"]}
                             },
                             "minProperties": 1,
                             "maxProperties": 1,
                             "required": ["mode"]},
                    "value": {
                        "type": "array",
                        "minItems": 9, "maxItems": 9,
                        "items": [{"type": "number"},
                                  {"type": "number"},
                                  {"type": "number"},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number", "minimum": 0},
                                  {"type": "number"},
                                  {"type": "number"},
                                  {"type": "number"}]}
                }
            }
        ],
        "required": ["args", "value"]
    }

    geometry_class = "BBox3D"


class Keypoint(BaseFieldWithDomain):
    """A DSDL Field to validate the given value and return a Keypoints object.

    Args:
        dom: The class domain which the current keypoints object belongs to.

    Attributes:
        dom(ClassDomain): The class domain which the current keypoints object belongs to.
    """
    data_schema = {
        "$id": "/special/keypoint",
        "title": "KeypointField",
        "description": "Keypoint Field in dsdl.",
        "type": "array",
        "items": {
            "type": "array",
            "items": {
                "type": "number"
            },
            "minItems": 3,
            "maxItems": 3,
        }
    }

    geometry_class = "KeyPoints"

    def additional_validate(self, value):
        dom = self.actural_dom
        if isinstance(self.actural_dom, list):
            assert len(self.actural_dom) == 1, "You can only assign one class dom in KeypointField."
            dom = self.actural_dom[0]
        assert len(dom) == len(value), \
            "The number of points should be equal to the labels in class domain."
        assert dom.get_attribute("skeleton") is not None, \
            f"You should assign skeletons for class domain {dom.__name__}."
        return value


class Text(BaseField):
    """A DSDL Field to validate the given value and return a Text object.

    Examples:
        >>> txt_field = Text()
        >>> value = "some text annotation"
        >>> txt_obj = txt_field.validate(value)
        >>> txt_obj.__class__.__name__
        "Text"
    """
    data_schema = {
        "$id": "/special/text",
        "title": "TextField",
        "description": "Text field in dsdl.",
        "type": "string"
    }

    geometry_class = "Text"


class ImageShape(BaseField):
    """A DSDL Field to validate the given value and return an ImageShape object.

    Examples:
        >>> shape_field = ImageShape()
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
    default_args = {"mode": "hw"}

    data_schema = {
        "$id": "/special/imageshape",
        "title": "ImageShapeField",
        "description": "ImageShape field in dsdl.",
        "type": "array",
        "items": {"type": "integer", "minimum": 0},
        "minItems": 2,
        "maxItems": 2,
    }

    args_schema = {
        "type": "object",
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["hw", "wh"]
            }
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["mode"]
    }

    geometry_class = "ImageShape"


class UniqueID(BaseField):
    """A DSDL Field to validate the given value and return an UniqueID object.

    Examples:
        >>> id_field = UniqueID(id_type="image_id")
        >>> value = "00000001"
        >>> id_obj = id_field.validate(value)
        >>> id_obj.__class__.__name__
        "UniqueID"

    Args:
        id_type: What the current unique id describes.

    Attributes:
        id_type(str): What the current unique id describes.
    """
    default_args = {"id_type": None}
    data_schema = {
        "$id": "/special/uniqueid",
        "title": "UniqueIDField",
        "description": "UniqueID field in dsdl.",
        "type": "string"
    }
    args_schema = {
        "type": "object",
        "properties": {
            "id_type": {"type": ["string", "null"]}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["id_type"]
    }

    geometry_class = "UniqueID"


class InstanceID(UniqueID):
    """A DSDL Field to validate the given value and return a UniqueID object to represent an instance id.

    Examples:
        >>> ins_field = InstanceID()
        >>> value = "instance_100"
        >>> ins_obj = ins_field.validate(value)
        >>> ins_obj.__class__.__name__
        "UniqueID"
    """
    default_args = {"id_type": "InstanceID"}

    data_schema = {
        "$id": "/special/instanceid",
        "title": "InstanceIDField",
        "description": "InstanceID field in dsdl.",
        "type": "string"
    }


class Date(BaseField):
    """A DSDL Field to validate the given value and return a datetime object.

    Examples:
        >>> date_field = Date(fmt="%Y-%m-%d")
        >>> value = "2020-06-06"
        >>> date_obj = date_field.validate(value)
        >>> date_obj.__class__.__name__
        "datetime"

    Args:
        fmt: The datetime format of the given value.

    Attributes:
        fmt(str): The datetime format of the given value.
    """
    data_schema = {
        "$id": "/special/date",
        "title": "DateField",
        "description": "Date field in dsdl.",
        "type": "string",
        "format": "date"
    }

    default_args = {"fmt": ""}

    args_schema = {
        "type": "object",
        "properties": {
            "fmt": {"type": "string"}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["fmt"]
    }

    def load_value(self, value):
        if self.kwargs["fmt"]:
            return datetime.strptime(value, self.kwargs["fmt"]).date()
        else:
            return date.fromisoformat(value)


class Time(BaseField):
    """A DSDL Field to validate the given value and return a time object.

    Examples:
        >>> time_field = Time(fmt="%Y-%m-%d %H:%M:%S")
        >>> value = "2020-06-06 23:03:15"
        >>> time_obj = time_field.validate(value)
        >>> time_obj.__class__.__name__
        "time"

    Args:
        fmt: The time format of the given value.

    Attributes:
        fmt(str): The time format of the given value.
    """
    data_schema = {
        "$id": "/special/time",
        "title": "TimeField",
        "description": "Time field in dsdl.",
        "type": "string",
        "format": "time"
    }

    default_args = {"fmt": ""}

    args_schema = {
        "type": "object",
        "properties": {
            "fmt": {"type": "string"}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["fmt"]
    }

    def load_value(self, value):
        if self.kwargs["fmt"]:
            return datetime.strptime(value, self.kwargs["fmt"]).time()
        else:
            return date.fromisoformat(value)
