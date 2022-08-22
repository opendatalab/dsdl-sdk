from dsdl.dataset import Dataset, ImageVisualizePipeline, Util
import click
import numpy as np
from random import randint
import cv2
import os

from .commons import OptionEatAll


@click.command()
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", "config", type=str, required=True, help="the path of the config file")
@click.option("-l", "--location", "location", type=click.Choice(["local", "ali-oss"]), required=True,
              help="the path of the config file")
@click.option("-n", "--num", "num", type=int, default=5, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-v", "--visualize", is_flag=True, help="whether to visualize the sample selected")
@click.option("-f", "--fields", cls=OptionEatAll, type=str, help="the task to visualize")
@click.option("-t", "--task", type=str, help="the task to visualize")
def view(dsdl_yaml, config, location, num, random, visualize, fields, task):
    dsdl_py = os.path.splitext(dsdl_yaml)[0] + ".py"
    print(dsdl_py)
    with open(dsdl_py, encoding='utf-8') as dsdl_file:
        exec(dsdl_file.read(), {})

    config_dic = {}
    with open(config, encoding='utf-8') as config_file:
        exec(config_file.read(), config_dic)
    location_config = config_dic["local" if location == "local" else "ali_oss"]

    dataset = Dataset(dsdl_yaml, location_config)
    palette = {}
    if task:
        assert task in ["detection",
                        "segmentation"], "invalid task, you can only choose in ['detection', 'segmentation']"
        if task == "detection":
            fields = ["image", "label", "bbox", "polygon", "attributes"]
        else:
            fields = ["image", "label", "attributes"]
    else:

        if fields is None:
            fields = []
        else:
            local_dic = {}
            exec(f"f = list({fields})", {}, local_dic)
            fields = local_dic['f']
        fields = list(set(fields + ["image", "attributes"]))
    fields = [_.lower() for _ in fields]

    num = min(num, len(dataset))

    if not random:
        indices = list(range(num))
    else:
        indices = [randint(0, len(dataset) - 1) for _ in range(num)]

    samples = []
    for ind in indices:
        samples.append(ImageVisualizePipeline(sample=dataset[ind], palette=palette, field_list=fields))

    print(Util.format_sample([s.format() for s in samples]))
    # 将读取的样本进行可视化
    if visualize:
        for sample in samples:
            vis_sample = sample.visualize()
            for vis_name, vis_item in vis_sample.items():
                cv2.imshow(vis_name, cv2.cvtColor(np.array(vis_item), cv2.COLOR_BGR2RGB))
                cv2.waitKey(0)
