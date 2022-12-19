import os.path
from environs import Env

local = dict(
    type="LocalFileReader",
    working_dir="local path of your media",
)

env = Env()
ali_oss = env.dict('ALI_OSS_DICT')


class Config:
    project_path = os.getcwd()
    root_path = os.path.join(project_path, "dsdl_test")
    temp_file_path = os.path.join(project_path, "temp.py")
    logger_path = os.path.join(project_path, "log_1030.txt")  # logger文件保存路径
    config_path = os.path.join(project_path, "config.py")   # dsdl view命令使用的配置文件路径
    v3_folder = os.path.join(root_path, "datasets")  # 存放v0.3格式的文件夹，会从oss下载到这个文件夹下
    dsdl_folder = os.path.join(
        root_path, "datasets_dsdl"
    )  # 存放dsdl格式的文件夹，从v0.3格式转换而来，与v0.3格式的文件夹不能相同
    unique_category = "category_name"  # 跑分类数据集的时候，可能需要修改此字段，详见分类转换脚本的readme
    dataset_list = {
        "classification": [
            "MNIST",
            # "UCF101",  #'VideoField'
            "Caltech-256",
            "Oxford_102_Flower",
            "Food-101",
            # "cats_vs_dogs",
            "STL-10",
            # "FGVC_Aircraft",
        ],
        "detection": [
            "FGVC_Aircraft",
            "KITTI_Object",
            # "ILSVRC2015DET",
            # "CityPersons",
            # "CrowdHuman",  # too large
            # "DOTA-v1.5",
            "xBD",
            "BDD100KImages",
        ],
    }

