from .base_dataset import BaseDataset
import io
from PIL import Image, ImageFont, ImageDraw
import numpy as np


class DetectionDataset(BaseDataset):
    KEY_MAPPING = {
        "$media": "media",
        "$annotation": {
            "$key": "objects",
            "$box2d": "bbox",
            "$category": "label"
        },
    }

    def parse_struct(self, sample):

        data_info = {}
        ground_truth = {"$box2d": [], "$category": []}
        media_key = self.get_field_name(self.key_mapping["$media"])
        image_struct = getattr(sample, media_key)
        if image_struct is None:
            return None
        image = Image.open(io.BytesIO(image_struct.read()))
        data_info["$media"] = image
        gt_key = self.get_field_name(self.key_mapping["$annotation"])
        gt_struct_list = getattr(sample, gt_key)
        box2d_key = self.get_field_name(self.key_mapping["$annotation"]["$box2d"])
        category_key = self.get_field_name(self.key_mapping["$annotation"]["$category"])
        for gt_struct in gt_struct_list:
            box2d_item = getattr(gt_struct, box2d_key)
            category = getattr(gt_struct, category_key)
            if box2d_item is not None:
                ground_truth["$box2d"].append(box2d_item)
                ground_truth["$category"].append(category)
        data_info["$annotation"] = ground_truth
        return data_info

    @staticmethod
    def visualize(sample):
        image = sample["$media"]
        box2d_lst = sample["$annotation"]["$box2d"]
        category_lst = sample["$annotation"]["$category"]

        font = ImageFont.truetype(size=np.floor(1.5e-2 * np.shape(image)[1] + 10).astype('int32'))

        draw = ImageDraw.Draw(image)

        for (label_, bbox_) in zip(category_lst, box2d_lst):
            bbox_[0], bbox_[1], bbox_[2], bbox_[3] = bbox_[0], bbox_[1], bbox_[0] + bbox_[2], bbox_[1] + bbox_[3]

            bbox_[0] = int(bbox_[0] * image.size[0])
            bbox_[1] = int(bbox_[1] * image.size[1])
            bbox_[2] = int(bbox_[2] * image.size[0])
            bbox_[3] = int(bbox_[3] * image.size[1])

            label_size = draw.textsize(label_, font)

            text_origin = np.array([bbox_[0], bbox_[1] + 0.2 * label_size[1]])

            color_for_draw = tuple(np.random.randint(0, 255, size=[3]))

            draw.rectangle([bbox_[0], bbox_[1], bbox_[2], bbox_[3]], outline=color_for_draw, width=2)
            draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=color_for_draw)
            draw.text(text_origin, str(label_), fill=(255, 255, 255), font=font)

        del draw

        image.show()
