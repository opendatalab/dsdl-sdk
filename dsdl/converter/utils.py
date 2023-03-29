import re
import os
import json
from pathlib import Path
import networkx as nx
import yaml
import numpy as np
from skimage import measure
from pycocotools import mask as mask_util
import xml.etree.ElementTree as ET


DSDL_TASK_NAMES_TEMPLATE = {
    "Image Classification": "class_template",
    "Object Detection": "detection_template",
    "Semantic Segmentation": None,
    "Instance Segmentation": None,
    "Panoptic Segmentation": None,
    "Keypoint Detection": None,
    "Multi-Object Tracking": None,
    "Single-Object Tracking": None,
    "Image Generation": None,
    "Optical Character Recognition": None,
    "Rotated Object Detection": None,
}

DSDL_MODALITYS = ("Images", "Texts", "Videos", "Audio", "3D")

DSDL_META_KEYS = ("Dataset Name", "HomePage", "Modality", "Task", "Subset Name")

def load_yaml(yaml_path):
    try:
        with open(yaml_path, 'r', encoding='utf-8') as fp:
            data = yaml.load(fp, yaml.FullLoader)
            return data
    except:
        return None

def load_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            return data
    except:
        return None

def load_text(text_path):
    try:
        with open(text_path, 'r', encoding='utf-8') as fp:
            for line in fp:
                line_str = line.strip()
                yield line_str
    except:
        return None

def bbox_xymin_xymax_to_xymin_w_h(bbox_value):
    bbox_result = None
    if len(bbox_value) == 4:
        xmin = float(bbox_value[0])
        ymin = float(bbox_value[1])
        xmax = float(bbox_value[2])
        ymax = float(bbox_value[3])
        width = xmax - xmin
        height = ymax - ymin
        bbox_result = [xmin, ymin, width, height]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def bbox_xymin_w_h_to_xymin_xymax(bbox_value):
    bbox_result = None
    if len(bbox_value) == 4:
        xmin = float(bbox_value[0])
        ymin = float(bbox_value[1])
        width = float(bbox_value[2])
        height = float(bbox_value[3])
        xmax = xmin + width
        ymax = ymin + height
        bbox_result = [xmin, ymin, xmax, ymax]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def bbox_xycenter_w_h_to_xymin_w_h(bbox_value):
    bbox_result = None
    if len(bbox_value) == 4:
        x_center = float(bbox_value[0])
        y_center = float(bbox_value[1])
        width = float(bbox_value[2])
        height = float(bbox_value[3])
        xmin = x_center - (width/2)
        ymin = y_center - (height/2)
        bbox_result = [xmin, ymin, width, height]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def bbox_xycenter_w_h_normal_to_xymin_w_h(bbox_value, image_width, image_height):
    bbox_result = None
    if len(bbox_value) == 4:
        x_center = float(bbox_value[0]) * float(image_width)
        y_center = float(bbox_value[1]) * float(image_height)
        width = float(bbox_value[2]) * float(image_width)
        height = float(bbox_value[3]) * float(image_height)
        xmin = x_center - (width/2)
        ymin = y_center - (height/2)
        bbox_result = [xmin, ymin, width, height]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def bbox_xymin_w_h_to_xycenter_w_h(bbox_value):
    bbox_result = None
    if len(bbox_value) == 4:
        xmin = float(bbox_value[0])
        ymin = float(bbox_value[1])
        width = float(bbox_value[2])
        height = float(bbox_value[3])
        x_center = xmin + (width/2)
        y_center = ymin + (height/2)
        bbox_result = [x_center, y_center, width, height]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def bbox_xymin_w_h_to_xycenter_w_h_normal(bbox_value, image_width, image_height):
    bbox_result = None
    if len(bbox_value) == 4:
        xmin = float(bbox_value[0])
        ymin = float(bbox_value[1])
        width = float(bbox_value[2])
        height = float(bbox_value[3])

        x_center = xmin + (width/2)
        y_center = ymin + (height/2)
        dw = 1/float(image_width)
        dh = 1/float(image_height)
        
        x_center *= dw
        y_center *= dh
        width *= dw
        height *= dh
        bbox_result = [x_center, y_center, width, height]
    else:
        raise ValueError(f"bbox_value length should be 4.")
    return bbox_result

