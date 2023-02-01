"""
The Base Class of all the Geometry class in DSDL.
"""
from PIL import Image


class BaseGeometry:

    def visualize(self, image: Image, palette: dict, **kwargs) -> Image:
        """Draw the current geometry object on an given image.

        Args:
            image: The image where the geometry object to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current geometry object.

        Returns:
            The image where the current geometry object has been drawn on.
        """
        return image

    def __repr__(self):
        return self.__class__.__name__ + " object"

    @property
    def field_key(self):
        """Get the field type.

        Returns:
            The field type name of the current geometry object.
        """
        return self.__class__.__name__
