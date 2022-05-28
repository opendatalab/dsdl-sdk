from .field import Field
from ..exception import ValidationError


class _CacheKey:
    """Object to identify model in memory."""


class StructMetaclass(type):
    def __new__(cls, name, bases, attributes):
        return super(cls, cls).__new__(cls, name, bases, attributes)


class Struct(metaclass=StructMetaclass):
    def __init__(self, **kwargs):
        self._cache_key = _CacheKey()
        self.populate(**kwargs)

    def populate(self, **values):
        """Populate values to fields. Skip non-existing."""
        values = values.copy()
        fields = list(self.iterate_with_name())
        for _, structure_name, field in fields:
            if structure_name in values:
                self.set_field(field, structure_name, values.pop(structure_name))
        for name, _, field in fields:
            if name in values:
                self.set_field(field, name, values.pop(name))

    def set_field(self, field, field_name, value):
        """Sets the value of a field."""
        try:
            field.__set__(self, value)
        except ValidationError as error:
            raise ValidationError(f"Error for field '{field_name}': {error}.")

    @classmethod
    def iterate_over_fields(cls):
        """Iterate through fields as `(attribute_name, field_instance)`."""
        for attr in dir(cls):
            cls_attr = getattr(cls, attr)
            if isinstance(cls_attr, Field):
                yield attr, cls_attr

    @classmethod
    def iterate_with_name(cls):
        """Iterate over fields, but also give `structure_name`.
        Format is `(attribute_name, structue_name, field_instance)`.
        Structure name is name under which value is seen in structure and
        schema (in primitives) and only there.
        """
        for attr_name, field in cls.iterate_over_fields():
            structure_name = field.structure_name(attr_name)
            yield attr_name, structure_name, field
