import os.path

from dsdl.dataset import CheckDataset, ImageVisualizePipeline, Util, Report
import click
import json
from random import randint

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader
from yaml import load as yaml_load
from .commons import OptionEatAll, load_samples, TASK_FIELDS
from ..parser import check_dsdl_parser


@click.command()
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
def check(dsdl_yaml, config, location, num, random, fields, task, position, output):
    assert os.path.isdir(output), "Please use '-o' to specify a existing working dir to generate the log files."
    log_dir = os.path.join(output, "log")
    os.makedirs(log_dir, exist_ok=True)
    report_obj = Report(os.path.join(log_dir, "output.md"))
    with open(dsdl_yaml, "r") as f:
        dsdl_info = yaml_load(f, Loader=YAMLSafeLoader)['data']
        sample_type = dsdl_info['sample-type']
        sample_path = dsdl_info["sample-path"]
        if sample_path == "$local" or sample_path == "local":
            samples = dsdl_info['samples']
        else:
            samples = load_samples(dsdl_yaml, sample_path)
    if position:
        parse_report = check_dsdl_parser(dsdl_yaml, dsdl_library_path=position, report_flag=True)
    else:
        parse_report = check_dsdl_parser(dsdl_yaml, dsdl_library_path="", report_flag=True)
    dsdl_py = parse_report["dsdl_py"]
    parse_report = json.loads(parse_report["check_log"])
    report_obj.set_parser_info(parse_report)
    if parse_report['flag'] == 0:
        report_obj.generate()
        return

    exec(dsdl_py, {})
    config_dic = {}
    with open(config, encoding='utf-8') as config_file:
        exec(config_file.read(), config_dic)
    location_config = config_dic["local" if location == "local" else "ali_oss"]
    dataset = CheckDataset(report_obj, samples, sample_type, location_config)

    palette = {}
    if task:
        assert task in TASK_FIELDS, f"invalid task, you can only choose in {list(TASK_FIELDS.keys())}"
        fields = TASK_FIELDS[task]
    else:
        if fields is None:
            fields = []
        else:
            local_dic = {}
            exec(f"f = list({fields})", {}, local_dic)
            fields = local_dic['f']
        fields = list(set(fields + ["image", "dict"]))
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
    for sample in samples:
        try:
            vis_sample = sample.visualize()
            for vis_name, vis_item in vis_sample.items():
                report_obj.add_image_info({"img": vis_item, "status": "success"})

        except Exception as e:
            report_obj.add_image_info({"img": None, "status": "fail", "msg": repr(e)})

    report_obj.generate()
