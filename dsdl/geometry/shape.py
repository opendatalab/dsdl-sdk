"""
DSDL Shape Geometry.
"""
from .base_geometry import BaseGeometry
from typing import List


class Shape(BaseGeometry):
    def __init__(self, value: List[int], mode: str, media: str):
        """A Geometry class which abstracts a media's shape.

        Args:
            value: A list which contains the shape information of the media.
            mode: The shape mode, which represents the format of media'shape. For Exsample, an image shape's mode can be "hw" or "wh".
            media: The media type, such as "image", "video" and so on.

        Attributes:
            _value(list[int]): The shape value of the media.
            _media_type(str): The type of the media.
            _mode(str): The mode of the media's shape.
        """
        media = media.lower()
        mode = mode.lower()
        self._media_type = media
        self._value = value
        self._mode = mode

    @property
    def media_type(self) -> str:
        """
        Returns:
            The media type of the current Shape object.
        """
        return self._media_type

    @property
    def value(self) -> List[int]:
        """
        Returns:
            The shape value.
        """
        return self._value

    @property
    def mode(self) -> str:
        """
        Returns:
            The mode of the shape.
        """
        return self._mode

    def __repr__(self):
        return f"{self.media_type} shape: {self.value}"


class ImageShape(Shape):
    def __init__(self, value: List[int], mode: str = "hw"):
        """A Geometry class which abstracts an image's shape.

        Args:
            value: A list which contains the width and height of the image.
            mode: The shape mode, value should be `"hw"` or `"wh"`. When `mode=="hw"`, the `value` arg should be image's [height, width]
                when `mode=="wh"', the `value` arg should be images's [width, height]

        Attributes:
            _width(int): The width of the image.
            _height(int): The height of the image.
        """
        assert mode.lower() in ("hw", "wh")
        super(ImageShape, self).__init__(value, mode.lower(), "image")
        if mode == "hw":
            self._height, self._width = value[0], value[1]
        else:
            self._width, self._height = value[0], value[1]

    @property
    def height(self) -> int:
        """
        Returns:
            The height of the image.
        """
        return self._height

    @property
    def width(self) -> int:
        """
        Returns:
            The width of the image.
        """
        return self._width

    def __repr__(self):
        return f"{self.media_type} height: {self.height}; {self.media_type} width: {self.width}"

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "ImageShape"
        """
        return "ImageShape"
