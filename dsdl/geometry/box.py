from typing import TypeVar, List
import numpy as np
from PIL import ImageDraw
from .base_geometry import BaseGeometry

_ELE_TYPE = TypeVar("_ELE_TYPE", int, float)


class BBox(BaseGeometry):

    def __init__(self, data: List[_ELE_TYPE], mode):
        """A Geometry class which abstracts a 2D bounding box object.

        Args:
            x: The bounding box's top left point horizontal axis.
            y: The bounding box's top left point vertical axis.
            width: The bounding box's width.
            height: The bounding box's height.

        Attributes:
            _data(list[float]): A list which contains the bounding box's top left point horizontal axis, top left point vertical axis, width and height.
        """
        assert mode in ("xyxy", "xywh")
        if mode == "xyxy":
            data = [data[0], data[1], data[2] - data[0], data[3] - data[1]]
        self._data = data

    @property
    def x(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's top left point horizontal axis.
        """
        return self._data[0]

    @property
    def y(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's top left point vertical axis.
        """
        return self._data[1]

    @property
    def width(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's width.
        """
        return self._data[2]

    @property
    def height(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's height.
        """
        return self._data[3]

    @property
    def xmin(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's top left point horizontal axis.
        """
        return self._data[0]

    @property
    def ymin(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's top left point vertical axis.
        """
        return self._data[1]

    @property
    def xmax(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's bottom right point horizontal axis.
        """
        return self._data[0] + self._data[2]

    @property
    def ymax(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's bottom right point vertical axis.
        """
        return self._data[1] + self._data[3]

    @property
    def area(self) -> _ELE_TYPE:
        """
        Returns:
            The bounding box's area.
        """
        return self.width * self.height

    @property
    def xyxy(self) -> List[_ELE_TYPE]:
        """
        Returns:
            The bounding box's [xmin ymin xmax ymax] format.
        """
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @property
    def xywh(self) -> List[_ELE_TYPE]:
        """
        Returns:
            The bounding box's [x y w h] format.
        """
        return [self.xmin, self.ymin, self.width, self.height]

    @property
    def openmmlabformat(self) -> List[_ELE_TYPE]:
        """
        Returns:
            The bounding box's [xmin ymin xmax ymax] format, which is used in openmmlab project.
        """
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    def to_int(self):
        """Convert the value in `self._data` to `int` type.
        """
        self._data = [int(_) for _ in self._data]

    def to_float(self):
        """Convert the value in `self._data` to `float` type.
        """
        self._data = [float(_) for _ in self._data]

    def visualize(self, image, palette, **kwargs):
        """Draw the current bounding box on an given image.

        Args:
            image: The image where the bounding box to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current bounding box, such as `Label` annotation.

        Returns:
            The image where the current bounding box has been drawn on.
        """
        draw_obj = ImageDraw.Draw(image)
        color = (0, 255, 0)
        if "label" in kwargs:
            for label in kwargs["label"].values():
                if label.category_name not in palette:
                    palette[label.category_name] = tuple(np.random.randint(0, 255, size=[3]))

                color = palette[label.category_name]
        draw_obj.rectangle(self.xyxy, outline=(*color, 255), width=2)
        del draw_obj
        return image

    def __repr__(self):
        return str(self.xyxy)
