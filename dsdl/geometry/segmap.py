import numpy as np
from PIL import Image as Image_
from .label import LabelList
from .box import BBox
from .media import Image


class SegmentationMap(Image):
    """
    A Geometry class for semantic segmentation map.
    """

    def __init__(self, value, dom, file_reader):
        super().__init__(value, file_reader)
        if isinstance(dom, list):
            assert len(dom) == 1, "You can only assign one class dom in LabelMapField."
            dom = dom[0]
        self._dom = dom

    @property
    def class_domain(self):
        return self._dom

    def visualize(self, image, palette, **kwargs):
        seg = self.to_array()
        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)
        category_ids = np.unique(seg)
        if self.class_domain.__name__ == "_LabelMapDefaultDomain":
            category_ids = category_ids + 1
        label_lst = []
        for category_id in category_ids:
            if int(category_id) > len(self._dom) or int(category_id) < 1:
                continue
            label = self._dom.get_label(int(category_id))
            category_name = label.category_name
            if category_name not in palette:
                palette[category_name] = tuple(np.random.randint(0, 255, size=[3]))
            label_lst.append(label)
            color_seg[seg == category_id, :] = np.array(palette[category_name])
        overlay = Image_.fromarray(color_seg).convert("RGBA")
        overlayed = Image_.blend(image, overlay, 0.5)
        LabelList(label_lst).visualize(image=overlayed, palette=palette, bbox={"temp": BBox([0, 0, 0, 0])})
        return overlayed
