<div align="center">
  <img src="https://raw.githubusercontent.com/opendatalab/dsdl-sdk/2ae5264a7ce1ae6116720478f8fa9e59556bed41/resources/opendatalab.svg" width="600"/>
  <div>&nbsp;</div>
  <div align="center">
    <a href="https://opendatalab.com/"> OpenDataLab Website</a>
    &nbsp;&nbsp;&nbsp;&nbsp;
  </div>
  <div>&nbsp;</div>
</div>

[English](README.md) | 简体中文

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dsdl) ](https://pypi.org/project/dsdl/)[![PyPI](https://img.shields.io/pypi/v/dsdl)](https://pypi.org/project/dsdl) [![docs](https://img.shields.io/badge/docs-latest-blue)](https://opendatalab.github.io/dsdl-docs/)

[📘使用文档](https://opendatalab.github.io/dsdl-docs/) |

## 简介

**数据**是人工智能的基石。数据获取、传播和使用的效率直接影响科技发展和应用进步。在人工智能漫长历史中，大量的数据集被制造和发布推动整个领域的发展。然而，这些数据集基于不同的形式定义，使得其在传播、融合和使用时成本较高。这通常表现为每个使用者/团队需要制定一套新的格式，开发定制化工具或脚本将新的数据集标准化合并到已有的工作流。

为了克服上述问题，我们设计了一套数据集描述语言DSDL(Data Set Description Language)。

### 主要特性

DSDL的设计目标总共有三点：**通用性(Generic)**，**便携性(Portable)**，以及**可拓展性(Extensible)**。三种特性总称为**GPE**。

* **通用性**

  该语言主要目的是提供一种统一表示的标准，可以覆盖各个领域的人工智能数据，而不是基于特定的一种任务或者某个领域设计。该语言应该可以用一致的格式来表达不同模态和结构的数据。

* **便携性**

  写完无需修改，随处分发。数据集描述可以被广泛的分发和交换，不需要修改就可以在各种环境下使用。这一目标的实现对于建立开发繁荣生态至关重要。为此我们需要仔细检查实现细节，使其对底层设施或组织无感知，从而去除基于特定假设的无必要依赖。

* **可拓展性**

  在不需要修改核心标准的情况下可以拓展表述的边界。对于C++或者Python等编程语言，应用边界可以通过使用链接库或者软件包得以显著拓展，而核心语法可以在很长的时间内保持稳定。基于链接库和包，可以形成丰富的生态系统，使对应语言可以长时间保持活跃度和发展。

## 安装

**方法1** 作为python包安装

```bash
pip install dsdl
```

**方法2** 从源码安装

```shell
git clone https://github.com/opendatalab/dsdl.git
cd dsdl
python setup.py install
```

## 快速入门

#### 解析器反序列化Yaml文件为Python代码
```bash
dsdl parse --yaml demo/coco_demo.yaml
```

#### 配置文件修改，设置读取路径

创建配置文件`config.py`，内容如下（目前只支持读取阿里云OSS数据与本地数据）：

```python
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
```

  在`config.py`中，列举了所有支持的媒体文件读取方式，根据实际情况选择并配置文件路径等信息：  

1. 本地读取： `local`中的参数`working_dir`（本地数据所在的目录）    
2. 阿里云OSS读取： `ali_oss`中的参数（阿里云OSS的配置`access_key_secret`, `endpoint`, `access_key_id`；桶名称`bucket_name`，数据在桶中的目录`working_dir`）  

#### 可视化功能展示

   ```bash
   dsdl view -y <yaml-name>.yaml -c <config.py> -l ali-oss -n 10 -r -v -f Label BBox Attributes
   ```

每个参数的意义为：

| 参数简写 | 参数全写      | 参数解释                                                                                                                                                  |
| -------- | ------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -y       | `--yaml`      | 定义所有samples的yaml文件的路径                                                                                                                           |
| -c       | `--config`    | 配置文件（`config.py`）的路径                                                                                                                             |
| -l       | `--location`  | 只可以指定为`local`或是`ali-oss`，分别表示读取本地的数据与读取阿里云的数据                                                                                |
| -n       | `--num`       | 加载数据集的样本数量                                                                                                                                      |
| -r       | `--random`    | 在加载数据集中的样本时是否随机选取样本，如果不指定的话就按顺序从开始选取样本                                                                              |
| -v       | `--visualize` | 是否将加载的数据进行可视化展示                                                                                                                            |
| -f       | `--field`     | 选择需要进行可视化的字段，如`-f BBox`表示可视化bbox，`-f Attributes`表示对样本的attributes进行可视化等等，可以同时选择多个，如`-f Label BBox  Attributes` |
| -t       | `--task`      | 可以选择当前需要可视化的任务类型，如果选择`-t detection`，则等价于`-f Label BBox Polygon Attributes`                                                      |

## 引用

如果你觉得本项目对你的研究工作有所帮助，请参考如下 bibtex 引用 DSDL。

```bibtex
@misc{dsdl2022,
    title={{DSDL}: Data Set Description Language},
    author={DSDL Contributors},
    howpublished = {\url{https://github.com/opendatalab/dsdl}},
    year={2022}
}
```

## 开源许可证

`DSDL` 采用 [Apache 2.0 开源许可证](LICENSE)。

## 声明

* 字段与模型的设计受到了 [Django ORM](https://www.djangoproject.com/) 和 [jsonmodels](https://github.com/jazzband/jsonmodels)的启发
