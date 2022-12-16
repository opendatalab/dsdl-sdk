import io
from PIL import Image
from ..exception import FileReadError
from .utils import bytes_to_numpy
import numpy as np
import cv2

from .base_geometry import BaseGeometry


class InstanceMap(BaseGeometry):
    """
    A Geometry class for instance segmentation map
    """

    def __init__(self, location, file_reader):
        self._loc = location
        self._reader = file_reader

    @property
    def location(self):
        return self._loc

    def to_bypes(self):
        """
        turn InstanceMap object to bytes
        """
        return io.BytesIO(self._reader.read())

    def to_image(self):
        """
        turn InstanceMap object to PIL.Image
        """
        try:
            img = Image.open(self.to_bypes())
        except Exception as e:
            raise FileReadError(f"Failed to convert bytes to an array. {e}") from None
        return img

    def to_array(self):
        """
        turn InstanceMap object to numpy.ndarray
        """
        return bytes_to_numpy(self.to_bypes())

    def visualize(self, image, palette, **kwargs):
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

    def __repr__(self):
        return f"path:{self.location}"

    @property
    def field_key(self):
        return "InstanceMap"
