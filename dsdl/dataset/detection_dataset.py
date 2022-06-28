from .base_dataset import BaseDataset
import io
from PIL import Image, ImageFont, ImageDraw
import numpy as np
from prettytable import PrettyTable


class DetectionDataset(BaseDataset):
    # KEY_MAPPING: yaml文件中定义的字段名称和dataset内部字段名称的对应关系，
    # 比如下面的实例表示yaml中sample中的media字段对应了dataset样本中的$media字段
    # yaml中annotation字段对应了dataset样本的中的$annotation字段
    # yaml中的box2d字段对应了dataset样本中的$box2d字段
    # yaml中的category字段对应了dataset样本中的$category字段
    # 该对应字典可由用户自己指定，详见visualize_demo1.py中的内容
    KEY_MAPPING = {
        "$media": "media",
        "$annotation": {
            "$key": "annotation",
            "$box2d": "box2d",
            "$category": "category"
        },
    }

    def parse_struct(self, sample):
        """
        该方法的作用是将根据yaml文件定义的样本Struct对象读取为数据集中可操作的数据结构
        下面的代码就是将
        class ObjectDetectionSample(Struct):
            image = ImageField()
            objects = ListField(ele_type=LocalObjectEntry())
        转换为一个样本（为字典类型）
            {
            $media: PIL.Image object
            $annotation: {
                $box2d: [...]
                $category: [...]
                }
            }
        """
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

    def visualize(self, sample):
        """
        该方法的作用是将parse_struct方法的返回值（单个样本）进行图像可视化
        """
        image = sample["$media"]
        box2d_lst = sample["$annotation"]["$box2d"]
        category_lst = sample["$annotation"]["$category"]

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
        table.field_names = ["sample idx", "media shape", "bbox", "label"]
        table._max_width = {"bbox": 50, "label": 25}
        if not isinstance(sample, list):
            sample = [sample]

        for idx, s in enumerate(sample, start=1):
            row = [idx, np.shape(s["$media"]), s["$annotation"]["$box2d"], s["$annotation"]["$category"]]
            table.add_row(row)

        return table
