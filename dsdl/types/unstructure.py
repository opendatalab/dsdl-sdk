from .field import Field
from ..geometry import ImageMedia, SegmentationMap, InstanceMap
from ..exception import ValidationError


class FileReader(object):
    def __init__(self, file_reader, args):
        self._file_reader = file_reader
        self.args = args

    def read(self):
        reader = self._file_reader
        with reader.load(self.args["$loc"]) as f:
            return f.read()


class UnstructuredObjectField(Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._file_reader = None

    def set_file_reader(self, file_reader):
        self._file_reader = file_reader

    @property
    def file_reader(self):
        return self._file_reader


class ImageField(UnstructuredObjectField):
    def __init__(self, *args, **kwargs):
        super(ImageField, self).__init__(*args, **kwargs)

    def validate(self, value):
        if isinstance(value, str):
            value = {"$loc": value}
        else:
            raise ValidationError(f"ImageField Error: expect str, got {value}")
        return ImageMedia(value["$loc"], FileReader(self.file_reader, value))


class LabelMapField(UnstructuredObjectField):
    def __init__(self, dom, *args, **kwargs):
        super(LabelMapField, self).__init__(*args, **kwargs)
        self.dom = dom

    def validate(self, value):
        if isinstance(value, str):
            value = {"$loc": value}
        else:
            raise ValidationError(f"LabelField Error: expect str, got {value}")
        return SegmentationMap(value['$loc'], FileReader(self.file_reader, value), self.dom)


class InstanceMapField(UnstructuredObjectField):
    def __init__(self, *args, **kwargs):
        super(InstanceMapField, self).__init__(*args, **kwargs)

    def validate(self, value):
        if isinstance(value, str):
            value = {"$loc": value}
        else:
            raise ValidationError(f"InstanceMapField Error: expect str, got {value}")
        return InstanceMap(value['$loc'], FileReader(self.file_reader, value))
