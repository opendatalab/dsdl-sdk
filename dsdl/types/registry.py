from ..exception import ClassHasDefinedError, ClassNotFoundError


class Registry:
    def __init__(self, name):
        self._name = name
        self._map = {}

    @property
    def name(self):
        return self._name

    def register(self, name, cls):
        # NOTICE: Since this method is called when models are imported,
        # it cannot perform imports because of the risk of import loops.
        if name in self._map:
            raise ClassHasDefinedError
        self._map[name] = cls

    def get(self, name):
        if name not in self._map:
            raise ClassNotFoundError
        return self._map[name]


STRUCT = Registry("struct")
CLASSDOMAIN = Registry("class domain")


class LabelRegistry:
    def __init__(self):
        self._labels = {}

    def registry(self, label):
        registry_name = label.registry_name
        if registry_name in self._labels:
            raise ClassHasDefinedError
        self._labels[registry_name] = label

    def get(self, registry_name):
        if registry_name not in self._labels:
            raise ClassNotFoundError
        return self._labels[registry_name]

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._labels
        elif hasattr(item, "registry_name"):
            return item.registry_name in self._labels
        else:
            return False


LABEL = LabelRegistry()
