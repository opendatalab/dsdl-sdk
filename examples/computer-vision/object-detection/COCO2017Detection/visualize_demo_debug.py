from dsdl.dataset import Dataset, ImageVisualizePipeline, Util

import numpy as np
from random import randint
import cv2
import os
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("-y", "--yaml", type=str, required=True, help="the path of dsdl yaml file")
    parser.add_argument("-c", "--config", choices=["local", "ali-oss"], required=True,
                        help="read from local or aliyun-OSS")
    parser.add_argument("-n", "--num", type=int, default=10, help="how many samples sampled from the dataset")
    parser.add_argument("-r", "--random", action="store_true", default=False, help="whether to sample randomly")
    parser.add_argument("-v", "--visualize", action="store_true", default=False, help="whether to visualize the sample selected")
    parser.add_argument("-f", "--fields", nargs="+", type=str, help="the fields to display")
    return parser.parse_args()


def main(dsdl_yaml, config, num, random, visualize, field_list):
    dsdl_name = os.path.splitext(os.path.basename(dsdl_yaml))[0]
    exec(f"from {dsdl_name} import *")
    # 判断当前是读取本地文件还是阿里云OSS上的文件
    if config == "local":
        from config import local_config as location_config
    else:
        from config import ali_oss_config as location_config
    dataset = Dataset(dsdl_yaml, location_config)
    palette = {}
    field_list = [_.lower() for _ in field_list]
    if "image" not in field_list:
        field_list.append("image")
    num = min(num, len(dataset))
    if not random:
        indices = list(range(num))
    else:
        indices = [randint(0, len(dataset) - 1) for _ in range(num)]

    samples = []
    for ind in indices:
        samples.append(ImageVisualizePipeline(sample=dataset[ind], palette=palette, field_list=field_list))

    print(Util.format_sample([s.format() for s in samples]))
    # 将读取的样本进行可视化
    if visualize:
        for sample in samples:
            vis_sample = sample.visualize()
            for vis_name, vis_item in vis_sample.items():
                cv2.imshow(vis_name, cv2.cvtColor(np.array(vis_item), cv2.COLOR_BGR2RGB))
                cv2.waitKey(0)


if __name__ == '__main__':

    main("coco_demo.yaml", "ali-oss", 3, True, True, ["label", "bool"])
