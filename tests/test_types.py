#from config import helloworld_config
#from dsdl.dataset import DemoDataset
#from helloworld_demo.helloworld import ImageClassificationSample
#from PIL import Image
#import io
import pytest

'''
def test_data_check():
    dataset = DemoDataset("helloworld_demo/helloworld.yaml", helloworld_config)
    image = dataset[0].image.to_image()
    image.show()
    for item in dataset.get_sample_list():
        print(item.val, type(item.val), item.i_val, item.p, item.date, item.i_list, item.item_list)
'''

def test_equal():
    assert 1==1

if __name__ == '__main__':
    test_equal()