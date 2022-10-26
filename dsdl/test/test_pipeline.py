import pytest
from tunas2dsdl.cli import convert
from examples.computer_vision.image_classification.dsdl_yaml_script import ConvertV3toDsdlYaml


tunas_dir_list = ["/Users/jiangyiying/sherry/tunas_data_demo/CIFAR10-tunas", ]

# content of test_sample.py
def func(x):
    return x + 1


@pytest.mark.parametrize('tunas_dir', tunas_dir_list)
def test_tunas2dsdl(tunas_dir):
    assert func(3) == 5