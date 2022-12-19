from typing import Optional, Dict, Tuple, List
import os
from collections import defaultdict
from .commons import Util
from ...geometry import LabelList, BBox
from ...types import Struct
from copy import deepcopy


class ImageSample:
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
        if hasattr(gt_item, "field_key"):
            field_key = gt_item.field_key.lower()
        else:
            field_key = gt_item.__class__.__name__.lower()
        if field_key not in self.ground_truths[gt_dir]:
            self.ground_truths[gt_dir][field_key] = {gt_name: gt_item}
        else:
            self.ground_truths[gt_dir][field_key][gt_name] = gt_item

    def visualize(self):
        image = self.image.to_image()
        image = image.convert("RGBA")
        image_label_lst = []  # store labels having no matched polygon or bbox, etc.
        for gt_dir, gt_item in self.ground_truths.items():
            field_keys = Util.sort_field(gt_item.keys())
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


class ImageVisualizePipeline:
    """
    step 1:

    该类用于处理Dataset中输出的样本，指定field_list后，会先调用方法 self.whole_pipeline，提取各个字段的信息，举例：
    Dataset中的某个sample形如：
        sample = {
        "$image": {"img2": img_obj, "img1":img_obj},
        "$list": {"objects": [{"$image": {"img1": img_obj}, "$bbox": {"box": box_obj}}],
                  "object2": [{"$bbox":{"box": box_obj}}, {"$bbox":{"box": box_obj}}], },
        "$struct": {
                "struct1": {
                    "$image": {"img3": img_obj, "img4": img_obj}
                }
            }
        }
    指定的field_list内容为：[bbox, image]
    则self.whole_pipeline方法会将sample处理为：
    {
        ”image": {
            "./img2": img_obj,
            "./img1": img_obj,
            "./objects/0/img1": img_obj,
            "./struct1/img3": img_obj,
            "./struct1/img4": img_obj,
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
    BU_DIST_WEIGHT = 1
    TD_DIST_WEIGHT = 0.01
    DIST_TRHESH = 2

    def __init__(self, field_list: List[str], sample: Struct, palette: Optional[Dict[str, Tuple]] = None):
        self.field_list = field_list
        self.palette = self.PALETTE
        if palette is not None:  # 如果用户自己定义了label调色盘，则更新默认的调色盘
            self.palette = palette
        if "image" not in field_list:  # 因为是imagevisualizer类，所以field_list中必须包含image字段
            raise ValueError("'image' field not found in the field list to be visualized.")
        self.data_dic = sample.extract_field_info(field_list)
        self.visualize_result = self.group_media_and_ann()

    @classmethod
    def _match(cls, ann_path, image_paths):
        dists = [cls._calculate_distance(ann_path, image_path) for image_path in image_paths]
        min_dist = min(dists)
        res = [image_paths[_] for _ in range(len(image_paths)) if dists[_] == min_dist and dists[_] < cls.DIST_TRHESH]
        return res

    @classmethod
    def _calculate_distance(cls, ann_path, image_path):
        img_dir = os.path.split(image_path)[0]
        bu_distance = 0
        while not ann_path.startswith(img_dir + "/"):
            bu_distance += 1
            img_dir = os.path.split(img_dir)[0]
        td_distance = len(ann_path.replace(img_dir, "").split("/")) - 1
        return cls._metric(bu_distance, td_distance)

    @classmethod
    def _metric(cls, bu_distance, td_distance):
        return bu_distance * cls.BU_DIST_WEIGHT + td_distance * cls.TD_DIST_WEIGHT

    def group_media_and_ann(self):
        data_dic = deepcopy(self.data_dic)
        image_dic = data_dic.pop("image")
        image_paths = list(image_dic.keys())
        result_dic = {k_: ImageSample(image_dic[k_], self.palette) for k_ in image_paths}
        for ann_dic in data_dic.values():
            for ann_path, ann_obj in ann_dic.items():
                matched_img_paths = self._match(ann_path, image_paths)
                for matched_img_path in matched_img_paths:
                    result_dic[matched_img_path].append_ground_truth(ann_path, ann_obj)
        return result_dic

    def visualize(self):
        vis_result = {}
        for image_path, sample_item in self.visualize_result.items():
            vis_result[image_path] = sample_item.visualize()
        return vis_result

    def format(self):
        format_result = []
        for image_vis_item in self.visualize_result.values():
            format_result.append(image_vis_item.format())
        return format_result
