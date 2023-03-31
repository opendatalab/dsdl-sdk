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
    
    pointers = [tee] * (len(folders)+len(files_list) - 1) + [last]
    
    for pointer, path in zip(pointers[:len(folders)], folders):
        yield prefix + pointer + path
        if path == "...":
            continue
        extension = branch if pointer == tee else space 
        
        yield from generate_tree_generator(os.path.join(dir_path, path), prefix=prefix+extension, space=space, branch=branch, tee=tee, last=last, display_num=display_num)
    
    for pointer, path in zip(pointers[len(folders):], files_list):
        yield prefix + pointer + path

def generate_tree_string(path_in):
    tree_str = ""
    tree_iter = generate_tree_generator(path_in)
    for line in tree_iter:
        tree_str += f"{line}\n"
    return tree_str

def generate_readme_without_middle_format(save_root_path, dataset_name, task_name, original_tree, dsdl_tree):
    readme_str = f"""# Data Set Description Language(DSDL) for {dataset_name} dataset

## Data Structure
Please make sure the folder structure of prepared dataset is organized as followed:

```
<dataset_root>
{original_tree}
```

The folder structure of dsdl annotation for {task_name} is organized as followed:

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
    working_dir="the prefix of the prepared dataset within the bucket")
```

Please change the 'access_key_secret', 'endpoint', 'access_key_id', 'bucket_name' and 'working_dir',
e.g. if the full path of your prepared dataset is "oss://bucket_name/dataset_name/prepared", then the working_dir should be "dataset_name/prepared".

## Related source:
1. Get more information about DSDL: [dsdl-docs](https://opendatalab.github.io/dsdl-docs/)
2. DSDL-SDK official repo: [dsdl-sdk](https://github.com/opendatalab/dsdl-sdk/)
3. Get more dataset: [OpenDataLab](https://opendatalab.com/)
"""
    save_path_p = Path(save_root_path)
    readme_new_path = save_path_p.joinpath("README.md")
    if not readme_new_path.exists():
        with open(str(readme_new_path), 'w', encoding='utf-8') as fp:
            fp.write(readme_str)
    else:
        print("README.md already exists.")

def generate_readme_with_middle_format(save_root_path, dataset_name, task_name, original_tree, dsdl_tree):
    readme_str = f"""# Data Set Description Language(DSDL) for {dataset_name} dataset

## prepare the dataset
To make sure the DSDL dataset for {task_name} run successfully, the tools/prepare.py should be executed. 
For this dataset, the following step will be selected to execute:
- decompress
- prepare dataset and generate DSDL annotation

There are four usage scenarios:
```
### decompress, convert
python tools/prepare.py <path_to_the_compressed_dataset_folder>

### decompress, copy and convert
python tools/prepare.py -c <path_to_the_compressed_dataset_folder>

### (already decompressed) copy and convert
python tools/prepare.py -d -c <path_to_the_decompressed_dataset_folder>

### (already decompressed) convert, directly overwrite
python tools/prepare.py -d <path_to_the_decompressed_dataset_folder>
```

For more messages, see [Dataset Prepare Section](https://opendatalab.github.io/dsdl-docs/tutorials/dataset_download/) in DSDL DOC, or use the help option:

```
python tools/prepare.py --help
```
    
## Data Structure
Please make sure the folder structure of prepared dataset is organized as followed:

```
<dataset_root>
{original_tree}
```

The folder structure of dsdl annotation for {task_name} is organized as followed:

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
    working_dir="the prefix of the prepared dataset within the bucket")
```

Please change the 'access_key_secret', 'endpoint', 'access_key_id', 'bucket_name' and 'working_dir',
e.g. if the full path of your prepared dataset is "oss://bucket_name/dataset_name/prepared", then the working_dir should be "dataset_name/prepared".

## Related source:
1. Get more information about DSDL: [dsdl-docs](https://opendatalab.github.io/dsdl-docs/)
2. DSDL-SDK official repo: [dsdl-sdk](https://github.com/opendatalab/dsdl-sdk/)
3. Get more dataset: [OpenDataLab](https://opendatalab.com/)
"""
    save_path_p = Path(save_root_path)
    readme_new_path = save_path_p.joinpath("README.md")
    if not readme_new_path.exists():
        with open(str(readme_new_path), 'w', encoding='utf-8') as fp:
            fp.write(readme_str)
    else:
        print("README.md already exists.")
