import os.path

local = dict(
    type="LocalFileReader",
    working_dir="local path of your media",
)

ali_oss = dict(
    type="AliOSSFileReader",
    access_key_secret="your secret key of aliyun oss",
    endpoint="your endpoint of aliyun oss",
    access_key_id="your access key of aliyun oss",
    bucket_name="your bucket name of aliyun oss",
    working_dir="the relative path of your media dir in the bucket")


class Config:
    root_path = "/Users/jiangyiying/sherry/work/dsdl_test/"
    logger_path = "./log_1030.txt"  # logger文件保存路径
    config_path = "/Users/jiangyiying/sherry/work/dsdl-sdk/dsdl/test/config.py"  # dsdl view命令使用的配置文件路径
    v3_folder_classification = os.path.join(root_path, "datasets/classification")  # 存放v0.3格式的文件夹，会从oss下载到这个文件夹下
    dsdl_folder_classification = os.path.join(root_path, "datasets_dsdl/classification")  # 存放dsdl格式的文件夹，从v0.3格式转换而来，与v0.3格式的文件夹不能相同
    v3_folder_detection = os.path.join(root_path, "datasets/detection")  # 存放v0.3格式的文件夹，会从oss下载到这个文件夹下
    dsdl_folder_detection = os.path.join(root_path, "datasets_dsdl/detection")  # 存放dsdl格式的文件夹，从v0.3格式转换而来，与v0.3格式的文件夹不能相同
    unique_category = "category_name"  # 跑分类数据集的时候，可能需要修改此字段，详见分类转换脚本的readme
    dataset_list_det = [
        "FGVC_Aircraft",
        "KITTI_Object",
        "ILSVRC2015DET",
        "CityPersons",
        "CrowdHuman",
        "DOTA-v1.5",
        "xBD",
        "BDD100KImages",
    ]
    dataset_list_cls = [
        "MNIST",
        # "UCF101",  #'VideoField'
        "Caltech-256",
        "Oxford_102_Flower",
        "Food-101",
        "cats_vs_dogs",
        "STL-10",
        "FGVC_Aircraft",
    ]


config = Config()
