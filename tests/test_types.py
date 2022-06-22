from helloworld import ImageClassificationSample
from config import helloworld_config
from dsdl import Dataset
from PIL import Image
import io


if __name__ == "__main__":
    dataset = Dataset("./helloworld.yaml", helloworld_config)
    # image = Image.open(io.BytesIO(dataset[0].image.read()))
    # image.show()
    for item in dataset.get_sample_list():
        print(item.val, type(item.val), item.i_val, item.p, item.date, item.i_list)
