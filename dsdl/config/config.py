from dsdl.config.utils import YamlConfig


class Config(YamlConfig):
    # 如果用户给定的yaml中没有定义一些东西，就用我们默认的：
    DSDL_LIBRARY_PATH: str = "/XXXX/COCO2017Detection/demo1"
    DATA_YAML: str = "coco_val_demo.yaml"
    STRUCT_YAML: str
    CLASS_YAML: str



