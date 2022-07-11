- demo1: 单个yaml文件定义数据集描述
- demo2: 使用import方式定义数据集描述，可以构建lib的方式共享复用
- demo3: 使用import方式，使用DSDL提供的lib
- json: OpenDataLab v0.3版本格式化数据集描述，作为dsdl的参考信息

## 执行步骤

1. 安装DSDL sdk

```bash
python setup.py install
```

2. 使用DSDL的parser生成demo3中的`data_field.py`文件

```bash
dsdl parse --yaml examples/computer-vision/object-detection/VOC2012Detection/demo3/data_samples.yaml
```

3. 然后cd到工作路径：`<root>/examples/computer-vision/object-detection/VOC2012Detection/demo?`(根据想演示的demo将?替换为1-3具体数字)

4. 待执行的代码为`visualize_demo.py`，在执行代码之前，需要代码做出一些修改：

   1. 在`config.py`中，需要修改其中的
      1. `ali_oss_kwargs`中的参数（阿里云OSS的配置`access_key_secret`, `endpoint`, `access_key_id`；桶名称`bucket_name`，数据在桶中的目录`working_dir`）
      2. `coco_config`中的参数`working_dir`（本地数据所在的目录）

5. 执行代码`visualize_demo.py`：

   ```bash
   python visualize_demo.py -y data_samples.yaml -c ali-oss -n 10 -r -v -f Label BBox
   ```

   或：

   ```bash
   python visualize_demo.py -y data_samples.yaml -c ali-oss -n 10 -r -v -t detection
   ```
   
   
   
   每个参数的意义为：
   
   | 参数简写 | 参数全写      | 参数解释                                                     |
   | -------- | ------------- | :----------------------------------------------------------- |
   | -y       | `--yaml`      | dsdl_yaml文件的路径                                          |
   | -c       | `--config`    | 只可以指定为`local`或是`ali-oss`，分别表示读取本地的数据与读取阿里云的数据 |
   | -n       | `--num`       | 加载数据集的样本数量                                         |
   | -r       | `--random`    | 在加载数据集中的样本时是否随机选取样本，如果不指定的话就按顺序从开始选取样本 |
   | -v       | `--visualize` | 是否将加载的数据进行可视化展示                               |
   | -f       | `--field`     | 选择需要进行可视化的字段，如`-f BBox`表示可视化bbox，`-f Label`表示对label进行可视化等等，可以同时选择多个，如`-f Label BBox` |
   | -t       | `--task`      | 可以选择当前需要可视化的任务类型，如果选择`-t detection`，则等价于`-f Label BBox` |

