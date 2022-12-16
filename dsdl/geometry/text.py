from .base_geometry import BaseGeometry
from PIL import ImageDraw, ImageFont
import numpy as np


class Text(BaseGeometry):
    def __init__(self, text):
        self._text = text

    @property
    def value(self):
        return self._text

    @property
    def text(self):
        return self._text

    def visualize(self, image, palette, **kwargs):
        draw_obj = ImageDraw.Draw(image)
        text_color = (0, 255, 0)  # green
        font = ImageFont.load_default()
        label_size = draw_obj.textsize(self.value, font)
        if "bbox" in kwargs:
            coords = np.array([[item.xyxy[0], item.xyxy[3] - 1.2 * label_size[1]] for item in kwargs["bbox"].values()])
        elif "polygon" in kwargs:
            coords = np.array(
                [[item.point_for_draw("lb")[0], item.point_for_draw("lb")[1] - 1.2 * label_size[1]] for item in
                 kwargs["polygon"].values()])
        elif "rotatedbbox" in kwargs:
            coords = np.array(
                [[item.point_for_draw("lb")[0], item.point_for_draw("lb")[1] - 1.2 * label_size[1]] for item in
                 kwargs["rotatedbbox"].values()])
        else:
            coords = np.array([[0, image.size[0] - 1.2 * label_size[1]]])
        for coord in coords:
            draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*text_color, 255))
            draw_obj.text(tuple(coord), self.value, fill=(255, 255, 255, 255), font=font)
        del draw_obj
        return image

    def __repr__(self):
        return self._text

    @property
    def field_key(self):
        return "Text"
