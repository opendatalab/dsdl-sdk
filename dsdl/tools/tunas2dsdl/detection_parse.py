import json
import re


class DetectionParse:
    PARAM_NAME = "cdom"
    FIELD_MAPPING = {
        "bbox": "BBox",
        "int": "Int",
        "float": "Num",
        "str": "Str",
        "points": "Polygon",
        "list": "List",
        "media": "Image",
        "bool": "Bool",
        "category": f"Label[dom=${PARAM_NAME}]",
    }

    def __init__(self, data_info_file, ann_file, dataset_name=None):
        self._dataset_name = dataset_name
        self._data_info_file = data_info_file
        self._annotation_file = ann_file
        self._data_info = self._read_json(data_info_file)
        self._annotation_info = self._read_json(ann_file)
        self._meta_info = self._parse_meta_info()
        self._class_domain_info, self._class_raw_info = self._parse_class_domain()
        self._dsdl_version_info = {"$dsdl-version": "0.5.0"}
        self._struct_defs, self._samples = self._parse_ann_info()

    def _parse_meta_info(self):
        meta_info = {k: v for k, v in self._data_info.items() if k not in ("tasks", "statistics")}
        meta_info["sub_dataset_name"] = self._annotation_info["sub_dataset_name"]
        if not self._dataset_name:
            self._dataset_name = meta_info["dataset_name"]
        return meta_info

    def _parse_class_domain(self):
        class_raw_info = {}
        class_domain_info = {"$def": "class_domain", "$name": self.clean(f"{self._dataset_name}ClassDom")}
        classes = []
        for task in self._data_info["tasks"]:
            task_name, task_type, task_source, catalog = task["name"], task["type"], task["source"], task[
                "catalog"]
            task_id = f"{task_name}-{task_type}-{task_source}"
            class_raw_info[task_id] = {_["category_id"]: _["category_name"] for _ in catalog}
            classes.extend(class_raw_info[task_id].values())
        class_domain_info["classes"] = sorted(list(set(classes)))
        return class_domain_info, class_raw_info

    def _parse_ann_info(self):
        samples = self._annotation_info["samples"]
        ann_info = []
        object_struct = {
            "$name": "LocalObjectEntry",
            "$def": "struct",
            "$params": [self.PARAM_NAME],
            "$fields": {
            }
        }
        sample_struct = {
            "$name": "ObjectDetectionSample",
            "$def": "struct",
            "$params": [self.PARAM_NAME],
            "$fields": {
                "media": self.FIELD_MAPPING["media"],
                "annotations": f"List[etype={object_struct['$name']}[{self.PARAM_NAME}=${self.PARAM_NAME}]]"
            }
        }
        data_info = {"sample-type": f"{sample_struct['$name']}[{self.PARAM_NAME}={self._class_domain_info['$name']}]"}
        optional_fields = set()
        annotations_optional_flag = False
        empty_annotations_flag = True
        for sample in samples:
            ground_truth_dict = {}
            sample_item = {"media": sample["media"]["path"]}
            for gt_item in sample.get("ground_truth", []):
                ann_id = gt_item.get("ref_ann_id") or gt_item["ann_id"]
                ground_truth_dict.setdefault(ann_id, {})

                if "bbox" in gt_item:
                    object_struct["$fields"]["bbox"] = self.FIELD_MAPPING["bbox"]
                    ground_truth_dict[ann_id]["bbox"] = gt_item["bbox"]

                if "points" in gt_item:
                    object_struct["$fields"]["points"] = self.FIELD_MAPPING["points"]
                    ground_truth_dict[ann_id]["points"] = gt_item["points"]

                task_id = f"{gt_item['name']}-{gt_item['type']}-{gt_item['source']}"
                _category_name = self._class_raw_info[task_id][gt_item["categories"][0]["category_id"]]
                ground_truth_dict[ann_id]["category"] = self._class_domain_info["classes"].index(_category_name) + 1
                object_struct["$fields"]['category'] = self.FIELD_MAPPING['category']
                ground_truth_dict[ann_id].update(gt_item["attributes"])
                _attribute_field_dict = {k: self.FIELD_MAPPING[v.__class__.__name__] for k, v in
                                         gt_item.get("attributes", {}).items() if
                                         v.__class__.__name__ in self.FIELD_MAPPING}
                object_struct["$fields"].update(_attribute_field_dict)
                optional_fields.update(_attribute_field_dict.keys())
            ground_truths = list(ground_truth_dict.values())
            if ground_truths:
                empty_annotations_flag = False
                sample_item["annotations"] = ground_truths
            else:
                annotations_optional_flag = True
            ann_info.append(sample_item)
        data_info["samples"] = ann_info
        if optional_fields:
            object_struct["$optional"] = list(optional_fields)
        if empty_annotations_flag:
            sample_struct["$fields"].pop("annotations")
            struct_defs = [sample_struct]
        else:
            if annotations_optional_flag:
                sample_struct["$optional"] = ["annotations"]
            struct_defs = [object_struct, sample_struct]
        return struct_defs, data_info

    @staticmethod
    def _read_json(file):
        with open(file, "r") as f:
            json_info = json.load(f)
        return json_info

    @staticmethod
    def clean(varStr):
        return re.sub('\W|^(?=\d)', '', varStr)

    @property
    def struct_defs(self):
        """
        dsdl的struct定义字典组成的列表
        """
        return self._struct_defs

    @property
    def samples(self):
        """
        dsdl的data字段下的内容，为一个字典，有sample-type域samples字段，samples包含了样本列表
        """
        return self._samples

    @property
    def sample_info(self):
        """
        tunas v0.3的annotation的json文件的原始内容
        """
        return self._annotation_info

    @property
    def class_domain_info(self):
        """
        dsdl的class_domain的定义字典
        """
        return self._class_domain_info

    @property
    def meta_info(self):
        """
        dsdl的元信息内容
        """
        return self._meta_info

    @property
    def data_info_file(self):
        """
        返回tunas v0.3 dataset_info.json的文件路径
        """
        return self._data_info_file

    @property
    def annotation_file(self):
        """
        返回tunas v0.3 的标注文件json文件的路径
        """
        return self._annotation_file

    @property
    def dsdl_version(self):
        """
        dsdl的版本信息字典
        """
        return self._dsdl_version_info
