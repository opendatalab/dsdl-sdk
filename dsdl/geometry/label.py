import os
import numpy as np
from PIL import ImageFont, ImageDraw
from .registry import CLASSDOMAIN
from .base_geometry import BaseGeometry, FontMixin


class Label(BaseGeometry, FontMixin):

    def __init__(self, name, supercategories=(), domain_name=None):
        """A Geometry class which abstracts a label object.

        Args:
            name: The name of the current label object.
            supercategories: The collection of the current label's super category objects.
            domain_name: The name of the class domain which the current label object belongs to.
        """
        self._name = name
        self._supercategories = [_ for _ in supercategories if isinstance(_, Label)]
        self._domain_name = domain_name

    @property
    def supercategories(self):
        """
        Returns:
            The collection of the current label's super category objects.
        """
        return self._supercategories

    @property
    def supercategories_names(self):
        """
        Returns:
            The names of the current label's supercategories.
        """
        return [_.name for _ in self._supercategories]

    @property
    def parent_names(self):
        """
        Returns:
            The names of the current label's supercategories.
        """
        return [_.name for _ in self._supercategories]

    @property
    def domain_name(self):
        """
        Returns:
            The name of the class domain which the current label object belongs to.
        """
        return self._domain_name

    @property
    def parents(self):
        """
        Returns:
            The collection of the current label's super category objects.
        """
        return self._supercategories

    @property
    def name(self):
        """
        Returns:
            The name of the current label object.
        """
        return self._name

    @property
    def registry_name(self):
        """
        Returns:
            The registry name of the current label object which is unique in the `LABEL` registry.
        """
        return f"{self._domain_name}__{self._name}"

    def set_domain(self, domain_name):
        """
        Set the `_domain_name` of the current label object.
        """
        if self._domain_name is None:
            self._domain_name = domain_name

    @property
    def category_name(self):
        """
        Returns:
            The name of the current label object.
        """
        return self._name

    @property
    def leaf_node_name(self):
        return self._name.split(".")[-1]
    
    @property
    def openmmlabformat(self):
        """
        Returns:
            The name of the current label object.
        """
        return self._name

    @property
    def class_domain(self):
        """
        Returns:
            (dsdl.geometry.ClassDomain): The class domain object which the current label object belongs to.
        """
        return CLASSDOMAIN.get(self.domain_name)

    def index_in_domain(self):
        """
        Returns:
            The index of the current label object in the class domain which it belongs to.
        """
        return self.class_domain.get_cat2ind_mapping()[self.category_name]

    def __eq__(self, other):
        """Compare whether the current label object is equal to the other.

        Args:
            other: Another Label object to be compared with the current one.

        Returns:
            Whether the current label object is equal to the other.
        """
        if self.domain_name != other.domain_name:
            return False
        if self.name != other.name:
            return False
        if len(self.parents) != len(self.parents):
            return False
        for p1 in self.parents:
            for p2 in other.parents:
                if p1 != p2:
                    return False
        return True

    def visualize(self, image, palette, **kwargs):
        """Draw the current label object on an given image.

        Args:
            image: The image where the label to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current label object, such as `BBox` annotation.

        Returns:
            The image where the current label object has been drawn on.
        """
        draw_obj = ImageDraw.Draw(image)
        if self.category_name not in palette:
            palette[self.category_name] = tuple(np.random.randint(0, 255, size=[3]))
        color = palette[self.category_name]
        if self.font is None:
            self.set_font(ImageFont.truetype(os.path.join(os.path.dirname(__file__), "source", "Arial_Font.ttf")))
        label_size = draw_obj.textsize(self.category_name, self.font)
        if "bbox" in kwargs:
            coords = np.array([[item.xyxy[0], item.xyxy[1] + 0.2 * label_size[1]] for item in kwargs["bbox"].values()])
        elif "polygon" in kwargs:
            coords = np.array([[item.point_for_draw()[0], item.point_for_draw()[1] + 0.2 * label_size[1]] for item in
                               kwargs["polygon"].values()])
        else:
            coords = np.array([[0, 0.2 * label_size[1]]])
        for coord in coords:
            draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*color, 255))
            draw_obj.text(tuple(coord), self.category_name, fill=(255, 255, 255, 255), font=self.font)
        del draw_obj
        return image

    def __repr__(self):
        return self.category_name


class LabelList(BaseGeometry, FontMixin):

    def __init__(self, label_list):
        """A Geometry class which abstracts a list of label objects.

        Args:
            label_list: A collection of `Label` objects.
        """
        self._label_list = list(label_list)

    @property
    def names(self):
        """
        Returns:
            All the names of the label object in the current `LabelList` object.
        """
        return [label.category_name for label in self._label_list]

    @property
    def category_names(self):
        """
        Returns:
            All the names of the label object in the current `LabelList` object.
        """
        return [label.category_name for label in self._label_list]

    @property
    def label_list(self):
        """
        Returns:
            All the `Label` objects in the current `LabelList` object.
        """
        return self._label_list

    @property
    def class_domains(self):
        """
        Returns:
            (List[dsdl.geometry.ClassDomain]): The class domain objects of all the `Label` objects in the current `LabelList` object.
        """
        return [label.class_domain for label in self._label_list]

    def visualize(self, image, palette, **kwargs):
        """Draw the current `LabelList` object on an given image.

        Args:
            image: The image where the labels to be drawn.
            palette: The palette which stores the color of different category name.
            **kwargs: Other annotations which may be used when drawing the current `LabelList` object, such as `BBox` annotation.

        Returns:
            The image where the current `LabelList` object has been drawn on.
        """
        draw_obj = ImageDraw.Draw(image)
        if self.font is None:
            self.set_font(ImageFont.truetype(os.path.join(os.path.dirname(__file__), "source", "Arial_Font.ttf")))
        y_offset = np.zeros((1, 2))
        for label_obj in self.label_list:

            category_name = label_obj.category_name

            if category_name not in palette:
                palette[category_name] = tuple(np.random.randint(0, 255, size=[3]))
            color = palette[category_name]

            label_size = draw_obj.textsize(category_name, self.font)
            if "bbox" in kwargs:
                # coords.shape = [num_box, 2]
                coords = y_offset + np.array(
                    [[item.xyxy[0], item.xyxy[1] + 0.2 * label_size[1]] for item in kwargs["bbox"].values()])
            elif "polygon" in kwargs:
                coords = y_offset + np.array(
                    [[item.point_for_draw()[0], item.point_for_draw()[1] + 0.2 * label_size[1]] for item in
                     kwargs["polygon"].values()])
            elif "rotatedbbox" in kwargs:
                coords = y_offset + np.array(
                    [[item.point_for_draw()[0], item.point_for_draw()[1] + 0.2 * label_size[1]] for item in
                     kwargs["rotatedbbox"].values()])
            elif "image_label_list" not in kwargs:
                coords = y_offset + np.array([[0, 0.2 * label_size[1]]])
            else:
                coords = []
                kwargs["image_label_list"].append(label_obj)

            y_offset += np.array([[0., 1.2 * label_size[1]]])
            for coord in coords:
                draw_obj.rectangle([tuple(coord), tuple(coord + label_size)], fill=(*color, 255))
                draw_obj.text(tuple(coord), category_name, fill=(255, 255, 255, 255), font=self.font)

        del draw_obj
        return image
