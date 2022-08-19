import click
from abc import ABC, abstractmethod
from yaml import load as yaml_load
from dsdl.exception import DefineSyntaxError
from dsdl.warning import DuplicateDefineWarning
import networkx as nx
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set, Union
from collections import defaultdict
from .utils import *
from .parse_params import ParserParam
from .parse_field import ParserField, EleStruct
from .parse_class import ParserClass, EleClass

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
    def parse(self, data_file: str, library_path: str):
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


class TypeEnum(Enum):
    CLASS_DOMAIN = "class_domain"
    STRUCT = "struct"


@dataclass()
class StructORClassDomain:
    name: str
    type: TypeEnum = TypeEnum.STRUCT
    field_list: List[Union[EleStruct, EleClass]] = field(default_factory=list)


class DSDLParser(Parser):
    def __init__(self):
        self.define_map = defaultdict(StructORClassDomain)
        self.dsdl_version = None
        self.meta = dict()

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
            if define_name.startswith("$"):
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


            if define_type == "struct":
                define_info = StructORClassDomain(name=define_name)
                FIELD_PARSER = ParserField()
                # 对class_defi中struct类型的ele做校验并存入define_info
                define_info.type = TypeEnum.STRUCT
                struct_params = define_value.get("$params", None)
                # struct_params = self.validate_params(set(struct_params), define_name)
                field_list = dict()
                for raw_field in define_value["$fields"].items():
                    field_name = raw_field[0].replace(" ", "")
                    field_type = raw_field[1].replace(" ", "")
                    if not field_name.isidentifier():
                        continue
                    if struct_params:
                        for param, value in PARAMS.general_param_map[
                            define_name
                        ].params_dict.items():
                            field_type = field_type.replace("$" + param, value)
                    field_list[field_name] = EleStruct(
                        name = field_name,
                        type = FIELD_PARSER.pre_parse_struct_field(field_name, field_type),
                    )
                # $optional字段在$fields字段之后处理，因为需要判断optional里面的字段必须是field字段里面的filed_name
                if "$optional" in define_value or FIELD_PARSER.optional:
                    optional_set = set(define_value["$optional"]) | FIELD_PARSER.optional
                    for optional_name in optional_set:
                        if optional_name in field_list:
                            temp_type = field_list[optional_name].type
                            temp_type = add_key_value_2_struct_field(
                                temp_type, "optional", True
                            )
                            field_list[optional_name].type = temp_type
                        else:
                            raise DefineSyntaxError(f"{optional_name} is not in $field")
                for attr_name in FIELD_PARSER.is_attr:
                    temp_type = field_list[attr_name].type
                    temp_type = add_key_value_2_struct_field(
                        temp_type, "is_attr", True
                    )
                    field_list[attr_name].type = temp_type

                # 得到处理好的struct的field字段
                define_info.field_list = list(field_list.values())

            elif define_type == "class_domain":
                CLASS_PARSER = ParserClass(define_name, define_value["classes"])
                define_info = StructORClassDomain(name=CLASS_PARSER.class_name)
                # 对class_defi中class_domain类型的ele（也就是定义的label）做校验并存入define_info
                define_info.type = TypeEnum.CLASS_DOMAIN
                define_info.field_list = CLASS_PARSER.class_field
            else:
                raise DefineSyntaxError(f"error type {define_type} in yaml, type must be class_dom or struct.")

            self.define_map[define_info.name] = define_info

    def generate(self, output_file):
        """
        将内存里面的模型（struct）和标签(label)部分输出成ORM模型（python代码）
        """
        # check define cycles. 如果有环形（就是循环定义）那是不行滴～
        define_graph = nx.DiGraph()
        define_graph.add_nodes_from(self.define_map.keys())
        for key, val in self.define_map.items():
            if val.type != TypeEnum.STRUCT:
                continue
            for field in val.field_list:
                for k in self.define_map.keys():  # MyEntry
                    if k in field.type:
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
                if val.type == TypeEnum.STRUCT:
                    print(f"class {key}(Struct):", file=of)
                    for field in val.field_list:
                        print(f"""    {field.name} = {field.type}""", file=of)
                if val.type == TypeEnum.CLASS_DOMAIN:
                    print(f"class {key}(ClassDomain):", file=of)
                    print("    Classes = [", file=of)
                    for ele_class in val.field_list:
                        if ele_class.super_categories:
                            temp = ", ".join(ele_class.super_categories)
                            print(f"""        Label("{ele_class.label_value}", supercategories=[{temp}]),""", file=of)
                        else:
                            print(f"""        Label("{ele_class.label_value}"),""", file=of)
                    print("    ]", file=of)
                if idx != len(ordered_keys) - 1:
                    print("\n", file=of)


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
