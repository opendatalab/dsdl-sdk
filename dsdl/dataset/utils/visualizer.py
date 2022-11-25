from typing import Optional, Dict, Tuple, List
import os
from collections import defaultdict

from .parser import Parser
from ...geometry import LabelList, BBox
from copy import deepcopy


class VisualizerUtil:

    @staticmethod
    def extract_field_pipeline(result_dic, sample, field_name):
        info = Parser.flatten_sample(sample, f"${field_name}")
        result_dic[field_name] = info

    @staticmethod
    def whole_pipeline(field_lst, sample):
        result_dic = {}
        for field_name in field_lst:
            VisualizerUtil.extract_field_pipeline(result_dic, sample, field_name)
        return result_dic

    @staticmethod
    def sort_field(field_lst):
        field_lst = list(field_lst)
        # 定义画图时的先后顺序，数值越小的越先画
        field_order = {"text": 40, "bbox": 20, "polygon": 10, "label": 30, "keypoint": 15, "insmap": 5, "labelmap": 0,
                       "others": -1}

        field_lst = sorted(field_lst, key=lambda k: field_order.get(k, -1))
        return field_lst


class ImageVisualizer:
    def __init__(self, image, palette):
        self.image = image
        self.palette = palette
        self.ground_truths = defaultdict(dict)

    def append_ground_truth(self, gt_path, gt_item):
        """
        {
            ./object/1:{
                bbox: {bb1: bbox_obj, bb2: bbox_obj}
                label: [l1: label_obj, l2: label_obj]
                bool: []
            }

            ./object/2: {
                bbox: {}
            }
        }
        """
        gt_dir, gt_name = os.path.split(gt_path)
        field_key = gt_item.__class__.__name__.lower()
        if field_key not in self.ground_truths[gt_dir]:
            self.ground_truths[gt_dir][field_key] = {gt_name: gt_item}
        else:
            self.ground_truths[gt_dir][field_key][gt_name] = gt_item

    def visualize(self):
        image = self.image.to_image()
        image = image.convert("RGBA")
        image_label_lst = []
        for gt_dir, gt_item in self.ground_truths.items():
            field_keys = VisualizerUtil.sort_field(gt_item.keys())
            for field_key in field_keys:
                if field_key == "label":
                    image = LabelList(gt_item[field_key].values()).visualize(image=image,
                                                                             image_label_list=image_label_lst,
                                                                             palette=self.palette, **gt_item)
                else:
                    for ann_item in gt_item[field_key].values():
                        if hasattr(ann_item, "visualize"):
                            image = ann_item.visualize(image=image, palette=self.palette, **gt_item)
        LabelList(image_label_lst).visualize(image=image, palette=self.palette, bbox={"temp": BBox(0, 0, 0, 0)})
        return image

    def format(self):
        result = {"media": self.image, "ann": list(self.ground_truths.values())}
        return result


class ImageVisualizePipeline(VisualizerUtil):
    """
    step 1:

    该类用于处理Dataset中输出的样本，指定field_list后，会先调用方法 self.whole_pipeline，提取各个字段的信息，举例：
    Dataset中的某个sample形如：
        sample = {
        "$image": {"img2": img_obj, "img1":img_obj},
        "$list": {"objects": [{"$image": {"img1": img_obj}, "$bbox": {"box": box_obj}}],
                  "object2": [{"$bbox":{"box": box_obj}}, {"$bbox":{"box": box_obj}}], }
        }
    指定的field_list内容为：[bbox, image]
    则self.whole_pipeline方法会将sample处理为：
    {
        ”image": {
            "./img2": img_obj,
            "./img1": img_obj,
            "./objects/0/img1": img_obj,
        },
        "bbox": {
            "./objects/0/box": box_obj,
            "./object2/0/box": box_obj,
            "./object2/1/box": box_obj
        }
    }

    step2:
    然后会调用self.group_media_and_ann方法，将图像与与之”目录路径“相同的标注进行组合，组合后图像和对应的标注会存储在一个 ImageVisualizer
    对象当中。ImageVisualizer类中还定义了可视化的相关方法，从而可以对每个图像&标注组合进行可视化。方法的返回值是一个字典，字典的键为图像路径，
    值即为ImageVisualizer对象，形如：
    {
        "./img2": ImageVisualizer_obj,
        "./img1": ImageVisualizer_obj,
        "./objects/0/img1": ImageVisualizer_obj,
    }

    step3:
    调用format/visualize方法，从而可以对各个ImageVisualizer对象进行文本/图像可视化。
    """
    PALETTE = {}

    def __init__(self, field_list: List[str], sample, palette: Optional[Dict[str, Tuple]] = None):
        self.field_list = field_list
        self.palette = self.PALETTE
        if palette is not None:  # 如果用户自己定义了label调色盘，则更新默认的调色盘
            self.palette = palette
        if "image" not in field_list:  # 因为是imagevisualizer类，所以field_list中必须包含image字段
            raise ValueError("'image' field not found in the field list to be visualized.")
        self.data_dic = self.whole_pipeline(field_list, sample)
        self.visualize_result = self.group_media_and_ann()

    def group_media_and_ann(self):
        data_dic = deepcopy(self.data_dic)
        image_dic = data_dic.pop("image")
        image_paths = list(image_dic.keys())
        # 将图像按照路径进行从长到短排序
        image_paths = sorted(image_paths, key=lambda x: len(x.split("/")), reverse=True)
        result_dic = {}
        for image_path in image_paths:
            image_dir = os.path.split(image_path)[0]
            image_obj = image_dic[image_path]
            result_dic[image_path] = ImageVisualizer(image_obj, self.palette)
            for ann_dic in data_dic.values():
                pop_keys = []
                for ann_path, ann_obj in ann_dic.items():
                    if ann_path.startswith(image_dir):
                        result_dic[image_path].append_ground_truth(ann_path, ann_dic[ann_path])
                        pop_keys.append(ann_path)
                for pop_key in pop_keys:
                    ann_dic.pop(pop_key)
        return result_dic

    def visualize(self):
        vis_result = {}
        for image_path, image_vis_item in self.visualize_result.items():
            vis_result[image_path] = image_vis_item.visualize()
        return vis_result

    def format(self):
        format_result = []
        for image_vis_item in self.visualize_result.values():
            format_result.append(image_vis_item.format())
        return format_result
