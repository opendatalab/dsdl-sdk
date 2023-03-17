from .base_geometry import BaseGeometry


class UniqueID(BaseGeometry):

    def __init__(self, value, field_key):
        self._value = value
        self._field_key = field_key

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"ID type: {self._field_key} ID value: {self.value}"

    @property
    def field_key(self):
        return self._field_key
