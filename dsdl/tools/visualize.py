from ..dataset import Dataset, ImageVisualizePipeline, Util
import click
import numpy as np
from random import randint
import cv2
import os

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from .commons import OptionEatAll, prepare_input
from ..parser import dsdl_parse


@click.command(name="view")
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", "config", type=str, required=True, help="the path of the config file")
@click.option("-l", "--location", "location", type=click.Choice(["local", "ali-oss"]), required=True,
              help="the path of the config file")
@click.option("-n", "--num", "num", type=int, default=5, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-v", "--visualize", is_flag=True, help="whether to visualize the sample selected")
@click.option("-f", "--fields", cls=OptionEatAll, type=str, help="the task to visualize")
@click.option("-t", "--task", type=str, help="the task to visualize")
@click.option("-p", "--position", type=str, required=False, help='the directory of dsdl define file')
@click.option("-m", "--multistage", is_flag=True, help="whether to use the generated python file")
@prepare_input(output=None)
def view(dsdl_yaml, num, random, visualize, fields, config, position, multistage, **kwargs):
    # parse
    if multistage:
        dsdl_py = os.path.splitext(dsdl_yaml["yaml_file"])[0] + ".py"
        with open(dsdl_py, encoding='utf-8') as dsdl_file:
            exec(dsdl_file.read(), {})
    else:
        if position:
            dsdl_py = dsdl_parse(dsdl_yaml["yaml_file"], dsdl_library_path=position)
        else:
            dsdl_py = dsdl_parse(dsdl_yaml["yaml_file"], dsdl_library_path="")
        exec(dsdl_py, {})

    dataset = Dataset(dsdl_yaml["samples"], dsdl_yaml["sample_type"], config,
                      global_info=dsdl_yaml["global_info"], global_info_type=dsdl_yaml["global_info_type"])

    num = min(num, len(dataset))
    if not random:
        indices = list(range(num))
    else:
        indices = [randint(0, len(dataset) - 1) for _ in range(num)]

    samples = list()
    palette = dict()
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
