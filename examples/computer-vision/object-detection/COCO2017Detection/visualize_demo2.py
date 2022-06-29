from demo2.data_field import ObjectDetectionSample
from dsdl.dataset import DetectionDataset

import click
from random import randint


@click.command()
@click.option("-y", "--yaml", "dsdl_yaml", type=str, required=True, help="the path of dsdl yaml file")
@click.option("-c", "--config", type=click.Choice(["local", "ali-oss"]), required=True,
              help="read from local or aliyun-OSS")
@click.option("-n", "--num", type=int, default=10, help="how many samples sampled from the dataset")
@click.option("-r", "--random", is_flag=True, help="whether to sample randomly")
@click.option("-v", "--visualize", is_flag=True, help="whether to visualize the sample selected")
def main(dsdl_yaml, config, num, random, visualize):

    if config == "local":
        from config import coco_config
    else:
        from config import coco_ali_oss_config as coco_config
    dataset = DetectionDataset(dsdl_yaml, coco_config)

    num = min(num, len(dataset))
    if not random:
        indices = list(range(num))
    else:
        indices = [randint(0, len(dataset) - 1) for _ in range(num)]

    samples = []
    for ind in indices:
        samples.append(dataset[ind])

    print(dataset.format_sample(samples))

    if visualize:
        for sample in samples:
            vis_sample = dataset.visualize(sample)
            vis_sample.show()


if __name__ == '__main__':
    main()
