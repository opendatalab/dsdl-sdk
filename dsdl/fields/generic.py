from .base_field import BaseField


class Bool(BaseField):
    data_schema = {
        "$id": "/generic/boolean",
        "title": "BoolField",
        "description": "Bool field in dsdl.",
        "oneOf": [
            {"type": "boolean"},
            {"enum": [0, 1]}
        ]
    }
    geometry_class = bool


class Int(BaseField):
    data_schema = {
        "$id": "/generic/int",
        "title": "IntField",
        "description": "Int field in dsdl.",
        "type": "integer",
    }


class Num(BaseField):
    data_schema = {
        "$id": "/generic/num",
        "title": "NumField",
        "description": "Num field in dsdl.",
        "type": "number",
    }


class Str(BaseField):
    data_schema = {
        "$id": "/generic/str",
        "title": "StrField",
        "description": "Str field in dsdl.",
        "type": "string",
    }


class Dict(BaseField):
    data_schema = {
        "$id": "/generic/dict",
        "title": "DictField",
        "description": "Dict field in dsdl.",
        "type": "object",
    }
