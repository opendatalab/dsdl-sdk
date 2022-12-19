import os.path

from dsdl.dataset import CheckDataset, ImageVisualizePipeline, Util, Report
import click
import json
from random import randint

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from .commons import OptionEatAll, prepare_input
from ..parser import check_dsdl_parser


@click.command(name="check")
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", "config", type=str, required=True, help="the path of the config file")
@click.option("-l", "--location", "location", type=click.Choice(["local", "ali-oss"]), required=True,
              help="the path of the config file")
@click.option("-n", "--num", "num", type=int, default=5, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-f", "--fields", cls=OptionEatAll, type=str, help="the task to visualize")
@click.option("-t", "--task", type=str, help="the task to visualize")
@click.option("-p", "--position", type=str, required=False, help='the directory of dsdl define file')
@click.option("-o", "--output", type=str, help="the dir to output the check report")
@prepare_input(visualize=True, multistage=False)
def check(dsdl_yaml, num, random, fields, config, position, output, **kwargs):
    assert os.path.isdir(output), "Please use '-o' to specify a existing working dir to generate the log files."
    log_dir = os.path.join(output, "log")
    os.makedirs(log_dir, exist_ok=True)
    report_obj = Report(os.path.join(log_dir, "output.md"))

    # parse
    if position:
        parse_report = check_dsdl_parser(dsdl_yaml["yaml_file"], dsdl_library_path=position, report_flag=True)
    else:
        parse_report = check_dsdl_parser(dsdl_yaml["yaml_file"], dsdl_library_path="", report_flag=True)
    dsdl_py = parse_report["dsdl_py"]
    parse_report = json.loads(parse_report["check_log"])
    report_obj.set_parser_info(parse_report)
    if parse_report['flag'] == 0:
        report_obj.generate()
        return
    exec(dsdl_py, {})

    dataset = CheckDataset(report_obj, dsdl_yaml["samples"], dsdl_yaml["sample_type"], config,
                           global_info_type=dsdl_yaml["global_info_type"], global_info=dsdl_yaml["global_info"])

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
    for sample in samples:
        try:
            vis_sample = sample.visualize()
            for vis_name, vis_item in vis_sample.items():
                report_obj.add_image_info({"img": vis_item, "status": "success"})

        except Exception as e:
            report_obj.add_image_info({"img": None, "status": "fail", "msg": repr(e)})

    report_obj.generate()
