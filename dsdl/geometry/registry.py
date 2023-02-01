"""
The Registry class to register all the `dsdl.types.Struct` classes or the `dsdl.geometry.ClassDomain` classes or the `dsdl.geometry.Label` objects.
"""
from ..exception import ClassNotFoundError
from ..warning import ClassHasDefinedWarning


class Registry:
    def __init__(self, name: str):
        """A collection to register given `dsdl.types.Struct` classes or `dsdl.geometry.ClassDomain` classes.

        Args:
            name: The name of the current `Registry` object.
        """
        self._name = name
        self._map = {}

    @property
    def name(self) -> str:
        """
        Returns:
            The name of the current `Registry` object.
        """
        return self._name

    def register(self, name, cls):
        """Register a given `Struct` or `ClassDomain` class into the current `Registry` object.
        Args:
            name(str): The registry name of the given `Struct` class.
            cls(dsdl.types.Struct or dsdl.geometry.ClassDomain): The `Struct` class to be registered.
        """
        # NOTICE: Since this method is called when models are imported,
        # it cannot perform imports because of the risk of import loops.
        if name in self._map:
            # raise ClassHasDefinedError
            ClassHasDefinedWarning(f"Class '{name}' has been registered, it will be replaced by this updated one.")
        self._map[name] = cls

    def get(self, name):
        """Get the `Struct` class when given the registry name.

        Args:
            name: The registry name to be queried.

        Returns:
            (dsdl.types.Struct or dsdl.geometry.ClassDomain): The `Struct` class coresponding the given registry name.
        """
        if name not in self._map:
            raise ClassNotFoundError(f"Class '{name}' is not defined.")
        return self._map[name]

    def clear(self):
        """Clear all the registered classes in the current `Registry` object.
        """
        self._map = {}


STRUCT = Registry("struct")
CLASSDOMAIN = Registry("class domain")


class LabelRegistry:
    def __init__(self):
        """A collection to register given `dsdl.geometry.Label` objects.
        """
        self._labels = {}

    def registry(self, label):
        """Register a given `Label` objects into the current `Registry` object.
        Args:
            label(dsdl.geometry.Label): The `Label` object to be registered.
        """
        registry_name = label.registry_name
        if registry_name in self._labels:
            # raise ClassHasDefinedError(f"The label {label.registry_name} has been registered.")
            ClassHasDefinedWarning(
                f"The label {label.registry_name} has been registered, it will be replaced bt this updated one.")
        self._labels[registry_name] = label

    def get(self, registry_name):
        """Get the `Label` object when given the registry name.

        Args:
            name: The registry name to be queried.

        Returns:
            (dsdl.geometry.Label): The `Label` object coresponding the given registry name.
        """
        if registry_name not in self._labels:
            raise ClassNotFoundError
        return self._labels[registry_name]

    def __contains__(self, item) -> bool:
        """Whether the current `Registry` object contains a given object.

        Args:
            item(str or dsdl.geometry.Label): The object or the registry name to be quried.

        Returns:
            Whether the current `Registry` object contains a given object.
        """
        if isinstance(item, str):
            return item in self._labels
        elif hasattr(item, "registry_name"):
            return item.registry_name in self._labels
        else:
            return False

    def clear(self):
        """Clear all the registered objects in the current `Registry` object.
        """
        self._labels = {}


LABEL = LabelRegistry()
