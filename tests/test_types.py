from config import helloworld_config
from dsdl.dataset import DemoDataset
from helloworld_demo.data_field import ImageClassificationSample
from PIL import Image
import io


def test_data_check():
    dataset = DemoDataset("helloworld_demo/helloworld.yaml", helloworld_config)
    image = Image.open(io.BytesIO(dataset[0].image.read()))
    image.show()
    for item in dataset.get_sample_list():
        print(item.val, type(item.val), item.i_val, item.p, item.date, item.i_list, item.item_list)

if __name__ == '__main__':
    test_data_check()