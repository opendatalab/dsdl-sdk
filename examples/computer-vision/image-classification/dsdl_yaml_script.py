# -*-coding:utf-8-*-
import os.path
import sys
import json
import argparse
import re

# from pydantic import BaseModel
# from typing import Optional, List, Dict


TAB_SPACE = "    "


def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert v0.3 format to dsdl yaml file."
    )
    parser.add_argument(
        "-s" "--src_dir",
        dest="src_dir",
        help="source file path: eg./Users/jiangyiying/sherry/tunas_data_demo/MNIST-tunas",
        required=True,
        type=str,
    )
    parser.add_argument(
        "-o" "--out_dir",
        dest="out_dir",
        default=None,
        help="out file path: eg./Users/jiangyiying/sherry/tunas_data_demo/MNIST-dsdl",
        type=str,
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(-1)

    args = parser.parse_args()
    return args


class ConvertV3toDsdlYaml:
    def __init__(self, dataset_path, output_path=None):
        self.dataset_name = None
        self.struct_sample_name = None
        self.dataset_path = dataset_path
        self.output_path = output_path
        self.dataset_info = dict()
        # 用来定义数据模型，就是.yaml的模型部分
        # {"name": struct_name: XXClassDom, "$def": struct_def, "classes": dict_id_class, "param": param, "label": label}
        self.sample_struct = dict()
        self.sample = dict()
        self.sub_dataset_name = None
        self.sample_type = None  # data里面的sample_type

    @staticmethod
    def camel_case(s):
        s = s.replace("-", " ")
        s = re.sub(r"(_|- )+", " ", s).title().replace(" ", "")
        return s

    def get_dataset_info(self):
        file_name = os.path.join(self.dataset_path, "dataset_info.json")
        with open(file_name) as fp:
            dataset_info = json.load(fp)
        self.dataset_name = dataset_info["dataset_name"]
        self.struct_sample_name = self.camel_case(self.dataset_name) + "Sample"
        for task in dataset_info["tasks"]:
            if task["type"] == "classification":
                dict_id_class = {}
                struct_name = self.camel_case(task["name"]) + "ClassDom"
                struct_def = "class_domain"
                for c in task["catalog"]:
                    dict_id_class[c["category_id"]] = str(c["category_name"])
                self.sample_struct[task["name"]] = {
                    "name": struct_name,
                    "$def": struct_def,
                    "classes": dict_id_class,
                }
            else:
                continue

    def get_sample_data(self, file_name):
        with open(file_name) as fp:
            dataset = json.load(fp)
        self.sub_dataset_name = dataset["sub_dataset_name"]
        self.samples = dataset["samples"]

    def write_class_yaml(self, out_file):
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("\n")
            for struct in self.sample_struct.values():
                fp.writelines(f"{struct['name']}:\n")
                fp.writelines(f"{TAB_SPACE}$def: class_domain\n")
                fp.writelines(f"{TAB_SPACE}classes:\n")
                for class_name in struct["classes"].values():
                    try:
                        int(class_name)
                        fp.writelines(
                            f"{TAB_SPACE * 2}- {self.dataset_name}_{class_name}\n"
                        )
                    except ValueError:
                        fp.writelines(f"{TAB_SPACE*2}- {class_name}\n")

    def write_struct_yaml(self, out_file):
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("\n")
            fp.writelines(f"{self.struct_sample_name}:\n")
            fp.writelines(f"{TAB_SPACE}$def: struct\n")
            if len(self.sample_struct) == 1:
                fp.writelines(f"{TAB_SPACE}$params: ['cdom']\n")
                fp.writelines(f"{TAB_SPACE}$fields: \n")
                fp.writelines(f"{TAB_SPACE * 2}image: Image\n")
                fp.writelines(f"{TAB_SPACE * 2}label: Label[dom=$cdom]\n")
                fp.writelines(f"{TAB_SPACE}$optional: ['label']\n")
                self.sample_struct[list(self.sample_struct.keys())[0]]["param"] = "cdom"
                self.sample_struct[list(self.sample_struct.keys())[0]][
                    "label"
                ] = "label"
            else:
                params = ["cdom" + str(i) for i in range(len(self.sample_struct))]
                fp.writelines(f"{TAB_SPACE}$params: {params}\n")
                fp.writelines(f"{TAB_SPACE}$fields: \n")
                fp.writelines(f"{TAB_SPACE * 2}image: Image\n")
                for name, param, i in zip(
                    self.sample_struct, params, range(len(self.sample_struct))
                ):
                    label = "label" + str(i)
                    label_content = "Label[dom=" + param + "]"
                    fp.writelines(f"{TAB_SPACE *2}{label}: {label_content}\n")
                    self.sample_struct[name]["param"] = param
                    self.sample_struct[name]["label"] = label

    def write_data_yaml(self, import_file_list, out_file):
        """
        import_file_list: $import自段段导入文件
        """
        with open(out_file, "w+") as fp:
            fp.writelines('$dsdl-version: "0.5.0"\n')
            fp.writelines("$import:\n")
            for i in import_file_list:
                fp.writelines(f"{TAB_SPACE}- {i}\n")
            fp.writelines("\n")
            fp.writelines("meta:\n")
            fp.writelines(f'{TAB_SPACE}name: "{self.dataset_name}"\n')
            fp.writelines(f'{TAB_SPACE}creator: "MSRA"\n')
            fp.writelines(f'{TAB_SPACE}dataset-version: "1.0.0"\n')
            fp.writelines(f'{TAB_SPACE}subdata-name: "{self.sub_dataset_name}"\n')
            fp.writelines("\n")
            fp.writelines("data:\n")
            cdom_temp = [
                struct["param"] + "=" + struct["name"]
                for struct in self.sample_struct.values()
            ]
            fp.writelines(
                f"{TAB_SPACE}sample-type: {self.struct_sample_name}[{','.join(cdom_temp)}]\n"
            )
            fp.writelines(f"{TAB_SPACE}samples:\n")
            for sample in self.samples:
                self.write_single_sample(sample, fp)

    def write_single_sample(self, sample, file_point):
        """提取sample信息，并格式化写入yaml文件
        sample = {
            'media': {'path':xxx, 'source':xxx, 'type':'image', 'height':xxx, 'width: xxx'},
            'ground_truth': [{}]}
        }
        """
        image_path = sample["media"]["path"]
        file_point.writelines(f'{TAB_SPACE * 2}- image: "{image_path}"\n')

        if "ground_truth" in sample.keys():
            gts = sample["ground_truth"]
        else:
            gts = []

        for gt in gts:
            if gt["type"] == "classification":
                name = gt["name"]
                cls_id = gt["category_id"]
                cls_name = self.sample_struct[name]["classes"][cls_id]
                label = self.sample_struct[name]["label"]
                try:
                    int(cls_name)
                    file_point.writelines(
                        f"{TAB_SPACE * 2}  {label}: {self.dataset_name}_{cls_name}\n"
                    )
                except ValueError:
                    file_point.writelines(f"{TAB_SPACE * 2}  {label}: {cls_name}\n")
            else:
                pass

    def convert_pipeline(self):
        if not self.output_path:
            temp = os.path.basename(self.dataset_path)
            root_path = os.path.dirname(self.dataset_path)
            self.output_path = os.path.join(root_path, temp + "_dsdl")
            if not os.path.exists(self.output_path):
                os.mkdir(self.output_path)
        self.get_dataset_info()
        file_name = os.path.join(self.dataset_path, "annotations", "json")
        file_list = os.listdir(path=file_name)
        # 1. generate class yaml file
        out_file = os.path.join(self.output_path, "class_dom.yaml")
        self.write_class_yaml(out_file)
        print(f"generate class yaml file: {out_file}")
        # 2. generate struct sample yaml file
        out_file = os.path.join(self.output_path, "struct_sample.yaml")
        self.write_struct_yaml(out_file)
        print(f"generate struct sample yaml file: {out_file}")
        # 3. generate data yaml file
        import_file_list = ["class_dom", "struct_sample"]
        for file in file_list:
            self.get_sample_data(os.path.join(file_name, file))
            out_file = os.path.join(
                self.output_path, self.sub_dataset_name + "_data.yaml"
            )
            self.write_data_yaml(import_file_list, out_file)
            print(f"generate data yaml file: {out_file}")


if __name__ == "__main__":
    args = parse_args()
    print(f"Called with args: \n{args}")
    src_file = args.src_dir
    out_file = args.out_dir
    print(f"your input source dictionary: {src_file}")
    print(f"your input destination dictionary: {out_file}")
    # src_file = "/Users/jiangyiying/sherry/tunas_data_demo/IMAGENET-tunas"
    # out_file = None
    v3toyaml = ConvertV3toDsdlYaml(src_file, out_file)
    v3toyaml.convert_pipeline()
