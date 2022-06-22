# -*-coding:utf-8-*-
#########################################################################
#    > File Name: convert2dsdl.py
#    > Author: Bin Wang
#    > Created Time: Tue 17 May 2022 07:33:40 AM UTC
#    > Desciption: 提取json文件中的标注信息，写入dsdl对应的data samples
#########################################################################
import sys
import json
import argparse
import pdb


TAB_SPACE = "    "


def get_dict(file_name):
    dict_id_class = {}
    with open("./coco_id-class.txt") as fp:
        for line in fp.readlines():
            id, clss = line.strip().split(":")
            id = int(id)
            dict_id_class[id] = clss
    return dict_id_class


def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description="Convert v0.3 format to dsdl yaml file."
    )
    parser.add_argument(
        "--subdata_name",
        dest="subdata_name",
        help="Subdataset name: train/val/test",
        default="val",
        type=str,
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(-1)

    args = parser.parse_args()
    return args


def write_sample(sample, file_point, dict_id_class):
    """提取sample信息，并格式化写入yaml文件
    sample = {
        'media': {'path':xxx, 'source':xxx, 'type':'image', 'height':xxx, 'width: xxx'},
        'ground_truth': {list of {'bbox':[x1,y1,w,h], 'ann_id':xxx,..., 'categories:[{}]'}}
    }
    """
    image_path = sample["media"]["path"]
    file_point.writelines(f'{TAB_SPACE*2}image: "{image_path}"\n')

    if "ground_truth" in sample.keys():
        gts = sample["ground_truth"]
    else:
        gts = []

    file_point.writelines(f"{TAB_SPACE*2}objects:\n")
    for i in range(len(gts)):
        if gts[i]["type"] == "box2d":
            [x1, y1, w, h] = gts[i]["bbox"]
            cls_id = gts[i]["categories"][0]["category_id"]
            cls_name = dict_id_class[cls_id]
            is_crowd = True if gts[i]["attributes"]["iscrowd"] else False
            file_point.writelines(
                f'{TAB_SPACE*3}- {{ bbox: [{x1}, {y1}, {w}, {h}], label: "{cls_name}", is_crowd: {is_crowd} }}\n'
            )
        else:
            pass


if __name__ == "__main__":

    args = parse_args()
    print(f"Called with args: \n{args}")
    src_file = f"./{args.subdata_name}2017.json"
    out_file = f"./{args.subdata_name}_data.yaml"
    print(f"source file: {src_file}")
    print(f"res file: {out_file}")

    file_id_class = "./coco_id-class.txt"
    dict_id_class = get_dict(file_id_class)

    with open(src_file) as fp:
        train_data = json.load(fp)

    with open(out_file, "w") as fp:
        fp.writelines("data:\n")
        fp.writelines(
            f"{TAB_SPACE}sample-type: ObjectDetectionSample[cdom=COCOClassDom]\n"
        )
        fp.writelines(f"{TAB_SPACE}samples:\n")

        samples = train_data["samples"]
        # for i in range(len(samples)):
        for i in range(100):
            write_sample(samples[i], fp, dict_id_class)
