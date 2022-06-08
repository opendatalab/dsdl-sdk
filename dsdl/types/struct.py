from .field import Field
from .unstructure import UnstructuredObjectField
from .registry import registry
from ..exception import ValidationError


class _CacheKey:
    """Object to identify model in memory."""


class StructMetaclass(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, StructMetaclass)]
        if not parents:
            return super_new(mcs, name, bases, attributes)

        new_class = super_new(mcs, name, bases, attributes)
        registry.register(name, new_class)
        return new_class


class Struct(metaclass=StructMetaclass):
    def __init__(self, dataset, **kwargs):
        self._cache_key = _CacheKey()
        self.dataset = dataset
        self.populate(**kwargs)

    def populate(self, **values):
        values = values.copy()
        fields = list(self.iterate_with_name())
        for _, structure_name, field in fields:
            if structure_name in values:
                self.set_field(field, structure_name, values.pop(structure_name))
        for name, _, field in fields:
            if name in values:
                self.set_field(field, name, values.pop(name))

    def set_field(self, field, field_name, value):
        if isinstance(field, UnstructuredObjectField):
            field.set_dataset(self.dataset)
        try:
            field.__set__(self, value)
        except ValidationError as error:
            raise ValidationError(f"Error for field '{field_name}': {error}.")

    @classmethod
    def iterate_over_fields(cls):
        for attr in dir(cls):
            cls_attr = getattr(cls, attr)
            if isinstance(cls_attr, Field):
                yield attr, cls_attr

    @classmethod
    def iterate_with_name(cls):
        for attr_name, field in cls.iterate_over_fields():
            structure_name = field.structure_name(attr_name)
            yield attr_name, structure_name, field

    @property
    def cache_key(self):
        return self._cache_key
