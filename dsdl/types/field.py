from weakref import WeakKeyDictionary

NotSet = object()


class Field:
    default_validators = []

    def __init__(self, name=None, default=NotSet):
        self.memory = WeakKeyDictionary()
        self.name = name
        self._default = default

    def __set__(self, instance, value):
        self.memory[instance._cache_key] = value

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if instance._cache_key not in self.memory:
            self.__set__(instance, self.get_default_value())
        return self.memory[instance._cache_key]

    def __str__(self):
        return "<%s>" % self.__class__.__name__

    @property
    def has_default(self):
        return self._default is not NotSet

    def get_default_value(self):
        return self._default if self.has_default else None

    def structure_name(self, default):
        return self.name if self.name is not None else default
