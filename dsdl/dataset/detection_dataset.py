from .base_dataset import BaseDataset
import io
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from prettytable import PrettyTable


class DetectionDataset(BaseDataset):
    """
    {
        image: {image: reader_obj},
        list: {objects: [{bbox: {bbox: xxx}, label: {label: xxx}, extra: {}}]}
        extra: {}
    }
    """

    def process_sample(self, sample):

        data_info = {"image extra": sample.get("extra", {})}

        if "image" not in sample:
            return None
        image_reader = self._get_first_value(sample["image"])
        image = Image.open(io.BytesIO(image_reader.read()))
        data_info["image"] = image

        annotations = {"bbox": [], "label": [], "anno extra": []}
        data_info["annotation"] = annotations

        if "list" not in sample:
            return data_info

        obj_lst = self._get_first_value(sample["list"])
        for obj in obj_lst:
            annotations["anno extra"].append(obj.get("extra", {}))
            annotations["bbox"].append(self._get_first_value(obj.get("bbox", {})))
            annotations["label"].append(self._get_first_value(obj.get("label", {})))

        return data_info

    def visualize(self, sample):
        """
        该方法的作用是将parse_struct方法的返回值（单个样本）进行图像可视化
        """
        image = sample["image"]
        box2d_lst = sample["annotation"]["bbox"]
        category_lst = sample["annotation"]["label"]

        # font = ImageFont.truetype(size=np.floor(1.5e-2 * np.shape(image)[1] + 10).astype('int32'))
        font = ImageFont.load_default()

        draw = ImageDraw.Draw(image)

        for (label_, bbox_) in zip(category_lst, box2d_lst):
            bbox_[0], bbox_[1], bbox_[2], bbox_[3] = bbox_[0], bbox_[1], bbox_[0] + bbox_[2], bbox_[1] + bbox_[3]

            bbox_[0] = int(bbox_[0])
            bbox_[1] = int(bbox_[1])
            bbox_[2] = int(bbox_[2])
            bbox_[3] = int(bbox_[3])

            label_size = draw.textsize(label_, font)

            text_origin = np.array([bbox_[0], bbox_[1] + 0.2 * label_size[1]])

            if label_ in self.palette:
                color_for_draw = self.palette[label_]
            else:
                color_for_draw = tuple(np.random.randint(0, 255, size=[3]))
                self.palette[label_] = color_for_draw

            draw.rectangle([bbox_[0], bbox_[1], bbox_[2], bbox_[3]], outline=color_for_draw, width=2)
            draw.rectangle([tuple(text_origin), tuple(text_origin + label_size)], fill=color_for_draw)
            draw.text(tuple(text_origin), str(label_), fill=(255, 255, 255), font=font)

        del draw

        return image

    @staticmethod
    def format_sample(sample):
        """
        该方法的作用就是将parse_struct方法的返回值（单个样本）写到一个列表中，方便在命令行中展示样本的基本信息
        """
        table = PrettyTable()
        table.title = "Samples"
        table.field_names = ["sample idx", "media shape", "annotation"]
        table._max_width = {"annotation": 50}
        if not isinstance(sample, list):
            sample = [sample]

        for idx, s in enumerate(sample, start=1):
            row = [idx, np.shape(s["image"]), list(zip(s["annotation"]["bbox"], s["annotation"]["label"],
                   s["annotation"]["anno extra"]))]
            table.add_row(row)

        return table
