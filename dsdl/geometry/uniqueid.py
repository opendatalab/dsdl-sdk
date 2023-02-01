"""
DSDL unique id Geometry.
"""
from .base_geometry import BaseGeometry


class UniqueID(BaseGeometry):
    def __init__(self, value: str, field_key: str):
        """A Geometry class which abstracts an unique id object.

        Args:
            value: The unique id value.
            field_key: The role which the current unique id plays, such as "frame id", "image id" or "annotation id".

        Attributes:
            _value: The unique id value.
            _field_key: The role which the current unique id plays, such as "frame id", "image id" or "annotation id".
        """
        self._value = value
        self._field_key = field_key

    @property
    def value(self) -> str:
        """
        Returns:
            The value of the current unique id.
        """
        return self._value

    def __eq__(self, other) -> bool:
        return self.value == other.value

    def __repr__(self) -> str:
        return f"ID type: {self._field_key} ID value: {self.value}"

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            `self._field_key`
        """
        return self._field_key
