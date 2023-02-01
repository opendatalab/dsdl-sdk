"""DSDL Attributes Geometry."""
from .base_geometry import BaseGeometry
from typing import Hashable, Any, Iterable


class Attributes(BaseGeometry):
    def __init__(self, **kwargs):
        """An Geometry class which abstracts an attribute object containing many key-value pairs.

        Args:
            **kwargs: `kwargs` should be a `dict` object which contains all the key-value pair to be stored in the attribute object.

        Attributes:
            container(dict): A container which stores all the key-value pairs.
        """
        self.container = {}
        for k, v in kwargs.items():
            self.container[k] = v

    def __setitem__(self, key: Hashable, value: Any):
        """Set an attribute key and coresponding value.

        Args:
            key: The attribute key to be set.
            value: The attribute value to be set.

        Returns:
            None
        """
        self.container[key] = value

    def __getitem__(self, item) -> Any:
        """Get the coresponding value in the current attribute object given a key.

        Args:
            item: The key to be looked up.

        Returns:
            The value coresponding to the given key.
        """
        return self.container[item]

    def __contains__(self, item: Hashable) -> bool:
        """Judge whether a key is contained in the current attribute object.

        Args:
            item: The key value to be checked.

        Returns:
            `True` if contained, `False` otherwise.
        """
        return item in self.container

    def keys(self) -> Iterable:
        """Get an iterable object contains all the keys of the attribute object.

        Returns:
            An iterable object contains all the keys of the attribute object.
        """
        return self.container.keys()

    def values(self):
        """Get an Iterable object contains all the values of the attribute object.

        Returns:
            An iterable object contains all the values of the attribute object.
        """
        return self.container.values()

    def __repr__(self):
        return self.container.__repr__()

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "Attributes"
        """
        return "Attributes"
