from .field import Field


class CoordField(Field):
    def __init__(self):
        super(CoordField, self).__init__()


class LabelField(Field):
    def __init__(self, dom):
        super(LabelField, self).__init__()
