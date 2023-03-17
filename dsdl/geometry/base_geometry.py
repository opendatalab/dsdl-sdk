class BaseGeometry:

    def visualize(self, image, palette, **kwargs):
        return image

    def __repr__(self):
        return self.__class__.__name__ + " object"

    @property
    def field_key(self):
        return self.__class__.__name__


class FontMixin:
    FONT = None

    @classmethod
    def set_font(cls, font):
        cls.FONT = font

    @property
    def font(self):
        return self.FONT
