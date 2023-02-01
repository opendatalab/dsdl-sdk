"""
DSDL Instance Map Geometry.
"""
import io
from PIL import Image
from ..exception import FileReadError
from .utils import bytes_to_numpy
import numpy as np
import cv2
from ..objectio import BaseFileReader
from .base_geometry import BaseGeometry


class InstanceMap(BaseGeometry):
    def __init__(self, location: str, file_reader: BaseFileReader):
        """A Geometry class which abstracts an instance map object.

        Args:
            location: The relative path of the current instance map object.
            file_reader: The file reader object of the current instance map object.
        """
        self._loc = location
        self._reader = file_reader

    @property
    def location(self) -> str:
        """
        Returns:
            The relative path of the current instance map.
        """
        return self._loc

    def to_bytes(self) -> io.BytesIO:
        """Turn InstanceMap object to bytes.

        Returns:
            The bytes of the current instance map.
        """
        return io.BytesIO(self._reader.read())

    def to_image(self) -> Image:
        """Turn InstanceMap object to a `PIL.Image` object.

        Returns:
            The `PIL.Image` object of the current instance map.
        """
        try:
            img = Image.open(self.to_bypes())
        except Exception as e:
            raise FileReadError(f"Failed to convert bytes to an array. {e}") from None
        return img

    def to_array(self) -> np.array:
        """Turn InstanceMap object to numpy.ndarray.

        Returns:
            The `np.ndarray` object of the current instance map.
        """
        return bytes_to_numpy(self.to_bypes())

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current instance map on an given image.

        Args:
            image: The image where the instance map to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current instance map.

        Returns:
            The image where the current instance map has been drawn on.
        """
        ins_map = self.to_array()
        color_map = np.zeros((ins_map.shape[0], ins_map[1], 3), dtype=np.uint8)
        ins_ids = np.unique(ins_map)

        for ins_id in ins_ids:
            if ins_id == 0:
                continue
            contour_color = tuple(np.random.randint(0, 255, size=[3]))
            this_map = (ins_map == ins_id).astype(np.uint8) * 255
            _, contours, _ = cv2.findContours(this_map, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(color_map, contours, -1, contour_color, 2)

        overlay = Image.fromarray(color_map).convert("RGBA")
        overlayed = Image.blend(image, overlay, 0.5)
        return overlayed

    def __repr__(self) -> str:
        return f"path:{self.location}"

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "InstanceMap"
        """
        return "InstanceMap"
