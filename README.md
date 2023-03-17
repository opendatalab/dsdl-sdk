<div align="center">
  <img src="https://raw.githubusercontent.com/opendatalab/dsdl-sdk/2ae5264a7ce1ae6116720478f8fa9e59556bed41/resources/opendatalab.svg" width="600"/>
  <div>&nbsp;</div>
  <div align="center">
    <a href="https://opendatalab.com/"> OpenDataLab Website</a>
    &nbsp;&nbsp;&nbsp;&nbsp;
  </div>
  <div>&nbsp;</div>
</div>

English | [简体中文](README_zh-CN.md)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/odl-cli) ](https://pypi.org/project/odl-cli/)[![PyPI](https://img.shields.io/pypi/v/odl-cli)](https://pypi.org/project/odl-cli/) [![docs](https://img.shields.io/badge/docs-latest-blue)](https://github.com/opendatalab/dsdl-sdk/tree/dev-cli/docs)[![dev workflow](https://github.com/opendatalab/dsdl-sdk/actions/workflows/dev.yml/badge.svg?branch=dev)](https://github.com/opendatalab/dsdl-sdk/actions/workflows/dev.yml)[![stage & preview workflow](https://github.com/opendatalab/dsdl-sdk/actions/workflows/preview.yml/badge.svg?branch=dev)](https://github.com/opendatalab/dsdl-sdk/actions/workflows/preview.yml)

[📘Documentation](https://github.com/opendatalab/dsdl-sdk/tree/dev-cli/docs) |

## Introduction

**Data** is the cornerstone of artificial intelligence. The efficiency of data acquisition, exchange, and application directly impacts the advances in technologies and applications. Over the long history of AI, a vast quantity of data sets have been developed and distributed. However, these datasets are defined in very different forms, which incurs significant overhead when it comes to exchange, integration, and utilization -- it is often the case that one needs to develop a new customized tool or script in order to incorporate a new dataset into a workflow.

To overcome such difficulties, we develop **Data Set Description Language (DSDL)**.

### Major features

The design of **DSDL** is driven by three goals, namely *generic*, *portable*, *extensible*. We refer to these three goals together as **GPE**.

* **Generic**

  This language aims to provide a unified representation standard for data in multiple fields of artificial intelligence, rather than being designed for a single field or task. It should be able to express data sets with different modalities and structures in a consistent format.

* **Portable**

  Write once, distribute everywhere. Dataset descriptions can be widely distributed and exchanged, and used in different environments without modification of the source files. The achievement of this goal is crucial for creating an open and thriving ecosystem. To this end, we need to carefully examine the details of the design, and remove unnecessary dependencies on specific assumptions about the underlying facilities or organizations.

* **Extensible**

  One should be able to extend the boundary of expression without modifying the core standard. For a programming language such as C++ or Python, its application boundaries can be significantly extended by libraries or packages, while the core language remains stable over a long period. Such libraries and packages form a rich ecosystem, making the language stay alive for a very long time.

## Installation

**Case a** install it with pip

```bash
pip install dsdl
```

**Case b** install it from source

```shell
git clone https://github.com/opendatalab/dsdl.git
cd dsdl
python setup.py install
```

## Get Started

#### Use dsdl parser to deserialize the Yaml file to Python code
```bash
dsdl parse --yaml demo/coco_demo.yaml
```

#### Modify the configuration & set the directory of media in dataset

Create a configuration file `config.py` with the following contents（for now dsdl only reading from aliyun oss or local is supported）：

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

 In `config.py`, the configuration of how to read the media in a dataset is defined. One should specify the arguments depending on from where to read the media：  

1. read from local： `working_dir` field in `local` should be specified (the directory of local media)    
2. read from aliyun oss： all the field in `ali_oss `should be specified (including `access_key_secret`, `endpoint`, `access_key_id`, `bucket_name`, `working_dir`)  

#### Visualize samples

   ```bash
   dsdl view -y <yaml-name>.yaml -c <config.py> -l ali-oss -n 10 -r -v -f Label BBox Attributes
   ```

The description of each argument is shown below:  

| simplified  argument | argument      | description                                                                                                                                                                                                                                        |
| -------------------- | ------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -y                   | `--yaml`      | The path of dsdl yaml file.                                                                                                                                                                                                                        |
| -c                   | `--config`    | The path of  location configuration file.                                                                                                                                                                                                          |
| -l                   | `--location`  | `local` or `ali-oss`，which means read media from local or aliyun oss.                                                                                                                                                                             |
| -n                   | `--num`       | The number of samples to be visualized.                                                                                                                                                                                                            |
| -r                   | `--random`    | Whether to load the samples in a random order.                                                                                                                                                                                                     |
| -v                   | `--visualize` | Whether to visualize the samples or just print the information in console.                                                                                                                                                                         |
| -f                   | `--field`     | The field type to visualize, e.g. `-f BBox`means show the bounding box in samples, `-f Attributes`means show the attributes of a sample in the console . One can specify multiple field types simultaneously, such as `-f Label BBox  Attributes`. |
| -t                   | `--task`      | The task you are working on, for example, `-t detection` is equivalent to `-f Label BBox Polygon Attributes`.                                                                                                                                      |

## Citation

If you find this project useful in your research, please consider cite:

```bibtex
@misc{dsdl2022,
    title={{DSDL}: Data Set Description Language},
    author={DSDL Contributors},
    howpublished = {\url{https://github.com/opendatalab/dsdl}},
    year={2022}
}
```

## License

`DSDL` is released under the [Apache 2.0 license](LICENSE).

## Acknowledgement

* Field & Model Design inspired by [Django ORM](https://www.djangoproject.com/) and [jsonmodels](https://github.com/jazzband/jsonmodels)
