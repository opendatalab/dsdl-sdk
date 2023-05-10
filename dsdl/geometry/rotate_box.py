from .base_geometry import BaseGeometry
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw


class RBBox(BaseGeometry):
    def __init__(self, value, mode="xywht", measure="radian"):
        """A Geometry class which abstracts a rotated bounding box object.

        Args:
            value: The value of the current rotated bounding box.
                   When the `mode` is `"xywht"`,
                   the format is [x, y, w, h, t], which are the bounding box's center point horizontal axis,
                   the bounding box's center point vertical axis, the bounding box's width the bounxing box's height,
                   and the bounding box's rotate angle (in radians).
                   Whe the `mode` is `"xyxy"`,
                   the format is `[[x1, y1], [x2, y2], [x3, y3], [x4, y4]]`, which represents the coordinates of the bounding box's four vertices.
            mode: The mode of the given `value`. Only `"xywht"` and `"xyxy"` are permitted.
        """
        assert mode in ("xywht", "xyxy") and measure in ("radian", "degree")
        if mode == "xywht":
            self._polygon = None
            if measure == "degree":
                value = value.copy()
                value[-1] = value[-1] / 180 * math.pi
            self._rbbox = value
        else:
            self._polygon = [value[i:i + 2] for i in (0, 2, 4, 6)]
            self._rbbox = None

    @staticmethod
    def rbbox2polygon(value):
        """Convert the `xywht` mode bounding box into `xyxy` mode.

        Args:
            value: The `xywht` mode bounding box's value.

        Returns:
            The coresponding `xyxy` mode bounding box's value.
        """
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
        """Converted the `xyxy` mode bounding box into `xywht` mode.

        Args:
            value: The `xyxy` mode bounding box's value.

        Returns:
            The coresponding `xywht` mode bounding box's value.
        """
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
        """Get the `xyxy` mode bounding box's value.

        Returns:
            The `xyxy` mode bounding box's value.
        """
        if self._polygon is None:
            self._polygon = self.rbbox2polygon(self._rbbox)
        return self._polygon

    @property
    def rbbox_value(self):
        """Get the `xywht` mode bounding box's value.

        Returns:
            The `xywht` mode bounding box's value.
        """
        if self._rbbox is None:
            self._rbbox = self.polygon2rbbox(self._polygon)
        return self._rbbox

    def visualize(self, image, palette, **kwargs):
        """Draw the current rotated bounding box on an given image.

        Args:
            image: The image where the rotated bounding box to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current bounding box, such as `Label` annotation.

        Returns:
            The image where the current rotated bounding box has been drawn on.
        """
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
