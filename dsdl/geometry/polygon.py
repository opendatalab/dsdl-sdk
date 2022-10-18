from typing import List
import numpy as np
from PIL import ImageDraw, Image
from .base_geometry import BaseGeometry


class PolygonItem(BaseGeometry):

    def __init__(
            self,
            points: List[List[float]]
    ):
        self._data = points

    @property
    def points(self) -> List[List[float]]:
        return self._data

    @property
    def points_x(self) -> List[float]:
        return [_[0] for _ in self._data]

    @property
    def points_y(self) -> List[float]:
        return [_[1] for _ in self._data]

    @property
    def point_for_draw(self) -> List[int]:
        p = min(self._data, key=lambda x: x[0] + x[1])
        p = [int(_) for _ in p]
        return p

    @property
    def openmmlabformat(self) -> List[float]:
        return self._flatten()

    def to_tuple(self):
        return tuple([(_[0], _[1]) for _ in self._data])

    def _flatten(self) -> List[float]:
        return [_ for point in self._data for _ in point]

    def __repr__(self):
        return str(self._data)


class Polygon(BaseGeometry):

    def __init__(self, polygons: List[PolygonItem]):
        self._data = polygons

    @property
    def polygons(self):
        return self._data

    @property
    def openmmlabformat(self) -> List[List[float]]:
        return [_.openmmlabformat for _ in self._data]

    @property
    def point_for_draw(self) -> [int, int]:
        p = min(self._data, key=lambda x: x.point_for_draw[0] + x.point_for_draw[1])
        p = [int(_) for _ in p.point_for_draw]
        return p

    def visualize(self, image, palette, **kwargs):
        color = (0, 255, 0)
        if "label" in kwargs:
            for label in kwargs["label"].values():
                if label.category_name not in palette:
                    palette[label.category_name] = tuple(np.random.randint(0, 255, size=[3]))

                color = palette[label.category_name]

        poly = Image.new('RGBA', image.size[:2])
        pdraw = ImageDraw.Draw(poly)
        for polygon_item in self.polygons:
            pdraw.polygon(polygon_item.to_tuple(), fill=(*color, 127), outline=(*color, 255))
        image.paste(poly, mask=poly)
        del pdraw
        return image

    def __repr__(self):
        return str(self._data)
