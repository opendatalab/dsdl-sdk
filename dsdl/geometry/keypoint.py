"""
DSDL KeyPoint2D Geometry.
"""
from .label import Label
from .class_domain import ClassDomain
from .base_geometry import BaseGeometry
from typing import List, Union
from ..exception import ClassNotFoundError
from PIL import ImageDraw, Image
import numpy as np


class Coord2D(BaseGeometry):

    def __init__(self, x: float, y: float, visiable: int, label: Label):
        """A Geometry class which abstracts a 2D coordinate object.

        Args:
            x: The horizontal axis of the current `Coord2D` object.
            y: The vertical axis of the current `Coord2D` object.
            visiable: Whether the current `Coord2D` object is visiable in the image. if visiable <= 0, The current `Coord2D` object is not visiable.
            label: The current `Coord2D` object's Label object.
        """
        self._x = x
        self._y = y
        self._visiable = visiable
        self._label = label

    @property
    def x(self) -> float:
        """
        Returns:
            The horizontal axis of the current `Coord2D` object.
        """
        return self._x

    @property
    def y(self) -> float:
        """
        Returns:
            The vertical axis of the current `Coord2D` object.
        """
        return self._y

    @property
    def point(self) -> List[float]:
        """
        Returns:
            The horizontal and vertical axises of the current `Coord2D` object.
        """
        return [self._x, self._y]

    @property
    def value(self) -> List[float, float, int]:
        """
        Returns:
            The value of the current `Coord2D` object.
        """
        return [self._x, self._y, self._visiable]

    @property
    def visiable(self) -> int:
        """
        Returns:
            The visiable value of the current `Coord2D` object.
        """
        return self._visiable

    @property
    def label(self) -> Label:
        """
        Returns:
            The `Label` object of the current `Coord2D` object.
        """
        return self._label

    @property
    def class_domain(self) -> ClassDomain:
        """
        Returns:
            The `ClassDomain` object of the current `Coord2D` object.
        """
        return self._label.class_domain

    @property
    def name(self) -> str:
        """
        Returns:
            The name of the current `Coord2D` object's `Label` object.
        """
        return self._label.name


class KeyPoints(BaseGeometry):
    def __init__(self, keypoints: List[Coord2D], domain: ClassDomain):
        """A Geometry class which abstracts a 2D keypoints annotation object.

        Args:
            keypoints: The list of `Coord2D` objects comprise the current `KeyPoints` object.
            domain: The class domain object which the current `KeyPoints` object belongs to.
        """
        self._keypoints = keypoints
        self._dom = domain

    @property
    def value(self) -> List[List[float, float, int]]:
        """
        Returns:
            The list of all the `Coord2D` objects' values.
        """
        return [_.value for _ in self._keypoints]

    @property
    def points(self) -> List[List[float, float]]:
        """
        Returns:
            The list of all the `Coord2D` objects' points.
        """
        return [_.point for _ in self._keypoints]

    @property
    def visables(self) -> List[List[int]]:
        """
        Returns:
            The list of all the `Coord2D` objects' visiable values.
        """
        return [_.visiable for _ in self._keypoints]

    @property
    def keypoints(self) -> List[Coord2D]:
        """
        Returns:
            The list of `Coord2D` objects comprise the current `KeyPoints` object.
        """
        return self._keypoints

    @property
    def class_domain(self) -> ClassDomain:
        """
        Returns:
            The class domain object which the current `KeyPoints` object belongs to.
        """
        return self._dom

    @property
    def names(self) -> List[str]:
        """
        Returns:
            The names of all the `Coord2D` objects comprising the current `KeyPoints` object.
        """
        return [_.name for _ in self._keypoints]

    def __getitem__(self, item: Union[str, int]) -> Coord2D:
        """Given the index or the category name, return the coresponding `Coord2D` object.
        Args:
            item: The index or the category name of one of all the `Coord2D` object.

        Returns:
            The coresponding `Coord2D` object.
        """
        assert isinstance(item, (str, int)), "The index must be str or int type value."
        if isinstance(item, int):
            return self._keypoints[item]
        elif isinstance(item, str):
            for ind, label_name in enumerate(self._dom.get_label_names()):
                if label_name == item:
                    return self._keypoints[ind]
        raise ClassNotFoundError(f"Category '{item}' not defined in domain {self._dom.__name__}.")

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current `Keypoints` object on an given image.

        Args:
            image: The image where the current `Keypoints` object to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current `Keypoints` object.

        Returns:
            The image where the current `Keypoints` object has been drawn on.
        """
        draw_obj = ImageDraw.Draw(image)
        line_color = (0, 255, 0)  # green
        point_radius = 3
        skeleton = self._dom.get_attribute("Skeleton")
        if skeleton is not None:
            point_pairs = skeleton.get_point_pairs(self)
            for point_pair in point_pairs:
                p1, p2 = point_pair[:2]
                if p1.visiable > 0 and p2.visiable:
                    draw_obj.line([*p1.point, *p2.point], width=2, fill=(*line_color, 255))
        for point in self._keypoints:
            if point.visiable > 0:
                label_ = point.label.category_name
                if label_ not in palette:
                    palette[label_] = tuple(np.random.randint(0, 255, size=[3]))
                point_color = palette[label_]
                x, y = point.point
                draw_obj.ellipse((x - point_radius, y - point_radius, x + point_radius, y + point_radius),
                                 fill=(*point_color, 255))
        del draw_obj
        return image

    def __repr__(self) -> str:
        return str(self.value)

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "Keypoint"
        """
        return "Keypoint"
