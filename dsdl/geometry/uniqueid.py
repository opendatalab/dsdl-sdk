from .base_geometry import BaseGeometry


class UniqueID(BaseGeometry):

    def __init__(self, value, id_type):
        """A Geometry class which abstracts an unique id object.

        Args:
            value: The unique id value.
            id_type: The role which the current unique id plays, such as "frame id", "image id" or "annotation id".

        Attributes:
            _value: The unique id value.
            _field_key: The role which the current unique id plays, such as "frame id", "image id" or "annotation id".
        """
        self._value = value
        self._field_key = id_type

    @property
    def value(self):
        """
        Returns:
            The value of the current unique id.
        """
        return self._value

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        return f"ID type: {self._field_key} ID value: {self.value}"
