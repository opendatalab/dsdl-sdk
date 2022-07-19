# DSDL-SDK 使用说明

## 1. 安装DSDL

python 环境3.8及以上
```bash
python setup.py install
```

## 2. Demo演示（COCO数据集可视化）

#### 2.1 解析器反序列化Yaml为Python代码
```bash
dsdl parse --yaml demo/coco_demo.yaml
```

#### 2.2 配置文件修改，设置读取路径

  在`config.py`中，列举了所有支持的媒体文件读取方式，根据实际情况选择并配置文件路径等信息：  
  a.本地读取： `local_config`中的参数`working_dir`（本地数据所在的目录）    
  b.阿里云OSS读取： `ali_oss_kwargs`中的参数（阿里云OSS的配置`access_key_secret`, `endpoint`, `access_key_id`；桶名称`bucket_name`，数据在桶中的目录`working_dir`）  

#### 2.3 可视化功能展示：

   ```bash
   python visualize.py -y <yaml-name>.yaml -c ali-oss -n 10 -r -v -f label bbox bool
   ```

   每个参数的意义为：

   | 参数简写 | 参数全写      | 参数解释                                                     |
   | -------- | ------------- | :----------------------------------------------------------- |
   | -y       | `--yaml`      | dsdl_yaml文件的路径                                          |
   | -c       | `--config`    | 只可以指定为`local`或是`ali-oss`，分别表示读取本地的数据与读取阿里云的数据 |
   | -n       | `--num`       | 加载数据集的样本数量                                         |
   | -r       | `--random`    | 在加载数据集中的样本时是否随机选取样本，如果不指定的话就按顺序从开始选取样本 |
   | -v       | `--visualize` | 是否将加载的数据进行可视化展示                               |
   | -f       | `--field`     | 选择需要进行可视化的字段，如`-f bbox`表示可视化bbox，`-f label`表示对label进行可视化等等，可以同时选择多个，如`-f label bbox bool` |


## Acknowledgments

* Field & Model Design inspired by [Django ORM](https://www.djangoproject.com/) and [jsonmodels](https://github.com/jazzband/jsonmodels)
