from .base_geometry import BaseGeometry
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw


class RBBox(BaseGeometry):
    def __init__(self, value, mode):
        if mode == "xywhr":
            self._polygon = None
            self._rbbox = value
        else:
            self._polygon = value
            self._rbbox = None

    @staticmethod
    def rbbox2polygon(value):
        x, y, width, height, angle = value
        cosA, sinA = math.cos(angle), math.sin(angle)

        def _rotate(p_):  # clockwise
            x_, y_ = p_
            x_r = (x_ - x) * cosA - (y_ - y) * sinA + x
            y_r = (x_ - x) * sinA + (y_ - y) * cosA + y
            return [x_r, y_r]

        x_l, x_r, y_t, y_b = x - width / 2, x + width / 2, y - height / 2, y + height / 2
        p_lt, p_lb, p_rt, p_rb = [x_l, y_t], [x_l, y_b], [x_r, y_t], [x_r, y_b]

        return [_rotate(p_lt), _rotate(p_lb), _rotate(p_rb), _rotate(p_rt)]

    def point_for_draw(self, mode: str = "lt"):
        assert mode in ("lb", "lt", "rb", "rt")
        if mode == "lt":
            p = min(self.polygon_value, key=lambda x: x[0] + x[1])
        elif mode == "lb":
            p = min(self.polygon_value, key=lambda x: x[0] - x[1])
        elif mode == "rt":
            p = min(self.polygon_value, key=lambda x: -x[0] + x[1])
        else:  # rb
            p = min(self.polygon_value, key=lambda x: -x[0] - x[1])
        p = [int(_) for _ in p]
        return p

    @staticmethod
    def polygon2rbbox(value):
        res = cv2.minAreaRect(np.array(value).astype(np.int32))
        x, y = res[0]
        width, height = res[1]  # width is "first edge"
        angle = res[2]
        if width < height:
            width, height = height, width
            angle = angle + 90
        angle = 1 - angle / 180 * math.pi
        return [x, y, width, height, angle]

    @property
    def polygon_value(self):
        if self._polygon is None:
            self._polygon = self.rbbox2polygon(self._rbbox)
        return self._polygon

    @property
    def rbbox_value(self):
        if self._rbbox is None:
            self._rbbox = self.polygon2rbbox(self._polygon)
        return self._rbbox

    def visualize(self, image, palette, **kwargs):
        color = (0, 255, 0)
        if "label" in kwargs:
            for label in kwargs["label"].values():
                if label.category_name not in palette:
                    palette[label.category_name] = tuple(np.random.randint(0, 255, size=[3]))

                color = palette[label.category_name]

        poly = Image.new('RGBA', image.size[:2])
        pdraw = ImageDraw.Draw(poly)
        pdraw.polygon([tuple(_) for _ in self.polygon_value], fill=(*color, 127), outline=(*color, 255))
        image.paste(poly, mask=poly)
        del pdraw
        return image

    def __repr__(self):
        x, y, w, h, angle = self.rbbox_value
        x, y, w, h, angle = int(x), int(y), int(w), int(h), int(angle / math.pi * 180)
        return f"[{x}, {y}, {w}, {h}, {angle}°]"

    @property
    def field_key(self):
        return "RotatedBBox"
