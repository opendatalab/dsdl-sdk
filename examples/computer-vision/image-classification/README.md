## 执行步骤

1. 安装DSDL sdk
```bash
python setup.py install
```

2. 然后cd到工作路径：`<root>/examples/computer-vision/image-classification`

3. 执行代码 `dsdl_yaml_script`,该代码可以统一将tunas 0.3版本的数据集转换为dsdl所需的yaml文件
   ```bash
   python dsdl_yaml_script.py -s "/Users/jiangyiying/sherry/tunas_data_demo/CIFAR10-tunas" -o "/Users/jiangyiying/sherry/tunas_data_demo/CIFAR10-tunas_dsdl/"
   ```
     每个参数的意义为：

   | 参数简写 | 参数全写  | 参数解释                                                  |
   | ----- | ------| :----------------------------------------------------------- |
   | -s   | `--src_dir`  | tunas 0.3版本的文件的路径                                       |
   | -o   | `--out_dir` | 生成的yaml的根路径（可以不写，不写默认为和src_dir为同一个根目录但是文件夹名字加上后缀_dsdl） |

   然后就会生成yaml文件。

2. 使用DSDL的parser生成demo中的`train_data.py`文件
```bash
dsdl parse --yaml examples/computer-vision/image-classification/CIFAR10/train_data.yaml
```
