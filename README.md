# DSDL-SDK

基于DSDL的开发工具包，包含：
1. 基于DSDL的数据集描述
2. 对应DSDL语法解析器

## 安装

python 环境3.8及以上
```bash
$ python setup.py install
```

parser入口

```bash
$ dsdl parse --yaml tests/helloworld_demo/helloworld.yaml
```
其他可以尝试的例子：
1. 这个demo2的例子没写`-p`是因为，已经把需要import的yaml放进`dsdl/dsdl_library`里面了哦，不然要写明地址
```bash 
$ dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo2/coco_val_demo.yaml
```
2.
```bash
$ dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo3/coco_val_demo.yaml -p examples/computer-vision/object-detection/COCO2017Detection/demo3
```
注意:
1. 我们只需要传入数据的yaml文件（如果数据和模型啥的都放一起那就传那个）就会生成在同一目录下的`.py`文件
2. 如果不写`-p`,默认的其他yaml存放路径是`dsdl/dsdl_library`,所以不写`-p`请先把需要import的yaml放进`dsdl/dsdl_library`
## Acknowledgments

* Field & Model Design inspired by [Django ORM](https://www.djangoproject.com/) and [jsonmodels](https://github.com/jazzband/jsonmodels)

