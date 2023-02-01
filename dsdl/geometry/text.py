"""
DSDL Text Annotation Geometry.
"""
from .base_geometry import BaseGeometry
from PIL import ImageDraw, ImageFont, Image
import numpy as np


class Text(BaseGeometry):
    def __init__(self, text: str):
        """A Geometry class which abstracts a text annotation object.

        Args:
            text: The text annotation.
        """
        self._text = text

    @property
    def value(self) -> str:
        """
        Returns:
            The text of the current text annotation.
        """
        return self._text

    @property
    def text(self) -> str:
        """
        Returns:
            The text of the current text annotation.
        """
        return self._text

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current text annotation on an given image.

        Args:
            image: The image where the text annotation to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current text annotation, such as `BBox` annotation.

        Returns:
            The image where the current text annotation has been drawn on.
        """
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
            coords = np.array([[0, image.size[1] - 1.2 * label_size[1]]])
        for coord in coords:
            draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*text_color, 255))
            draw_obj.text(tuple(coord), self.value, fill=(255, 255, 255, 255), font=font)
        del draw_obj
        return image

    def __repr__(self) -> str:
        return self._text

    @property
    def field_key(self) -> str:
        """Get the field type.

        Returns:
            "Text"
        """
        return "Text"