def replace_special_characters(str_in):
    str_out = re.sub("\W", "_", str_in)
    return str_out

def annToRLE(ann, img_height, img_width):
        """
        Convert annotation which can be polygons, uncompressed RLE to RLE.
        :return: binary mask (numpy 2D array)
        """
        h, w = img_height, img_width
        segm = ann['segmentation']
        if type(segm) == list:
            # polygon -- a single object might consist of multiple parts
            # we merge all parts into one mask rle code
            rles = mask_util.frPyObjects(segm, h, w)
            rle = mask_util.merge(rles)
        elif type(segm['counts']) == list:
            # uncompressed RLE
            rle = mask_util.frPyObjects(segm, h, w)
        else:
            # rle
            rle = ann['segmentation']
        return rle

def annToMask(ann, h, w):
    """
    Convert annotation which can be polygons, uncompressed RLE, or RLE to binary mask.
    :return: binary mask (numpy 2D array)
    """
    rle = annToRLE(ann, h, w)
    m = mask_util.decode(rle)
    return m

def mask2polygon(mask):
    # fortran_ground_truth_binary_mask = np.asfortranarray(mask)
    # encoded_ground_truth = mask_util.encode(fortran_ground_truth_binary_mask)
    # ground_truth_area = mask_util.area(encoded_ground_truth)
    # ground_truth_bounding_box = mask_util.toBbox(encoded_ground_truth)
    contours = measure.find_contours(mask, 0.5)
    segmentations = []
    for contour in contours:
        contour = np.flip(contour, axis=1)
        if contour.size > 6:
            segmentation = contour.ravel().tolist()
            segmentations.append(segmentation)
    return segmentations

def rle2polygon(ann, img_height, img_width):
    curr_mask = annToMask(ann, img_height, img_width)
    curr_polygon = mask2polygon(curr_mask)
    result = []
    for k, v in enumerate(curr_polygon):
        curr_v = np.array(v).reshape(-1,2).tolist()
        result.append(curr_v)
    return result

def generate_class_dom(dsdl_root_path, names_list, class_dom_name="ClassDom"):
    # 这里可以调用某个函数获取版本号
    dsdl_version="0.5.3"
    if not class_dom_name:
        raise ValueError(f"The class-dom name is {class_dom_name}, please specify the correct class-dom name !")
    if len(names_list) == 0:
        raise ValueError("The class-dom's value of names_list is an empty list, please specify the correct name_list !")
    save_path_p = Path(dsdl_root_path)
    save_defs_p = save_path_p.joinpath("defs")
    if not save_defs_p.exists():
        os.makedirs(save_defs_p)

    class_dom_path = save_defs_p.joinpath("class-dom.yaml")
    if not class_dom_path.exists():
        code_str = f'$dsdl-version: \"{dsdl_version}\"\n\n'
        code_str += f'{class_dom_name}:\n'
        code_str += "    $def: class_domain\n"
        code_str += "    classes:\n"
        for cname in names_list:
            code_str += f"        - {cname}\n"
        with open(class_dom_path, "w", encoding='utf-8') as fp1:
            fp1.write(code_str)
    else:
        print(f"{class_dom_path} already exists !")
    print("class_dom.yaml 已经生成")

def generate_global_info(dsdl_root_path, class_info_list):
    if len(class_info_list) == 0:
        raise ValueError("The class_info_list is an empty list, please specify the correct class_info_list !")
    
    save_path_p = Path(dsdl_root_path)
    save_defs_p = save_path_p.joinpath("defs")
    if not save_defs_p.exists():
        os.makedirs(save_defs_p)

    global_info_path = save_defs_p.joinpath("global-info.json")
    if not global_info_path.exists():
        result_dict = {}
        result_dict["global-info"] = {"class_info": class_info_list}
        with open(global_info_path, "w", encoding="utf-8") as fp:
            json.dump(result_dict, fp, indent=4)
    else:
        print(f"The {global_info_path} already exists !")

