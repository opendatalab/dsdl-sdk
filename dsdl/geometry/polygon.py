"""
DSDL Polygon Geometry.
"""
from typing import List, Tuple
import numpy as np
from PIL import ImageDraw, Image
from .base_geometry import BaseGeometry


class PolygonItem(BaseGeometry):

    def __init__(
            self,
            points: List[List[float]]
    ):
        """A Geometry class which abstracts a single polygon item object (which means there is only one closed shape).

        Args:
            points: The coordinates of a polygon object, whose format is `[[x1, y1], [x2, y2], ...]`

        Attributes:
            _data(list[list[float]]): The coordinates of a polygon object, whose format is `[[x1, y1], [x2, y2], ...]`
        """
        self._data = points

    @property
    def points(self) -> List[List[float]]:
        """
        Returns:
            The coordinates of the current polygon item. The format is `[[x1, y1], [x2, y2], ...]`.
        """
        return self._data

    @property
    def points_x(self) -> List[float]:
        """
        Returns:
            The horizontal axis of all the points which the current polygon item consists of. The format is [x1, x2, x3, ...].
        """
        return [_[0] for _ in self._data]

    @property
    def points_y(self) -> List[float]:
        """
        Returns:
            The vertical axis of all the points which the current polygon item consists of. The format is [y1, y2, y3, ...].
        """
        return [_[1] for _ in self._data]

    def point_for_draw(self, mode: str = "lt"):
        """
        Get the point's coordinate where a legend is fit to draw.
        Args:
            mode: The position model. Only "lb", "lt", "rb", "rt" are permitted, which mean get the coordinate of left bottom,
                left top, right bottom and right top corresponding.

        Returns:
            The coordinate corresponding to the `mode`, whose format is [x, y].
        """
        assert mode in ("lb", "lt", "rb", "rt")
        if mode == "lt":
            p = min(self._data, key=lambda x: x[0] + x[1])
        elif mode == "lb":
            p = min(self._data, key=lambda x: x[0] - x[1])
        elif mode == "rt":
            p = min(self._data, key=lambda x: -x[0] + x[1])
        else:  # rb
            p = min(self._data, key=lambda x: -x[0] - x[1])
        p = [int(_) for _ in p]
        return p

    @property
    def openmmlabformat(self) -> List[float]:
        """
        Returns:
            All the points of the format [x1, y1, x2, y2, ...].
        """
        return self._flatten()

    def to_tuple(self) -> Tuple[Tuple[float]]:
        """
        Returns:
            The coordinates of the current polygon item. The format is `((x1, y1), (x2, y2), ...)`.
        """
        return tuple([(_[0], _[1]) for _ in self._data])

    def _flatten(self) -> List[float]:
        return [_ for point in self._data for _ in point]

    def __repr__(self) -> str:
        return str(self._data)


class Polygon(BaseGeometry):

    def __init__(self, polygons: List[PolygonItem]):
        """A Geometry class which abstracts a polygon object (which meas there may be multi closed shapes).

        Args:
            polygons: A list of a number of PolygonItem objects.
        """
        self._data = polygons

    @property
    def polygons(self):
        """
        Returns:
            A list of all the PolygonItem objects in the current polygon object.
        """
        return self._data

    @property
    def openmmlabformat(self) -> List[List[float]]:
        """
        Returns:
            All the points of all the polygon item. The format is `[[x1, y1, x2, y2, ...], [x1, y1, x2, y2, ...], ...]`.
        """
        return [_.openmmlabformat for _ in self._data]

    def point_for_draw(self, mode: str = "lt") -> [int, int]:
        """
        Get the point's coordinate where a legend is fit to draw.
        Args:
            mode: The position model. Only "lb", "lt", "rb", "rt" are permitted, which mean get the coordinate of left bottom,
                left top, right bottom and right top corresponding.

        Returns:
            The coordinate correspond to the `mode`. The format is [x, y].
        """
        assert mode in ("lb", "lt", "rb", "rt")
        if mode == "lt":
            p = min(self._data, key=lambda x: x.point_for_draw(mode)[0] + x.point_for_draw(mode)[1])
        elif mode == "lb":
            p = min(self._data, key=lambda x: x.point_for_draw(mode)[0] - x.point_for_draw(mode)[1])
        elif mode == "rt":
            p = min(self._data, key=lambda x: -x.point_for_draw(mode)[0] + x.point_for_draw(mode)[1])
        else:  # rb
            p = min(self._data, key=lambda x: -x.point_for_draw(mode)[0] - x.point_for_draw(mode)[1])
        p = [int(_) for _ in p.point_for_draw(mode)]
        return p

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current polygon object on an given image.

        Args:
            image: The image where the polygon to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current polygon object, such as `Label` annotation.

        Returns:
            The image where the current polygon object has been drawn on.
        """
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

    def __repr__(self) -> str:
        return str(self._data)

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "Polygon"
        """
        return "Polygon"


class RLEPolygon(BaseGeometry):
    def __init__(self, rle_data, image_shape):
        """
        rle_data: rle list
        image_shape: [H, W]
        """
        self._rle_data = rle_data
        self._image_shape = image_shape

    @property
    def rle_data(self):
        return self._rle_data

    @property
    def image_shape(self):
        return self._image_shape

    @property
    def mask(self):
        '''
        # ref: https://www.kaggle.com/paulorzp/run-length-encode-and-decode
        mask_rle: run-length as string formated (start length)
        shape: (height,width) of array to return
        Returns numpy array, 1 - mask, 0 - background
        '''
        s = self._rle_data
        shape = self._image_shape
        starts, lengths = [np.asarray(x, dtype=int) for x in (s[0:][::2], s[1:][::2])]
        starts -= 1
        ends = starts + lengths
        img = np.zeros(shape[0] * shape[1], dtype=np.uint8)
        for lo, hi in zip(starts, ends):
            img[lo:hi] = 1
        return img.reshape(shape)

    @property
    def openmmlabformat(self):
        return {"counts": self.rle_data, "size": self.image_shape}

    def point_for_draw(self, mode: str = "lt") -> [int, int]:
        pass

    def visualize(self, image, palette, **kwargs):
        color = (0, 255, 0)
        mask = self.mask
        color_seg = np.array((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)

        if "label" in kwargs:
            for label in kwargs["label"].values():
                if label.category_name not in palette:
                    palette[label.category_name] = tuple(np.random.randint(0, 255, size=[3]))

                color = palette[label.category_name]
        color_seg[mask == 1, :] = np.array(color)
        overlay = Image.fromarray(color_seg).convert("RGBA")
        overlayed = Image.blend(image, overlay, 0.5)
        return overlayed
