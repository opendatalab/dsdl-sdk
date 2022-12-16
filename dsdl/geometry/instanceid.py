from .base_geometry import BaseGeometry


class InstanceID(BaseGeometry):

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"instance {self.value}"

    @property
    def field_key(self):
        return "InstanceID"
