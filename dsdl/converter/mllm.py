import os
from pathlib import Path
from collections import defaultdict


def generate_config_file(save_root_path):
    config_str = """
local = dict(
    type="LocalFileReader",
    working_dir="the root path of the prepared dataset",)

ali_oss = dict(
    type="AliOSSFileReader",
    access_key_secret="your secret key of aliyun oss",
    endpoint="your endpoint of aliyun oss",
    access_key_id="your access key of aliyun oss",
    bucket_name="your bucket name of aliyun oss",
    working_dir="the path of the prepared dataset without the bucket's name")
    """
    save_path_p = Path(save_root_path)
    config_new_path = save_path_p.joinpath("config.py")
    if not config_new_path.exists():
        with open(str(config_new_path), 'w', encoding='utf-8') as fp:
            fp.write(config_str)
    else:
        print("config.py already exists!")

def generate_tree_generator(dir_path, prefix='', space='    ', branch='│   ', tee='├── ', last='└── ', display_num=3):
    _, folders, files = next(os.walk(dir_path))
    if len(folders)>display_num:
        folders[display_num:]=["..."]
    ext_list = defaultdict(list)
    files_list = []
    for file in sorted(files):
        ext = os.path.splitext(file)[1]
        if len(ext_list[ext])<display_num:
            ext_list[ext].append(file)            
        elif len(ext_list[ext])==display_num:
            ext_list[ext].append("...")            
        else:
            continue
    for ext in ext_list:
        files_list.extend(ext_list[ext])
    # 中间的用 ├── ，最后一个用 └── :
    pointers = [tee] * (len(folders)+len(files_list) - 1) + [last]
    
    for pointer, path in zip(pointers[:len(folders)], folders):
        yield prefix + pointer + path
        if path == "...":
            continue
        extension = branch if pointer == tee else space 
        # 文件夹需要递归遍历
        yield from generate_tree_generator(os.path.join(dir_path, path), prefix=prefix+extension, space=space, branch=branch, tee=tee, last=last, display_num=display_num)
    
    for pointer, path in zip(pointers[len(folders):], files_list):
        yield prefix + pointer + path

def generate_tree_string(path_in):
    tree_str = ""
    tree_iter = generate_tree_generator(path_in)
    for line in tree_iter:
        tree_str += f"{line}\n"
    return tree_str

def generate_readme_without_middle_format(save_root_path, dataset_name, original_tree, dsdl_tree):
    readme_str = f"""# Data Set Description Language(DSDL) for {dataset_name} dataset

## Data Structure
Please make sure the folder structure of prepared dataset is organized as followed:

```
<dataset_root>
{original_tree}
```

The folder structure of dsdl annotation is organized as followed:
```
<dataset_root>
{dsdl_tree}
```

## config.py
You can load your dataset from local or oss.
From local:

```
local = dict(
    type="LocalFileReader",
    working_dir="the root path of the prepared dataset",
)
```
Please change the 'working_dir' to the path of your prepared dataset where media data can be found,
for example: "<root>/dataset_name/prepared".

From oss:
```
ali_oss = dict(
    type="AliOSSFileReader",
    access_key_secret="your secret key of aliyun oss",
    endpoint="your endpoint of aliyun oss",
    access_key_id="your access key of aliyun oss",
    bucket_name="your bucket name of aliyun oss",
    working_dir="the path of the prepared dataset without the bucket's name")
```
Please change the 'access_key_secret', 'endpoint', 'access_key_id', 'bucket_name' and 'working_dir',
for example: "/dataset_name/prepared".

## official docs: 
[dsdl-docs](https://opendatalab.github.io/dsdl-docs/)

## official repo:
[dsdl-sdk](https://github.com/opendatalab/dsdl-sdk)

## get more dataset:
[opendatalab](https://opendatalab.com/)
"""
    save_path_p = Path(save_root_path)
    readme_new_path = save_path_p.joinpath("README.md")
    if not readme_new_path.exists():
        with open(str(readme_new_path), 'w', encoding='utf-8') as fp:
            fp.write(readme_str)
    else:
        print("README.md already exists.")

def generate_readme_with_middle_format(save_root_path, dataset_name, original_tree, prepared_tree, dsdl_tree, dataset_converter_description):
    readme_str = f"""# Data Set Description Language(DSDL) for {dataset_name} dataset

To make sure the DSDL dataset run successfully, the tools/prepare.sh should be executed. 
For this dataset, the following step will be executed:
- decompress
- prepare dataset and generate DSDL annotation

Each steps will be explained in the following section.
If you want to skip any of these steps, please comment out this part of the code in tools/prepare.sh.
Please run following command in your terminal, make sure to change the <path_to_the_compressed_dataset>:

```
sh tools/prepare.sh <path_to_the_compressed_dataset>
```

## decompress
If you download the dataset package from OpenDataLab, you can run the decompress part directly.
If you already decompress the dataset, please make sure the folder structure is organized as followed:
```
<dataset_root>
{original_tree}
```

## prepare dataset and generate DSDL annotation
It can help prepare dataset and generate DSDL annotation. {dataset_converter_description}
After that, the folder structure of prepared dataset is organized as followed:

```
<dataset_root>
{prepared_tree}
```

It also generate DSDL annotation, the folder of dsdl is organized as followed:
```
<dsdl_root>
{dsdl_tree}
```

## config.py
You can load your dataset from local or oss.
From local:

```
local = dict(
    type="LocalFileReader",
    working_dir="the root path of the prepared dataset",
)
```
Please change the 'working_dir' to the path of your prepared dataset where media data can be found,
for example: "<root>/dataset_name/prepared".

From oss:
```
ali_oss = dict(
    type="AliOSSFileReader",
    access_key_secret="your secret key of aliyun oss",
    endpoint="your endpoint of aliyun oss",
    access_key_id="your access key of aliyun oss",
    bucket_name="your bucket name of aliyun oss",
    working_dir="the path of the prepared dataset without the bucket's name")
```
Please change the 'access_key_secret', 'endpoint', 'access_key_id', 'bucket_name' and 'working_dir',
for example: "/dataset_name/prepared".

## official docs: 
[dsdl-docs](https://opendatalab.github.io/dsdl-docs/)

## official repo:
[dsdl-sdk](https://github.com/opendatalab/dsdl-sdk)

## get more dataset:
[opendatalab](https://opendatalab.com/)
"""
    save_path_p = Path(save_root_path)
    readme_new_path = save_path_p.joinpath("README.md")
    if not readme_new_path.exists():
        with open(str(readme_new_path), 'w', encoding='utf-8') as fp:
            fp.write(readme_str)
    else:
        print("README.md already exists.")
