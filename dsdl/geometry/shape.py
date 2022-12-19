from .base_geometry import BaseGeometry


class Shape(BaseGeometry):
    def __init__(self, value, mode, media):
        media = media.lower()
        mode = mode.lower()
        self._media_type = media
        self._value = value
        self._mode = mode

    @property
    def media_type(self):
        return self._media_type

    @property
    def value(self):
        return self._value

    @property
    def mode(self):
        return self._mode

    def __repr__(self):
        return f"{self.media_type} shape: {self.value}"


class ImageShape(Shape):
    def __init__(self, value, mode="hw"):
        assert mode.lower() in ("hw", "wh")
        super(ImageShape, self).__init__(value, mode.lower(), "image")
        if mode == "hw":
            self._height, self._width = value[0], value[1]
        else:
            self._width, self._height = value[0], value[1]

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    def __repr__(self):
        return f"image height: {self.height}; image width: {self.width}"

    @property
    def field_key(self):
        return "ImageShape"
