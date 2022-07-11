import numpy as np
from PIL import ImageFont

class Label:

    def __init__(self, category_id, category_name, class_domain):

        self._id = category_id
        self._name = category_name
        self._dom = class_domain

    @property
    def category_name(self):
        return self._name

    @property
    def category_id(self):
        return self._id

    @property
    def class_domain(self):
        return self._dom

    def visualize(self, image, draw_obj, palette, **kwargs):
        if self.category_name not in palette:
            palette[self.category_name] = tuple(np.random.randint(0, 255, size=[3]))
        color = palette[self.category_name]
        font = ImageFont.load_default()
        label_size = draw_obj.textsize(self.category_name, font)
        if "bbox" in kwargs:
            coords = np.array([[item.xyxy[0], item.xyxy[1]+0.2 * label_size[1]] for item in kwargs["bbox"].values()])
        else:
            coords = np.array([[0, 0.2 * label_size[1]]])
        for coord in coords:
            draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=color)
            draw_obj.text(tuple(coord), self.category_name, fill=(255, 255, 255), font=font)
        return draw_obj

    def __repr__(self):
        return self.category_name


