from .label import Label
from .classdomain import ClassDomainMeta
from .base_geometry import BaseGeometry
from dsdl.exception import ClassNotFoundError
from PIL import ImageDraw
import numpy as np
from typing import List, Union


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
    def x(self):
        """
        Returns:
            The horizontal axis of the current `Coord2D` object.
        """
        return self._x

    @property
    def y(self):
        """
        Returns:
            The vertical axis of the current `Coord2D` object.
        """
        return self._y

    @property
    def point(self):
        """
        Returns:
            The horizontal and vertical axises of the current `Coord2D` object.
        """
        return [self._x, self._y]

    @property
    def value(self):
        """
        Returns:
            The value of the current `Coord2D` object.
        """
        return [self._x, self._y, self._visiable]

    @property
    def visiable(self):
        """
        Returns:
            The visiable value of the current `Coord2D` object.
        """
        return self._visiable

    @property
    def label(self):
        """
        Returns:
            The `Label` object of the current `Coord2D` object.
        """
        return self._label

    @property
    def class_domain(self):
        """
        Returns:
            The `ClassDomain` object of the current `Coord2D` object.
        """
        return self._label.class_domain

    @property
    def name(self):
        """
        Returns:
            The name of the current `Coord2D` object's `Label` object.
        """
        return self._label.name


class KeyPoints(BaseGeometry):
    def __init__(self, value, dom: Union[List[ClassDomainMeta], ClassDomainMeta]):
        """A Geometry class which abstracts a 2D keypoints annotation object.

        Args:
            value: The list of `Coord2D` objects comprise the current `KeyPoints` object.
            dom: The class domain object which the current `KeyPoints` object belongs to.
        """
        if isinstance(dom, list):
            assert len(dom) == 1, "You can only assign one class dom in KeypointField."
            dom = dom[0]
        keypoints = []
        for class_ind, p in enumerate(value, start=1):
            label = dom.get_label(class_ind)
            coord2d = Coord2D(x=p[0], y=p[1], visiable=int(p[2]), label=label)
            keypoints.append(coord2d)
        self._keypoints = keypoints
        self._dom = dom

    @property
    def value(self):
        """
        Returns:
            The list of all the `Coord2D` objects' values.
        """
        return [_.value for _ in self._keypoints]

    @property
    def points(self):
        """
        Returns:
            The list of all the `Coord2D` objects' points.
        """
        return [_.point for _ in self._keypoints]

    @property
    def visables(self):
        """
        Returns:
            The list of all the `Coord2D` objects' visiable values.
        """
        return [_.visiable for _ in self._keypoints]

    @property
    def keypoints(self):
        """
        Returns:
            The list of `Coord2D` objects comprise the current `KeyPoints` object.
        """
        return self._keypoints

    @property
    def class_domain(self):
        """
        Returns:
            The class domain object which the current `KeyPoints` object belongs to.
        """
        return self._dom

    @property
    def names(self):
        """
        Returns:
            The names of all the `Coord2D` objects comprising the current `KeyPoints` object.
        """
        return [_.name for _ in self._keypoints]

    def __getitem__(self, item):
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

    def visualize(self, image, palette, **kwargs):
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

    def __repr__(self):
        return str(self.value)
