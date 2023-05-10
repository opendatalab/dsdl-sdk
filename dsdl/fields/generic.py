from .base_field import BaseField


class Bool(BaseField):
    """A DSDL Field to validate and return a boolean value.

    Examples:
        >>> bool_field = Bool()
        >>> value = True
        >>> bool_field.validate(value)
        True
    """
    data_schema = {
        "$id": "/generic/boolean",
        "title": "BoolField",
        "description": "Bool field in dsdl.",
        "oneOf": [
            {"type": "boolean"},
            {"type": "number", "enum": [0, 1]}
        ]
    }
    geometry_class = bool


class Int(BaseField):
    """A DSDL Field to validate and return an int value.

    Examples:
        >>> int_field = Int()
        >>> value = 1.0
        >>> int_field.validate(value)
        1
    """
    data_schema = {
        "$id": "/generic/int",
        "title": "IntField",
        "description": "Int field in dsdl.",
        "type": "integer",
    }


class Num(BaseField):
    """A DSDL Field to validate and return a float value.

    Examples:
        >>> float_field = Num()
        >>> value = 1
        >>> float_field.validate(value)
        1.0
    """
    data_schema = {
        "$id": "/generic/num",
        "title": "NumField",
        "description": "Num field in dsdl.",
        "type": "number",
    }


class Str(BaseField):
    """A DSDL Field to validate and return a str value.

    Examples:
        >>> str_field = Str()
        >>> value = "test"
        >>> str_field.validate(value)
        "test"
    """
    data_schema = {
        "$id": "/generic/str",
        "title": "StrField",
        "description": "Str field in dsdl.",
        "type": "string",
    }


class Dict(BaseField):
    """A DSDL Field to validate and return a dict value.

    Examples:
        >>> dic_field = Dict()
        >>> value = {"1": "a"}
        >>> dic_field.validate(value)
        {"1": "a"}
    """
    data_schema = {
        "$id": "/generic/dict",
        "title": "DictField",
        "description": "Dict field in dsdl.",
        "type": "object",
    }
