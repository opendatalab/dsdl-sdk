from .base_geometry import BaseGeometry


class UniqueID(BaseGeometry):

    def __init__(self, value, id_type):
        self._value = value
        self._field_key = id_type

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"ID type: {self._field_key} ID value: {self.value}"
