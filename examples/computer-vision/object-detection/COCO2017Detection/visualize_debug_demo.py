from demo3.data_field import ObjectDetectionSample
from dsdl.dataset import Dataset, ImageVisualizePipeline, Util

import click
import numpy as np
from random import randint
import cv2


@click.command()
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", type=click.Choice(["local", "ali-oss"]), required=True,
              help="read from local or aliyun-OSS")
@click.option("-n", "--num", type=int, default=10, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-v", "--visualize", is_flag=True, help="whether to visualize the sample selected")
@click.option("-f", "--fields", "field_list", required=True, help="the fields to display")
def main(dsdl_yaml, config, num, random, visualize, field_list):

    # 判断当前是读取本地文件还是阿里云OSS上的文件
    if config == "local":
        from config import coco_config
    else:
        from config import coco_ali_oss_config as coco_config
    dataset = Dataset(dsdl_yaml, coco_config)
    palette = {}
    field_list = [_.lower() for _ in field_list]
    # field_lst = ["image", "label", "bbox", "bool"]
    # # field_lst = ["image", "bbox", "bool"]
    # 选取要读取的样本的索引
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
    main()
