import re
import networkx as nx
from typing import Dict, List
from jsonmodels import models, fields, validators
import keyword
from dsdl.exception import ValidationError


TYPES_WITHOUT_PARS = [
    "Bool",
    "Num",
    "Int",
    "Str",
    "Coord",
    "Coord3D",
    "Interval",
    "BBox",
    "Polygon",
    "Image",
    "InstanceMap",
    "Video",
    "Dict",
    "Text",
    "InstanceID",
]
TYPES_TIME = ["Date", "Time"]
TYPES_LABEL = ["Label", "LabelMap", "Keypoint"]
TYPES_LIST = ["List"]
TYPES_IMAGE_SHAPE = ["ImageShape"]
TYPES_ROTATED_BBOX = ["RotatedBBox"]
TYPES_ALL = TYPES_WITHOUT_PARS + TYPES_TIME + TYPES_LABEL + TYPES_LIST + TYPES_IMAGE_SHAPE + TYPES_ROTATED_BBOX


class CheckLogItem(models.Base):
    def_name = fields.StringField(required=True, validators=validators.Enum("class_domain", "struct", "all"))
    yaml = fields.StringField(nullable=True)
    flag = fields.IntField(required=True, validators=validators.Enum(0, 1), default=0)  # 0:error, 1: right
    msg = fields.StringField(nullable=True)


class CheckLog(models.Base):
    def_name = fields.StringField(required=True, validators=validators.Enum("class_domain", "struct", "all"))
    flag = fields.IntField(required=True, validators=validators.Enum(0, 1), default=0)  # 0:error, 1: right
    sub_struct = fields.ListField([CheckLogItem], nullable=True)


def sanitize_variable_name(varstr: str) -> str:
    """
    1. 将`.`替换为`__` 2.将（非字母开头）和（非字母数字及下划线）替换为`_`
    eg. apple.fruit_and_vegetables会转化为apple__fruit_and_vegetables
    """
    temp = varstr.split(".")
    temp = [re.sub("\W|^(?=\d)", "_", i) for i in temp]
    temp = "__".join(temp)
    return temp


def check_name_format(varstr: str):
    if not varstr.isidentifier():
        err_msg = (
            f"`{varstr}` must be a a valid identifier. "
            f"[1. `Struct` name 2. `Class domain` name 3.name of `$field` in `Struct`] "
            f"is considered a valid identifier if "
            f"it only contains alphanumeric letters (a-z) and (0-9), or underscores (_). "
            f"A valid identifier cannot start with a number, or contain any spaces."
        )
        raise ValidationError(f"{err_msg}")
    # 判断是否为python保留字
    if keyword.iskeyword(varstr):
        err_msg = (
            f"`{varstr}` can't be a Python keyword."
            f"check https://docs.python.org/3/reference/lexical_analysis.html#keywords "
            f"for more information."
        )
        raise ValidationError(err_msg)


def rreplace(s, old, new, occurrence):
    """
    从右向左的替换函数，类似replace,不过是反着的
    """
    li = s.rsplit(old, occurrence)
    return new.join(li)


def add_key_value_2_struct_field(field: str, key: str, value) -> str:
    """
    add key, value to field in struct,
    eg: key: optional, value: True, field: NumField(is_attr=True)
    return: NumField(optional=True, is_attr=True)
    """
    p = re.compile(r"[(](.*)[)]", re.S)  # 贪婪匹配
    k_v_list = re.findall(p, field)[0].strip()
    if k_v_list:
        k_v_list = k_v_list.split(",")
    else:
        k_v_list = []
    k_v_list.append(str(key) + "=" + str(value))
    temp = "(" + ", ".join(k_v_list) + ")"
    return field.replace("(" + re.findall(p, field)[0] + ")", temp)


def sort_nx(
    dict_sort_key: Dict[str, List[str]],
) -> List:
    """
    利用有向图对嵌套结构进行排序
    Args:
        dict_sort_key： {当前节点：[父节点],...}
    Returns: 排好序的节点的list，从父到子
    """
    define_graph = nx.DiGraph()
    define_graph.add_nodes_from(dict_sort_key.keys())
    for key, val in dict_sort_key.items():
        for base in val:
            for k in dict_sort_key.keys():
                if k in base:
                    define_graph.add_edge(k, key)
    if not nx.is_directed_acyclic_graph(define_graph):
        raise "define cycle found."
    ordered_keys = list(nx.topological_sort(define_graph))
    return ordered_keys
