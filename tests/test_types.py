from helloworld import ImageClassificationSample
from dsdl.types import ImageField
import yaml


if __name__ == "__main__":
    with open("./helloworld.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)["data"]
        for item in data.items():
            if item[0] == "samples":
                for sample in item[1]:
                    a = ImageClassificationSample(**sample)
                    print(type(a.valid))
