from copy import deepcopy
from dsdl.geometry import GEOMETRY, CLASSDOMAIN, PlaceHolder, FIELD
from typing import Union, List as List_
from fastjsonschema import compile, JsonSchemaDefinitionException, JsonSchemaValueException


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
    """
    The Parent Class of all fields.
    """
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
        _args_schema = self._compile_schema(self.args_schema)
        self.validate_schema(_args_schema, all_kwargs)
        self.kwargs = all_kwargs
        self._all_schema = self._compile_all_schema()

    @classmethod
    def validate_schema(cls, schema, data):
        try:
            schema(data)
        except JsonSchemaValueException as e:
            raise JsonSchemaValueException(
                f"ValidationError in {cls.extract_key()[1:].capitalize()} field: \n  Schema is {schema}. \n  Data is {data}.\n  `{e}`")
        return schema

    def additional_validate(self, value):
        return value

    @classmethod
    def _compile_schema(cls, schema):
        schema = schema.copy()
        schema["$schema"] = "http://json-schema.org/draft-07/schema"
        try:
            res = compile(schema)
        except JsonSchemaDefinitionException as e:
            raise JsonSchemaDefinitionException(
                f"SchemaError in {cls.extract_key()[1:].capitalize()} field: \n  `{e}`")
        return res

    @classmethod
    def _compile_all_schema(cls):

        default_all_schema = getattr(cls, "whole_schema", None)
        if default_all_schema is not None:
            default_all_schema["$schema"] = "http://json-schema.org/draft-07/schema"
            all_schema = default_all_schema
        else:
            all_schema = {
                "$schema": "http://json-schema.org/draft-07/schema",
                "type": "object",
                "properties": {
                    "args": cls.args_schema,
                    "value": cls.data_schema
                },
                "required": ["args", "value"]
            }
        try:
            compiled_all_schema = compile(all_schema)
        except JsonSchemaDefinitionException as e:
            raise JsonSchemaDefinitionException(
                f"SchemaError in {cls.extract_key()[1:].capitalize()} field: \n  `{e}`")
        return compiled_all_schema

    def validate_all_schema(self, value):
        all_data = {"value": value, "args": self.kwargs}
        self.validate_schema(self._all_schema, all_data)
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
        dom_schema = self._compile_schema({"dom": dom})
        self.validate_schema(dom_schema, self.dom_schema)
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
    """A DSDL Field to validate all the value in the given list and return a list of validated object.

    Examples:
        >>> from dsdl.fields import Dict
        >>> list_field = List(ele_type=Dict(), ordered=False)
        >>> value = [{"a": 1}, {"b": 2}, {"c": 3}]
        >>> list_field.validate(value)
        [{"a": 1}, {"b": 2}, {"c": 3}]

    Args:
        ele_type: The field type of the element in the given list value.
        ordered: Whether the order of the elements in the list should be contained.

    Attributes:
        ele_type(Union[Field, Struct]): The field type or struct type of the element in the given list value.
        ordered(bool): Whether the order of the elements in the list should be contained.
        file_reader(BaseFileReader): The file reader object which is needed when the ele_type is ImageField, LabelMapField or InstanceMapField.
        prefix(str): A helper prefix string which is used when initializing a Struct object.
        flatten_dic(Dict[str, Any]): A helper dict which is used in a Struct object.
    """
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
