"""
DSDL Semantic Segmentation Map Geometry.
"""
from .base_geometry import BaseGeometry
from .utils import bytes_to_numpy
from ..exception import FileReadError
import numpy as np
from PIL import Image
import io
from .label import LabelList
from .box import BBox
from .class_domain import _LabelMapDefaultDomain
from ..objectio import BaseFileReader
from .class_domain import ClassDomain


class SegmentationMap(BaseGeometry):
    def __init__(self, location: str, file_reader: BaseFileReader, dom: ClassDomain):
        """A Geometry class which abstracts a semantic segmentation map object.

        Args:
            location: The relative path of the current semantic segmentation map image.
            file_reader: The file reader object of the current semantic segmentation map image.
            dom: The current semantic segmentation map's class domain.
        """
        self._loc = location
        self._reader = file_reader
        self._dom = dom
        if self._dom is None:
            self._dom = _LabelMapDefaultDomain

    @property
    def class_domain(self) -> ClassDomain:
        """
        Returns:
            The current semantic segmentation map's class domain.
        """
        return self._dom

    @property
    def location(self) -> str:
        """
        Returns:
            The relative path of the current semantic segmentation map image.
        """
        return self._loc

    def to_bytes(self) -> io.BytesIO:
        """Turn SegmentationMap object to bytes.

        Returns:
            The bytes of the current semantic segmentation map's image.
        """
        return io.BytesIO(self._reader.read())

    def to_image(self) -> Image:
        """Turn SegmentationMap object to a `PIL.Image` object.

        Returns:
            The `PIL.Image` object of the current semantic segmentation map image.
        """
        try:
            img = Image.open(self.to_bytes())
        except Exception as e:
            raise FileReadError(f"Failed to convert bytes to an array. {e}") from None
        return img

    def to_array(self) -> np.array:
        """Turn SegmentationMap object to numpy.ndarray.

        Returns:
            The `np.ndarray` object of the current semantic segmentation map image.
        """
        return bytes_to_numpy(self.to_bytes())

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current semantic segmentation map on an given image.

        Args:
            image: The image where the semantic segmentation map to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current semantic segmentation map.

        Returns:
            The image where the current semantic segmentation map has been drawn on.
        """
        seg = self.to_array()
        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)
        category_ids = np.unique(seg)
        if self.class_domain.__name__ == "_LabelMapDefaultDomain":
            category_ids = category_ids + 1
        label_lst = []
        for category_id in category_ids:
            if int(category_id) > len(self._dom) or int(category_id) < 1:
                continue
            label = self._dom.get_label(int(category_id))
            category_name = label.category_name
            if category_name not in palette:
                palette[category_name] = tuple(np.random.randint(0, 255, size=[3]))
            label_lst.append(label)
            color_seg[seg == category_id, :] = np.array(palette[category_name])
        overlay = Image.fromarray(color_seg).convert("RGBA")
        overlayed = Image.blend(image, overlay, 0.5)
        LabelList(label_lst).visualize(image=overlayed, palette=palette, bbox={"temp": BBox(0, 0, 0, 0)})
        return overlayed

    def __repr__(self):
        return f"path:{self.location}, class domain: {self._dom.__name__}"

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "LabelMap"
        """
        return "LabelMap"
