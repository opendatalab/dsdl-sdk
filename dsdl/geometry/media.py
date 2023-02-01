"""
DSDL Image Geometry.
"""
import io

import numpy as np
from PIL import Image
from ..exception import FileReadError
from .base_geometry import BaseGeometry
from .utils import bytes_to_numpy
from ..objectio import BaseFileReader


class ImageMedia(BaseGeometry):

    def __init__(self, location: str, file_reader:BaseFileReader):
        """A Geometry class which abstracts an image object.

        Args:
            location: The relative path of the current image object.
            file_reader: The file reader object of the current image object.
        """
        self._loc = location
        self._reader = file_reader

    @property
    def location(self) -> str:
        """
        Returns:
            The relative path of the current image.
        """
        return self._loc

    def to_bytes(self) -> io.BytesIO:
        """Turn ImageMedia object to bytes.

        Returns:
            The bytes of the current image.
        """
        return io.BytesIO(self._reader.read())

    def to_image(self) -> Image:
        """Turn ImageMedia object to a `PIL.Image` object.

        Returns:
            The `PIL.Image` object of the current image.
        """
        try:
            img = Image.open(self.to_bytes())
        except Exception as e:
            raise FileReadError(f"Failed to convert bytes to an array. {e}") from None
        return img

    def to_array(self) -> np.array:
        """Turn ImageMedia object to numpy.ndarray.

        Returns:
            The `np.ndarray` object of the current image.
        """
        return bytes_to_numpy(self.to_bytes())

    def __repr__(self) -> str:
        return f"path:{self.location}"

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "Image"
        """
        return "Image"
