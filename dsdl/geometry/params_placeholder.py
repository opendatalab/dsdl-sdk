from typing import Union, List


class PlaceHolderItem:
    def __init__(self, value: str):
        self.value = None
        self.arg_name = None
        self.namespace = None
        if value.startswith("$"):
            self.arg_name = value[1:]
        else:
            self.value = value

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj

    def validate(self):
        if self.value is None:
            assert self.namespace is not None, "You should set namespace before validating."
            self.value = self.namespace.params[self.arg_name].validate()
        return self.value


class PlaceHolder:
    def __init__(self, value: Union[str, List[str]]):
        if isinstance(value, list):
            self.value = [PlaceHolderItem(_) for _ in value]
        else:
            self.value = PlaceHolderItem(value)
        self.namespace = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        if isinstance(self.value, list):
            for item in self.value:
                item.set_namespace(struct_obj)
        else:
            self.value.set_namespace(struct_obj)

    def validate(self):
        if isinstance(self.value, list):
            return [_.validate() for _ in self.value]
        return self.value.validate()
