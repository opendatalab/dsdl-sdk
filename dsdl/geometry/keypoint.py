from .label import Label
from .class_domain import ClassDomain
from .base_geometry import BaseGeometry
from typing import List
from ..exception import ClassNotFoundError
from PIL import ImageDraw
import numpy as np


class Coord2D(BaseGeometry):

    def __init__(self, x: float, y: float, visiable: int, label: Label):
        self._x = x
        self._y = y
        self._visiable = visiable
        self._label = label

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def point(self):
        return [self._x, self._y]

    @property
    def value(self):
        return [self._x, self._y, self._visiable]

    @property
    def visiable(self):
        return self._visiable

    @property
    def label(self):
        return self._label

    @property
    def class_domain(self):
        return self._label.class_domain

    @property
    def name(self):
        return self._label.name


class KeyPoints(BaseGeometry):
    def __init__(self, keypoints: List[Coord2D], domain: ClassDomain):
        self._keypoints = keypoints
        self._dom = domain

    @property
    def value(self):
        return [_.value for _ in self._keypoints]

    @property
    def points(self):
        return [_.point for _ in self._keypoints]

    @property
    def visables(self):
        return [_.visiable for _ in self._keypoints]

    @property
    def keypoints(self):
        return self._keypoints

    @property
    def class_domain(self):
        return self._dom

    @property
    def names(self):
        return [_.name for _ in self._keypoints]

    def __getitem__(self, item):
        assert isinstance(item, (str, int)), "The index must be str or int type value."
        if isinstance(item, int):
            return self._keypoints[item]
        elif isinstance(item, str):
            for ind, label_name in enumerate(self._dom.get_label_names()):
                if label_name == item:
                    return self._keypoints[ind]
        raise ClassNotFoundError(f"Category '{item}' not defined in domain {self._dom.__name__}.")

    def visualize(self, image, palette, **kwargs):
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

    @property
    def field_key(self):
        return "Keypoint"
