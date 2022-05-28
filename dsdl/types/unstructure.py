from .field import Field


class ImageField(Field):
    def __init__(self):
        super(ImageField, self).__init__()

    def read(self):
        print(self.__get__(self))