def get_dsdl_template_file_name(dsdl_root_path):
    save_path_p = Path(dsdl_root_path)
    save_defs_p = save_path_p.joinpath("defs")
    if not save_defs_p.exists():
        raise FileNotFoundError(f"{save_defs_p} not exists !")
    template_file = ""
    for item_file in save_defs_p.iterdir():
        if item_file.suffix == ".yaml":
            if item_file.name == "class-dom.yaml" or item_file.name == "global-info.yaml":
                continue
            else:
                template_file = item_file.name
    return template_file

def get_subset_yaml_str(meta_info, template_file_name, sample_struct_name, class_dom_name, dsdl_version):
    dataset_name = meta_info["Dataset Name"]
    homepage = meta_info["HomePage"]
    subset_name = meta_info["Subset Name"]
    task_name = meta_info["Task"]
    mod_name = meta_info["Modality"]
    template_file_name = template_file_name.replace(".yaml", "")
    yaml_str = f'$dsdl-version: \"{dsdl_version}\"\n\n'
    yaml_str += '$import:\n'
    yaml_str += '  - ../defs/class-dom\n'
    yaml_str += f'  - ../defs/{template_file_name}\n\n'
    yaml_str += 'meta:\n'
    yaml_str += f'  Dataset Name: \"{dataset_name}\"\n'
    yaml_str += f'  HomePage: \"{homepage}\"\n'
    yaml_str += f'  Subset Name: \"{subset_name}\"\n'
    yaml_str += f'  Modality: \"{mod_name}\"\n'
    yaml_str += f'  Task: \"{task_name}\"\n\n'
    yaml_str += 'data:\n'
    yaml_str += f'  sample-type: {sample_struct_name}[cdom={class_dom_name}]\n'
    yaml_str += f'  sample-path: {subset_name}_samples.json\n'
    return yaml_str

def generate_subset_yaml_and_json(meta_dict, dsdl_root_path, samples_list):
    save_path_p = Path(dsdl_root_path)
    sub_name = meta_dict['Subset Name']
    curr_subdir = f"set-{sub_name}"
    save_subset_p = save_path_p.joinpath(curr_subdir)
    if not save_subset_p.exists():
        os.makedirs(save_subset_p)

    sub_yaml_file_name = f"{sub_name}.yaml"
    sub_yaml_path = save_subset_p.joinpath(sub_yaml_file_name)
    sub_sample_json_path = save_subset_p.joinpath(f"{sub_name}_samples.json")

    template_file_name = get_dsdl_template_file_name(dsdl_root_path)
    if not template_file_name:
        raise FileNotFoundError("The task template file is missing .")
    
    sample_struct_name = get_dsdl_sample_struct_name(dsdl_root_path)
    class_dom_name = get_dsdl_class_dom_name(dsdl_root_path)
    
    # 这里可以调用某个函数获取版本号
    dsdl_version="0.5.3"
    yaml_str = get_subset_yaml_str(meta_dict, template_file_name, sample_struct_name, class_dom_name, dsdl_version)
    if not sub_yaml_path.exists():
        with open(sub_yaml_path, "w", encoding='utf-8') as fp1:
            fp1.write(yaml_str)
    
    samples_result = {"samples": samples_list}
    with open(sub_sample_json_path, "w", encoding="utf-8") as fp:
        json.dump(samples_result, fp, indent=4)

