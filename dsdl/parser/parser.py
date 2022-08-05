import click
from abc import ABC, abstractmethod
from yaml import load as yaml_load
from dsdl.exception import DefineSyntaxError
from dsdl.warning import DuplicateDefineWarning
import networkx as nx
import os
import re
from typing import List, Set
from collections import defaultdict
from .utils import *
from .parse_params import ParserParam, SingleStructParam

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader


class Parser(ABC):
    """
    定义一个Parser的抽象基类（没法实例化的）：
    用处： 强制子类实现某些方法：写框架时常用。
    """

    @abstractmethod
    def parse(self, input_file_list):
        """
        将yaml文件中的模型（struct）和标签(label)部分校验之后读入某个变量中
        """
        pass

    @abstractmethod
    def generate(self, output_file):
        """
        将内存里面的模型（struct）和标签(label)部分输出成ORM模型（python代码）
        """
        pass

    def process(self, data_file, library_path, output_file):
        self.parse(data_file, library_path)
        self.generate(output_file)
        print(
            f"Convert Yaml File to Python Code Successfully!\n \
            Yaml file (source): {data_file}\n \
            Output file (output): {output_file}"
        )


class DSDLParser(Parser):
    def __init__(self):
        self.define_map = dict()
        self.TYPES_WITHOUT_PARS = [
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
            "Dict",
        ]
        self.TYPES_WITH_PARS = ["Date", "Label", "Time"]
        self.TYPES_WITH_PARS_SP = ["List"]
        self.dsdl_version = None
        self.meta = dict()
        # eg. 对于：sample-type: SceneAndObjectSample[scenedom=SceneDom, objectdom=ObjectDom]， 就是SceneAndObjectSample
        self.data_sample_type = None
        # # eg. {SceneAndObjectSample:{scenedom: SceneDom, objectdom: ObjectDom}}
        # self.sample_param_map = defaultdict(dict)
        # # eg. {SceneAndObjectSample:{$parent:[](父类只能有一个或为空),scenedom: None, objectdom: None},
        # #  LocalObjectEntry:{$parent:[SceneAndObjectSample], cdom:None}}
        # self.general_param_map = defaultdict(dict)

    def parse(self, data_file: str, library_path: str):
        """
        将yaml文件中的模型（struct）和标签(label)部分校验之后读入变量self.define_map中
            input_file_list: 读入的yaml文件
        """
        with open(data_file, "r") as f:
            desc = yaml_load(f, Loader=YAMLSafeLoader)

        # 校验必须有meta和$dsdl-version字段，见白皮书2.1
        try:
            self.dsdl_version = desc["$dsdl-version"]  # 存版本号，后续应该会使用（目前木有用）
        except KeyError as e:
            raise DefineSyntaxError(f"data yaml must contains {e} section")
        try:
            self.meta = desc["meta"]  # 存版meta信息，后续应该会使用（目前木有用）
        except KeyError as e:
            raise DefineSyntaxError(f"data yaml must contains {e} section")

        # 校验必须有data字段和data中的sample-type字段
        try:
            data_sample_type = desc["data"]["sample-type"]
        except KeyError as e:
            raise DefineSyntaxError(f"data yaml must contains {e} in `data` section")

        if "$import" in desc:
            import_list = desc["$import"]
            import_list = [
                os.path.join(library_path, p.strip() + ".yaml") for p in import_list
            ]
        else:
            import_list = []
        if "defs" in desc:
            # 获取yaml中模型（struct）和标签(label)部分的内容，存储在变量class_defi中，
            # 因为有不同格式的yaml(数据和模型放同一个yaml中或者分开放)，所以用if...else分别做处理
            # 注意区分这个root_class_defi,为啥要把他先存好？如果import的yaml中，有重复的模型，需要用它覆盖，参见白皮书2.5.1
            root_class_defi = desc["defs"].items()
            self.dsdl_version = desc["$dsdl-version"]  # 存版本号，后续应该会使用（目前木有用）
        else:
            root_class_defi = dict()

        import_desc = dict()
        for input_file in import_list:
            with open(input_file, "r") as f:
                import_desc.update(yaml_load(f, Loader=YAMLSafeLoader))

        if "defs" in import_desc:
            # 获取yaml中模型（struct）和标签(label)部分的内容，存储在变量class_defi中，
            # 因为有不同格式的yaml(数据和模型放同一个yaml中或者分开放)，所以用if...else分别做处理
            class_defi = import_desc["defs"]
        else:
            class_defi = import_desc
        # root_class_defi是数据yaml里面定义的模型，如果和import里面的重复了，会覆盖掉前面import的。参见白皮书2.5.1
        class_defi.update(root_class_defi)

        # self.general_param_map = self.get_params(class_defi)
        # 获取 self.data_sample_type和self.sample_param_map
        PARAMS = ParserParam(data_type=data_sample_type, struct_defi=class_defi)

        # 对class_defi循环，处理里面的每一个struct或者label(class_domain)
        for define_name, define_value in class_defi.items():
            if not define_name.isidentifier():
                continue  # 类似$dsdl-version就会continue掉
            if define_name in self.define_map:
                DuplicateDefineWarning(f"{define_name} has defined.")

            # 每个定义的数据结构里面必须有$def
            try:
                define_type = define_value["$def"]
            except KeyError as e:
                raise DefineSyntaxError(
                    f"{define_name} section must contains {e} sub-section"
                )

            define_info = {"name": define_name}
            if define_type == "struct":
                # 对class_defi中struct类型的ele做校验并存入define_info
                define_info["type"] = "struct"
                struct_params = define_value.get("$params", None)
                # struct_params = self.validate_params(set(struct_params), define_name)
                field_list = dict()
                define_info["field_list"] = []
                for raw_field in define_value["$fields"].items():
                    field_name = raw_field[0].replace(" ", "")
                    field_type = raw_field[1].replace(" ", "")
                    if not field_name.isidentifier():
                        continue
                    if struct_params:
                        for param, value in PARAMS.general_param_map[define_name].params_dict.items():
                            field_type = field_type.replace("$" + param, value)
                    field_list[field_name] = {
                        "name": field_name,
                        "type": self.parse_struct_field(field_type),
                    }
                # $optional字段在$fields字段之后处理，因为需要判断optional里面的字段必须是field字段里面的filed_name
                if "$optional" in define_value:
                    for optional_name in define_value["$optional"]:
                        if optional_name in field_list:
                            temp_type = field_list[optional_name]["type"]
                            temp_type = add_key_value_2_struct_field(
                                temp_type, "optional", True
                            )
                            field_list[optional_name]["type"] = temp_type
                        else:
                            raise DefineSyntaxError(f"{optional_name} is not in $field")
                # 得到处理好的struct的field字段
                define_info["field_list"] = list(field_list.values())

            if define_type == "class_domain":
                # 对class_defi中class_domain类型的ele（也就是定义的label）做校验并存入define_info
                define_info["type"] = "class_domain"
                define_info["class_list"] = []
                for class_name in define_value["classes"]:
                    define_info["class_list"].append(
                        {
                            "name": sanitize_variable_name(class_name),
                        }
                    )

            self.define_map[define_info["name"]] = define_info

    def generate(self, output_file):
        """
        将内存里面的模型（struct）和标签(label)部分输出成ORM模型（python代码）
        """
        # check define cycles. 如果有环形（就是循环定义）那是不行滴～
        define_graph = nx.DiGraph()
        define_graph.add_nodes_from(self.define_map.keys())
        for key, val in self.define_map.items():
            if val["type"] != "struct":
                continue
            for field in val["field_list"]:
                for k in self.define_map.keys():  # MyEntry
                    if k in field["type"]:
                        define_graph.add_edge(k, key)
        if not nx.is_directed_acyclic_graph(define_graph):
            raise "define cycle found."

        with open(output_file, "w") as of:
            print("# Generated by the dsdl parser. DO NOT EDIT!\n", file=of)
            print(
                "from dsdl.types import *\nfrom enum import Enum, unique\n\n", file=of
            )
            ordered_keys = list(nx.topological_sort(define_graph))
            for idx, key in enumerate(ordered_keys):
                val = self.define_map[key]
                if val["type"] == "struct":
                    print(f"class {key}(Struct):", file=of)
                    for field in val["field_list"]:
                        print(f"""    {field["name"]} = {field["type"]}""", file=of)
                if val["type"] == "class_domain":
                    print("@unique", file=of)
                    print(f"class {key}(Enum):", file=of)
                    for class_id, item in enumerate(val["class_list"], start=1):
                        class_name = item["name"]
                        print(f"""    {class_name.lower()} = {class_id}""", file=of)
                if idx != len(ordered_keys) - 1:
                    print("\n", file=of)


    def parse_list_filed(self, raw: str) -> str:
        """
        解析处理List类型的field
        """

        def sanitize_etype(val: str) -> str:
            """
            验证List类型中的etype是否存在（必须存在）且是否为合法类型
            """
            return self.parse_struct_field(val)

        def all_subclasses(cls):
            """
            返回某个类的所有子类：like[<class '__main__.Bar'>, <class '__main__.Baz'>...]
            """
            return cls.__subclasses__() + [
                g for s in cls.__subclasses__() for g in all_subclasses(s)
            ]

        def sanitize_ordered(val: str) -> str:
            if val.lower() in ["true", "false"]:
                if val.lower() == "true":
                    return "True"
                else:
                    return "False"
            else:
                raise DefineSyntaxError(
                    f"invalid value {val} in ordered of List {raw}."
                )

        field_type = "List"

        raw = rreplace(raw.replace(f"{field_type}[", "", 1), "]", "", 1)
        param_list = raw.split(",")
        ele_type, ordered = None, None
        if len(param_list) == 2:
            ele_type = param_list[0]
            ordered = param_list[1]
        elif len(param_list) == 1:
            ele_type = param_list[0]
        else:
            raise DefineSyntaxError(f"invalid parameters {raw} in List.")

        ele_type = ele_type.split("=", 1)
        if len(ele_type) == 2:
            if ele_type[0].strip() != "etype":
                raise DefineSyntaxError(f"List types must contains parameters `etype`.")
            ele_type = ele_type[1]
            c_dom = re.findall(r"\[(.*)\]", ele_type)
            if c_dom:
                ele_type = ele_type.replace("[" + c_dom[0] + "]", "", 1).strip()
        else:
            ele_type = ele_type[0]
        # else:
        #     raise DefineSyntaxError(f"invalid parameters {raw} in List.")

        res = field_type + "Field("
        if ele_type:
            ele_type = sanitize_etype(ele_type)
            res += "ele_type=" + ele_type
        else:
            raise DefineSyntaxError(f"List types must contains parameters `etype`.")
        if ordered:
            ordered = ordered.split("=")[-1]
            ordered = sanitize_ordered(ordered)
            res += ", ordered=" + ordered
        return res + ")"

    @staticmethod
    def parse_struct_field_with_params(raw: str) -> str:
        """
        解析处理Label, Time, Date类型的field
        """

        def sanitize_dom(val: str) -> str:
            """
            Label中对dom部分的校验，是用来严格限制特定格式或者字符。
            防止yaml里有一些异常代码注入到生成的Python 代码里被执行起来。
            """
            if not val.isidentifier():
                raise DefineSyntaxError(f"invalid dom: {val}")
            return val

        def sanitize_fmt(val: str) -> str:
            """
            Date, Time中对ftm部分的校验，是用来严格限制特定格式或者字符。
            防止yaml里有一些异常代码注入到生成的Python 代码里被执行起来。
            """
            val = val.strip("\"'")
            return f'"{val}"'

        field_map = {
            "Label": {"dom": sanitize_dom},
            "Date": {"fmt": sanitize_fmt},
            "Time": {"fmt": sanitize_fmt},
        }
        field_type = ""
        for k in field_map.keys():
            if raw.startswith(k):
                field_type = k
        if field_type == "":
            raise "Unknown field"

        raw = raw.replace(f"{field_type}[", "").replace("]", "")
        param_list = raw.split(",")
        valid_param_list = []
        for param in param_list:
            parts = param.split("=")
            # 需要考虑参数省略的情况，因为dom经常省略
            if len(parts) == 2:
                field_para = parts[0]
                field_var = parts[1]
            elif len(parts) == 1:
                field_para = next(iter(field_map[field_type]))
                field_var = parts[0]
            else:
                raise DefineSyntaxError(f"invalid parameters {raw} in List.")
            sanitized = field_map[field_type][field_para](field_var)
            valid_param_list.append(f"{field_para}={sanitized}")
        return field_type + "Field(" + ", ".join(valid_param_list) + ")"

    def parse_struct_field(self, raw_field_type: str) -> str:
        """
        校验struct类型的每个字段的入口函数，对不同情况（Int,Image,List...）的字段进行校验并读入内存。
            raw_field_type: like: Int, Image, Label[dom=MyClassDom], List[List[Int], ordered = True], ....
        """
        if raw_field_type in self.TYPES_WITHOUT_PARS:
            # 不带参数的不需要校验，直接可以转化为python代码（注意区分yaml中的模型部分到ORM的校验和通过ORM读入数据的校验，
            # 后者在dataset.py中定义，你脑子里想的Int也需要校验是数据的校验。）
            return raw_field_type + "Field()"
        elif raw_field_type.startswith(tuple(self.TYPES_WITH_PARS_SP)):
            # 带参数的Date, Time, Label类型的字段的校验
            return self.parse_list_filed(raw_field_type)
        elif raw_field_type.startswith(tuple(self.TYPES_WITH_PARS)):
            # 带参数的List类型的字段的校验
            # （因为List类型比较特殊，里面可以包含List，Label等各种其他字段，涉及递归，所以单独拿出来）
            return DSDLParser.parse_struct_field_with_params(raw_field_type)
        else:
            c_dom = re.findall(r"\[(.*)\]", raw_field_type)
            if c_dom:
                raw_field_type = raw_field_type.replace(
                    "[" + c_dom[0] + "]", "", 1
                ).strip()
            return raw_field_type + "()"
            # raise DefineTypeError(f"No type {raw_field_type} in DSDL.")


@click.command()
@click.option(
    "-y",
    "--yaml",
    "dsdl_yaml",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--path",
    "dsdl_library_path",
    type=str,
    default="dsdl/dsdl_library",
)
def parse(dsdl_yaml, dsdl_library_path):
    dsdl_name = os.path.splitext(os.path.basename(dsdl_yaml))[0]
    output_file = os.path.join(os.path.dirname(dsdl_yaml), f"{dsdl_name}.py")
    dsdl_parser = DSDLParser()
    dsdl_parser.process(dsdl_yaml, dsdl_library_path, output_file)
