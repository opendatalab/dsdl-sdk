# COCO2017 Object Detection Demo

> - demo1: 最简demo: 所有内容均放入一个yaml文件
> - demo2: 过渡demo: 定义definition模板，支持import操作
> - demo3: 最佳demo: Definition模板 + 类别形参，完全将def模板和data实例解耦

## 执行步骤

1. 安装DSDL sdk
```bash
python setup.py install
```

2. 使用DSDL的parser生成demo中的`data_field.py`文件
```bash
dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo1/coco_val_demo.yaml
dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo2/coco_val_demo.yaml -p examples/computer-vision/object-detection/COCO2017Detection/demo2
dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo3/coco_val_demo.yaml
or (dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo3/coco_val_demo_v2.yaml -p examples/computer-vision/object-detection/COCO2017Detection/demo3)
```

3. 然后cd到工作路径：`<root>/examples/computer-vision/object-detection/COCO2017Detection/demo?`(根据想演示的demo将?替换为1-3具体数字)

4. 待执行的代码为`visualize_demo.py`，在执行代码之前，需要代码做出一些修改：

   1. 在`config.py`中，需要修改其中的  
      a. 本地读取：`local_config`中的参数`working_dir`  
      b. 阿里云OSS读取：`ali_oss_kwargs`中的参数（阿里云OSS的配置`access_key_secret`, `endpoint`, `access_key_id`；桶名称`bucket_name`，数据在桶中的目录`working_dir`）  

5. 执行代码`visualize_demo.py`：

   ```bash
   python visualize_demo.py -y coco_val_demo.yaml -c ali-oss -n 10 -r -v -f label bbox bool
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

