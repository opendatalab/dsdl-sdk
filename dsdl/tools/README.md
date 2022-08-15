# 运行步骤

1. cd dsdl/tools

2. 执行命令：

   ```bash
   python tunas2dsdl_detection_demo.py -i <path of dataset_info.json> -a <path of annotation.json> -w <working_dir>
   ```

# 参数解释

| 参数                  | 解释                                    |
| --------------------- | --------------------------------------- |
| `-i`/`--dataset_info` | tunas v0.3的dataset_info.json的文件路径 |
| `-a`/`--ann_info`     | tunas v0.3的标注文件的路径              |
| `-w`/`--working_dir`  | 运行结果的保存目录（目录需要存在）      |

**举例：**

```bash
python tunas2dsdl_detection_demo.py -i ./dataset_info.json -a ./val2017.json -w ./result
```