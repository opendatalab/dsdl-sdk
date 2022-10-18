## 执行步骤

1. 安装DSDL sdk
```bash
python setup.py install
```

2. 然后cd到工作路径：`<root>/examples/computer-vision/image-classification`

3. 执行代码 `dsdl_yaml_script`,该代码可以统一将tunas 0.3版本的数据集转换为dsdl所需的yaml文件
   ```bash
   python dsdl_yaml_script.py -s "/Users/jiangyiying/sherry/tunas_data_demo/CIFAR10-tunas" -o "/Users/jiangyiying/sherry/tunas_data_demo/CIFAR10-tunas_dsdl/" -l
   ```
     每个参数的意义为：

   | 参数简写 | 参数全写  | 参数解释                                                                                                                      |
   | ----- |---------------------------------------------------------------------------------------------------------------------------| :----------------------------------------------------------- |
   | -s   | `--src_dir`  | tunas 0.3版本的文件的路径                                                                                                         |
   | -o   | `--out_dir` | 可选，生成的yaml的根路径（可以不写，不写默认为和src_dir为同一个根目录但是文件夹名字加上后缀_dsdl）                                                                 |
   | -c   | `--unique_cate` | 可选，这个参数一般不用管，除非你的数据集的category_name是有重复的（目前只有Imagenet是这样的， 所以Imagenet此处要）设置成`wordnet_id`                                   |
   | -l    |  `--local`  | 可选，是否将数据集中的samples单独存储到一个json文件中还是存储在同一个文件中，当样本数量不大的情况下可以使用该选项，默认存储的文件名为XXX_samples.json，保存在同一个目录下（如果使用`-l`则存在同一个yaml文件中） |

   然后就会生成yaml文件。

4. 使用DSDL的parser生成demo中的`train_data.py`文件
   ```bash
   dsdl parse --yaml examples/computer-vision/image-classification/CIFAR10/train_data.yaml
   ```
   其他可以尝试的例子, eg：
   ```bash
   $ dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo2/coco_val_demo.yaml
   ```
   ```bash
   $ dsdl parse --yaml examples/computer-vision/object-detection/COCO2017Detection/demo2/coco_val_demo.yaml -p examples/computer-vision/object-detection/COCO2017Detection/demo2
   ```
   | 参数简写 | 参数全写  | 参数解释                                                  |
   | ----- | ------| :----------------------------------------------------------- |
   | -y   | `--yaml`  | 数据的yaml文件，一般是train.yaml、test.yaml                                     |
   | -p   | `--path` | 其他yaml存放路径，默认的其他yaml存放路径是`dsdl/dsdl_library` |

   注意:
     - 我们只需要传入数据的yaml文件（如果数据和模型啥的都放一起那就传那个）就会生成在同一目录下的`.py`文件
     - 如果不写`-p`,默认的其他yaml存放路径是`dsdl/dsdl_library`,所以不写`-p`请先把需要import的yaml放进`dsdl/dsdl_library`
