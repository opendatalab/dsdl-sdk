from .base_field import BaseField, BaseFieldWithDomain
from datetime import date, time
from dsdl.geometry import LABEL


class Coord(BaseField):
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
    data_schema = {
        "$id": "/special/bbox",
        "title": "BBoxField",
        "description": "Bounding box field in dsdl.",
        "type": "array",
        "items": [
            {"type": "number"},
            {"type": "number"},
            {"type": "number", "minimum": 0.},
            {"type": "number", "minimum": 0.},
        ],
        "minItems": 4,
        "maxItems": 4,
    }

    geometry_class = "BBox"


class RotatedBBox(BaseField):
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


class Keypoint(BaseFieldWithDomain):
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
    data_schema = {
        "$id": "/special/text",
        "title": "TextField",
        "description": "Text field in dsdl.",
        "type": "string"
    }

    geometry_class = "Text"


class ImageShape(BaseField):
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
    default_args = {"id_type": "InstanceID"}

    data_schema = {
        "$id": "/special/instanceid",
        "title": "InstanceIDField",
        "description": "InstanceID field in dsdl.",
        "type": "string"
    }


class Date(BaseField):
    data_schema = {
        "$id": "/special/date",
        "title": "DateField",
        "description": "Date field in dsdl.",
        "type": "string",
        "format": "date"
    }

    geometry_class = date.fromisoformat


class Time(BaseField):
    data_schema = {
        "$id": "/special/time",
        "title": "TimeField",
        "description": "Time field in dsdl.",
        "type": "string",
        "format": "time"
    }

    geometry_class = time.fromisoformat
