from PIL import Image as Image_
import numpy as np
import cv2
from .media import Image


class InstanceMap(Image):
    """
    A Geometry class for instance segmentation map
    """

    def visualize(self, image, palette, **kwargs):
        """Draw the current instance map on an given image.

        Args:
            image: The image where the instance map to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current instance map.

        Returns:
            The image where the current instance map has been drawn on.
        """
        ins_map = self.to_array()
        color_map = np.zeros((ins_map.shape[0], ins_map[1], 3), dtype=np.uint8)
        ins_ids = np.unique(ins_map)

        for ins_id in ins_ids:
            if ins_id == 0:
                continue
            contour_color = tuple(np.random.randint(0, 255, size=[3]))
            this_map = (ins_map == ins_id).astype(np.uint8) * 255
            _, contours, _ = cv2.findContours(this_map, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(color_map, contours, -1, contour_color, 2)

        overlay = Image_.fromarray(color_map).convert("RGBA")
        overlayed = Image_.blend(image, overlay, 0.5)
        return overlayed
