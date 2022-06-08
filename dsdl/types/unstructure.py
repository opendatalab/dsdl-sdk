from .field import Field


class FileReader(object):
    def __init__(self, dataset, args):
        self.dataset = dataset
        self.args = args

    def read(self):
        reader = self.dataset.config["UnstructuredObjectFileReader"]
        with reader.load(self.args["$loc"]) as f:
            return f.read()


class UnstructuredObjectField(Field):
    def __init__(self):
        super().__init__()
        self._dataset = None

    def set_dataset(self, dataset):
        self._dataset = dataset

    @property
    def dataset(self):
        return self._dataset


class ImageField(UnstructuredObjectField):
    def __init__(self):
        super(ImageField, self).__init__()

    def validate(self, value):
        if isinstance(value, str):
            value = {"$loc": value}
        return FileReader(self.dataset, value)
