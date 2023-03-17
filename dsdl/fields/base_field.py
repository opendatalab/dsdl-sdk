from copy import deepcopy
from jsonschema import validate, FormatChecker, Draft7Validator, ValidationError, SchemaError
from dsdl.geometry import GEOMETRY, CLASSDOMAIN, PlaceHolder, FIELD
from typing import Union, List as List_


class FieldMeta(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, FieldMeta)]
        if not parents:
            return super_new(mcs, name, bases, attributes)
        new_cls = super_new(mcs, name, bases, attributes)
        FIELD.register(name, new_cls)
        return new_cls


class BaseField(metaclass=FieldMeta):
    data_schema = {}
    args_schema = {
        "type": "object",
        "minProperties": 0,
        "maxProperties": 0,
    }
    default_args = {}
    geometry_class = None

    def __init__(self, **kwargs):
        all_kwargs = deepcopy(self.default_args)
        all_kwargs.update(kwargs)
        self.validate_schema(all_kwargs, self.args_schema)
        self.kwargs = all_kwargs

    # @classmethod
    # def get_schema(cls, **kwargs):
    #     schema = deepcopy(cls.data_schema)
    #     default_args = deepcopy(cls.default_args)
    #     default_args.update(kwargs)
    #
    #     cls.validate_schema(default_args, cls.args_schema)
    #     schema["dsdl_args"] = default_args
    #     return schema

    def additional_validate(self, value):
        return value

    @property
    def all_schema(self):
        default_all_schema = getattr(self.__class__, "whole_schema", None)
        all_schema = {
            "type": "object",
            "properties": {
                "args": self.args_schema,
                "value": self.data_schema
            },
            "required": ["args", "value"]
        }
        return default_all_schema or all_schema

    def validate_schema(self, data, schema):
        try:
            validate(data, schema, format_checker=FormatChecker(), cls=Draft7Validator)
        except SchemaError as e:
            raise SchemaError(f"SchemaError in {self.extract_key()[1:].capitalize()} field: \n  Schema is {schema}.\n  `{e}`")
        except ValidationError as e:
            raise ValidationError(
                f"ValidationError in {self.extract_key()[1:].capitalize()} field: \n  Schema is {schema}. \n  Data is {data}.\n  `{e}`")

    def validate_all_schema(self, value):
        all_data = {"value": value, "args": self.kwargs}
        self.validate_schema(all_data, self.all_schema)
        return self.additional_validate(value)

    def load_value(self, value):
        if self.geometry_class is None:
            return value
        if callable(self.geometry_class):
            return self.geometry_class(value, **self.kwargs)
        return GEOMETRY.get(self.geometry_class)(value, **self.kwargs)

    def validate(self, value):
        value = self.validate_all_schema(value)
        return self.load_value(value)

    @classmethod
    def extract_key(cls):
        field_cls_name = cls.__name__
        return "$" + field_cls_name.lower()

    def __call__(self, value):
        return self.validate(value)


class BaseFieldWithDomain(BaseField):
    _single_dom_schema = {"oneOf": [
        {"enum": CLASSDOMAIN.names_contained()},
        {"type": "string", "pattern": "^\$[a-zA-Z_]\w*$"}
    ]}

    dom_schema = {
        "type": "object",
        "properties": {
            "dom":
                {"oneOf": [
                    _single_dom_schema,
                    {"type": "array", "items": _single_dom_schema}
                ]}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["dom"]
    }

    def __init__(self, dom: Union[str, List_[str]], **kwargs):
        super().__init__(**kwargs)
        self.namespace = None
        self.validate_schema({"dom": dom}, self.dom_schema)
        self.arg_dom = PlaceHolder(dom)
        self.actural_dom = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        self.arg_dom.set_namespace(struct_obj)

    def get_actural_dom(self):
        actural_dom = self.arg_dom.validate()
        if isinstance(actural_dom, list):
            actural_dom = [CLASSDOMAIN.get(_) for _ in actural_dom]
        else:
            actural_dom = CLASSDOMAIN.get(actural_dom)
        self.actural_dom = actural_dom

    def validate(self, value):
        self.get_actural_dom()
        value = self.validate_all_schema(value)
        return self.load_value(value)

    def load_value(self, value):
        assert self.actural_dom is not None, "You should set namespace first."
        if self.geometry_class is None:
            return value
        if self.geometry_class.__class__.__name__ == "GeometryMeta":
            return self.geometry_class(value, dom=self.actural_dom, **self.kwargs)
        return GEOMETRY.get(self.geometry_class)(value, dom=self.actural_dom, **self.kwargs)


class List(BaseField):
    data_schema = {
        "$id": "/generic/list",
        "title": "ListField",
        "description": "List field in dsdl.",
        "type": "array",
        "items": {}
    }

    default_args = {"ordered": False}

    args_schema = {
        "type": "object",
        "properties": {
            "ordered": {"type": "boolean"}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["ordered"]
    }

    def __init__(self, etype, **kwargs):
        super().__init__(**kwargs)
        self.etype = etype
        self.namespace = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        if hasattr(self.etype, "set_namespace"):
            self.etype.set_namespace(struct_obj)

    def validate(self, value):
        res = [self.etype.validate(item) for item in value]
        return res