def parse_xml_det_task(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    sample_dict = {}
    object_list = []
    
    size_node = root.find("size")
    sample_dict["width"] = int(size_node.find("width").text)
    sample_dict["height"] = int(size_node.find("height").text)
    sample_dict["depth"] = int(size_node.find("depth").text)

    object_node_list = root.findall("object")
    for obj_node in object_node_list:
        curr_obj_dict = {}
        name = obj_node.find("name").text
        curr_obj_dict["name"] = name
        
        bndbox_node = obj_node.find("bndbox")
        xmin = float(bndbox_node.find("xmin").text)
        xmax = float(bndbox_node.find("xmax").text)
        ymin = float(bndbox_node.find("ymin").text)
        ymax = float(bndbox_node.find("ymax").text)
        bndbox_value = [xmin, ymin, xmax, ymax]
        curr_obj_dict["bndbox"] = bndbox_value

        difficult = obj_node.find("difficult")
        occluded = obj_node.find("occluded")
        truncated = obj_node.find("truncated")  
        pose = obj_node.find("pose")  
        if difficult is not None:
            curr_obj_dict["difficult"] = int(difficult.text)
        if occluded is not None:
            curr_obj_dict["occluded"] = int(occluded.text)
        if truncated is not None:
            curr_obj_dict["truncated"] = int(truncated.text)
        if pose is not None:
            curr_obj_dict["pose"] = pose.text
        object_list.append(curr_obj_dict)
    sample_dict["objects"] = object_list
    return sample_dict

def check_dsdl_meta_info(meta_info_in):
    if isinstance(meta_info_in, dict):
        meta_keys_set = set(DSDL_META_KEYS)
        curr_meta_keys_set = set(meta_info_in.keys())
        if curr_meta_keys_set.issubset(meta_keys_set):
            if not meta_info_in["Dataset Name"]:
                raise ValueError(f"Dataset Name is null, please specify the dataset name !")
            if meta_info_in["Modality"] not in DSDL_MODALITYS:
                raise ValueError(f"DSDL Modality' value must in {DSDL_MODALITYS}, but current value is {meta_info_in['Modality']}")
            if meta_info_in["Task"] not in DSDL_TASK_NAMES_TEMPLATE:
                raise ValueError(f"Task value must in {DSDL_TASK_NAMES_TEMPLATE}, but current value is {meta_info_in['Task']}")
        else:
            raise ValueError(f"meta_info_in's keys must in {DSDL_META_KEYS}, but current keys is {curr_meta_keys_set}")
    else:
        raise TypeError("The param meta_info_in's type must be dict !")

def check_task_template_file(dsdl_root_path):
    template_name = get_dsdl_template_file_name(dsdl_root_path)
    if not template_name:
        raise FileNotFoundError(f"The task template file is missing .")

def struct_sort(struct_dict_in):
    digraph_obj = nx.DiGraph()
    struct_names = list(struct_dict_in.keys())
    digraph_obj.add_nodes_from(struct_names)
    for s_name, s_value in struct_dict_in.items():
        s_fields_values = list(s_value["$fields"].values())
        for field_value in s_fields_values:
            for k in struct_names:
                if k in field_value:
                    digraph_obj.add_edge(k, s_name)            
    if not nx.is_directed_acyclic_graph(digraph_obj):
        raise "define cycle found."
    ordered_struct_name = list(nx.topological_sort(digraph_obj))
    return ordered_struct_name

def get_dsdl_sample_struct_name(dsdl_root_path):
    save_path_p = Path(dsdl_root_path)
    save_defs_p = save_path_p.joinpath("defs")
    template_name = get_dsdl_template_file_name(dsdl_root_path)
    if not template_name:
        raise FileNotFoundError("The task template file is missing .")
    template_path_p = save_defs_p.joinpath(template_name)
    curr_data = load_yaml(str(template_path_p))
    del curr_data["$dsdl-version"]
    order_names = struct_sort(curr_data)
    return order_names[-1]

def get_dsdl_class_dom_name(dsdl_root_path):
    save_path_p = Path(dsdl_root_path)
    save_defs_p = save_path_p.joinpath("defs")
    class_dom_path = save_defs_p.joinpath("class-dom.yaml")
    curr_data = load_yaml(str(class_dom_path))
    class_dom_name = ""
    if len(curr_data.keys()) == 2:
        for item_name in curr_data.keys():
            if item_name == "$dsdl-version":
                continue
            else:
                class_dom_name = item_name
    else:
        raise ValueError(f"class-dom.yaml中出现多个类域名称。")
    return class_dom_name
