import numpy as np
from PIL import ImageFont, ImageDraw


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

    def visualize(self, image, palette, **kwargs):
        draw_obj = ImageDraw.Draw(image)
        if self.category_name not in palette:
            palette[self.category_name] = tuple(np.random.randint(0, 255, size=[3]))
        color = palette[self.category_name]
        font = ImageFont.load_default()
        label_size = draw_obj.textsize(self.category_name, font)
        if "bbox" in kwargs:
            coords = np.array([[item.xyxy[0], item.xyxy[1] + 0.2 * label_size[1]] for item in kwargs["bbox"].values()])
        elif "polygon" in kwargs:
            coords = np.array([[item.point_for_draw[0], item.point_for_draw[1] + 0.2 * label_size[1]] for item in
                               kwargs["polygon"].values()])
        else:
            coords = np.array([[0, 0.2 * label_size[1]]])
        for coord in coords:
            draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*color, 255))
            draw_obj.text(tuple(coord), self.category_name, fill=(255, 255, 255, 255), font=font)
        del draw_obj
        return image

    def __repr__(self):
        return self.category_name


class LabelList:

    def __init__(self, label_list):
        self._label_list = list(label_list)

    @property
    def category_names(self):
        return [label.category_name for label in self._label_list]

    @property
    def category_ids(self):
        return [label.category_id for label in self._label_list]

    @property
    def label_list(self):
        return self._label_list

    @property
    def class_domains(self):
        return [label.class_domain for label in self._label_list]

    def visualize(self, image, palette, **kwargs):
        draw_obj = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        y_offset = np.zeros((1, 2))
        for label_obj in self.label_list:

            category_name = label_obj.category_name

            if category_name not in palette:
                palette[category_name] = tuple(np.random.randint(0, 255, size=[3]))
            color = palette[category_name]

            label_size = draw_obj.textsize(category_name, font)
            if "bbox" in kwargs:
                # coords.shape = [num_box, 2]
                coords = y_offset + np.array(
                    [[item.xyxy[0], item.xyxy[1] + 0.2 * label_size[1]] for item in kwargs["bbox"].values()])
            elif "polygon" in kwargs:
                coords = y_offset + np.array(
                    [[item.point_for_draw[0], item.point_for_draw[1] + 0.2 * label_size[1]] for item in
                     kwargs["polygon"].values()])
            elif "image_label_list" not in kwargs:
                coords = y_offset + np.array([[0, 0.2 * label_size[1]]])
            else:
                coords = []
                kwargs["image_label_list"].append(label_obj)

            y_offset += np.array([[0., 1.2 * label_size[1]]])
            for coord in coords:
                draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*color, 255))
                draw_obj.text(tuple(coord), category_name, fill=(255, 255, 255, 255), font=font)

        del draw_obj
        return image
