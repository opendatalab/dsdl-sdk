from ..exception import StructHasDefinedError, StructNotFoundError


class Registry:
    def __init__(self):
        self.struct_map = {}

    def register(self, struct_name, struct_cls):
        if struct_name in self.struct_map:
            raise StructHasDefinedError
        self.struct_map[struct_name] = struct_cls

    def get_struct(self, name):
        if name not in self.struct_map:
            raise StructNotFoundError
        return self.struct_map[name]


registry = Registry()
