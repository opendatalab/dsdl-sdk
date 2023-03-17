from .registry import GEOMETRY


class GeometryMeta(type):
    def __new__(mcs, name, bases, attributes):
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, GeometryMeta)]
        if not parents:
            return super_new(mcs, name, bases, attributes)
        new_cls = super_new(mcs, name, bases, attributes)
        GEOMETRY.register(name, new_cls)
        return new_cls


class BaseGeometry(metaclass=GeometryMeta):

    def visualize(self, image, palette, **kwargs):
        return image

    def __repr__(self):
        return self.__class__.__name__ + " object"


class FontMixin:
    FONT = None

    @classmethod
    def set_font(cls, font):
        cls.FONT = font

    @property
    def font(self):
        return self.FONT
