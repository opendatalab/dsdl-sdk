from helloworld import ImageClassificationSample
from dsdl import types
import yaml


if __name__ == "__main__":
    sample_list = []
    with open("./helloworld.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)["data"]
        sample_type = data["sample-type"]
        for item in data.items():
            if item[0] == "samples":
                for sample in item[1]:
                    cls = types.registry.get_struct(sample_type)
                    sample_list.append(cls(**sample))

    for item in sample_list:
        print(item.image)
