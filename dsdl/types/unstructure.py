from .field import Field
from ..geometry import ImageMedia


class FileReader(object):
    def __init__(self, file_reader, args):
        self._file_reader = file_reader
        self.args = args

    def read(self):
        reader = self._file_reader
        with reader.load(self.args["$loc"]) as f:
            return f.read()


class UnstructuredObjectField(Field):
    def __init__(self):
        super().__init__()
        self._file_reader = None

    def set_file_reader(self, file_reader):
        self._file_reader = file_reader

    @property
    def file_reader(self):
        return self._file_reader


class ImageField(UnstructuredObjectField):
    def __init__(self):
        super(ImageField, self).__init__()

    def validate(self, value):
        if isinstance(value, str):
            value = {"$loc": value}
        return ImageMedia(value["$loc"], FileReader(self.file_reader, value))
