from dsdl.dataset import Dataset, ImageVisualizePipeline, Util
import click
import numpy as np
from random import randint
import cv2

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from yaml import load as yaml_load
from .commons import OptionEatAll, load_samples
from ..parser import dsdl_parse


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
@click.option("-p", "--position", type=str, required=False, help='the directory of dsdl define file')
def view(dsdl_yaml, config, location, num, random, visualize, fields, task, position):
    with open(dsdl_yaml, "r") as f:
        dsdl_info = yaml_load(f, Loader=YAMLSafeLoader)['data']
        sample_type = dsdl_info['sample-type']
        sample_path = dsdl_info["sample-path"]
        if sample_path == "$local" or sample_path == "local":
            samples = dsdl_info['samples']
        else:
            samples = load_samples(dsdl_yaml, sample_path)
    if position:
        dsdl_py = dsdl_parse(dsdl_yaml, position)
    else:
        dsdl_py = dsdl_parse(dsdl_yaml)
    exec(dsdl_py, {})
    config_dic = {}
    with open(config, encoding='utf-8') as config_file:
        exec(config_file.read(), config_dic)
    location_config = config_dic["local" if location == "local" else "ali_oss"]
    dataset = Dataset(samples, sample_type, location_config)

    palette = {}
    if task:
        assert task in ["detection",
                        "segmentation",
                        "classification"], "invalid task, you can only choose in ['detection', 'segmentation', 'classification']"
        if task == "classification":
            fields = ["image", "label"]
        elif task == "detection":
            fields = ["image", "label", "bbox", "polygon", "attributes"]
        elif task == "segmentation":
            fields = ["image", "segmap", "attributes"]
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
