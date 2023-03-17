from .base_field import BaseField, BaseFieldWithDomain
from dsdl.geometry import GEOMETRY


class UnstructuredObjectField(BaseField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.namespace = None
        self.file_reader = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        self.file_reader = struct_obj.file_reader

    def load_value(self, value):
        assert self.file_reader is not None, "You should set namespace before validating."
        if self.geometry_class is None:
            raise RuntimeError("You should assign a geometry class.")
        if self.geometry_class.__class__.__name__ == "GeometryMeta":
            return self.geometry_class(value, file_reader=self.file_reader, **self.kwargs)
        return GEOMETRY.get(self.geometry_class)(value, file_reader=self.file_reader, **self.kwargs)


class UnstructuredObjectFieldWithDomain(BaseFieldWithDomain):
    def __init__(self, dom, **kwargs):
        super().__init__(dom, **kwargs)
        self.file_reader = None

    def set_namespace(self, struct_obj):
        super().set_namespace(struct_obj)
        self.file_reader = struct_obj.file_reader

    def load_value(self, value):
        print(value)
        assert self.file_reader is not None and self.actural_dom is not None, \
            "You should set namespace before validating."
        if self.geometry_class is None:
            raise RuntimeError("You should assign a geometry class.")
        if self.geometry_class.__class__.__name__ == "GeometryMeta":
            return self.geometry_class(value, file_reader=self.file_reader, dom=self.actural_dom, **self.kwargs)
        return GEOMETRY.get(self.geometry_class)(value, file_reader=self.file_reader, dom=self.actural_dom,
                                                 **self.kwargs)
