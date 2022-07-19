## 执行命令
首先需要在**根目录**下执行以下命令来解析yaml文件：
```bash
dsdl parse --yaml demo/coco_demo.yaml
```
或者
```bash
dsdl parse --yaml demo/voc_demo.yaml
```

1. 执行COCOdemo命令如下：

   ```bash
   python visualize_demo.py -y coco_demo.yaml -c ali-oss -n 10 -r -v -f Label BBox
   ```

   或：

   ```bash
   python visualize_demo.py -y coco_demo.yaml -c ali-oss -n 10 -r -v -t detection
   ```

   

2. 执行VOCdemo命令如下：

   ```bash
   python visualize_demo.py -y voc_demo.yaml -c ali-oss -n 10 -r -v -f Label BBox
   ```
   
   或：
   
   ```bash
   python visualize_demo.py -y voc_demo.yaml -c ali-oss -n 10 -r -v -t detection
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

