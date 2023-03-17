import warnings

import os
import re
import json
import click
import traceback
import networkx as nx
from yaml import load as yaml_load
from dataclasses import dataclass, field
from enum import Enum

from collections import defaultdict
from abc import ABC, abstractmethod
from typing import Optional, Set, Dict,Union
from typing import List as _List

# from petrel_client.client import Client
# conf_path = '~/petreloss.conf'
# client = Client(conf_path)

from .utils import *
from .parse_field import EleStruct, ParserField
from .parse_class import ParserClass, EleClass

# 先导入dsdl.fields这里FIELD才可以生效
from dsdl.fields import *
from dsdl.geometry import FIELD
from dsdl.exception import DefineSyntaxError, DSDLImportError
from dsdl.exception import ValidationError
from dsdl.warning import DuplicateDefineWarning, DefineSyntaxWarning

try:
    from yaml import CSafeLoader as YAMLSafeLoader
except ImportError:
    from yaml import SafeLoader as YAMLSafeLoader

CHECK_LOG = CheckLog(def_name="all", flag=0)

class Parser(ABC):
    """
    定义一个Parser的抽象基类（没法实例化的）：
    用处： 强制子类实现某些方法：写框架时常用。
    """

    @abstractmethod
    def _parse(self, data_file: str, library_path: str):
        """
        将yaml文件中的模型（struct）和标签(label)部分校验之后读入某个变量中
        """
        pass

    @abstractmethod
    def _generate(self) -> Optional[str]:
        """
        将内存里面的模型（struct）和标签(label)部分输出成ORM模型（python代码）
        """
        pass

    def process(self, data_file, library_path, output_file):
        self._parse(data_file, library_path)
        dsdl_py = self._generate()
        print(
            f"Convert Yaml File to Python Code Successfully!\n"
            f"Yaml file (source): {data_file}\n"
            f"Output file (output): {output_file}"
        )
        return dsdl_py


class TypeEnum(Enum):
    CLASS_DOMAIN = "class_domain"
    STRUCT = "struct"


@dataclass()
class StructORClassDomain:
    name: str
    type: TypeEnum = TypeEnum.STRUCT
    field_list: _List[Union[EleStruct, EleClass]] = field(default_factory=list)
    parent: _List[str] = None  # class_dom 特有的super category
    skeleton: _List[_List[int]] = None
    optional_list: _List[str] = None
    params: _List[str] = None

    def __post_init__(self):
        """
        按照规定struct和class dom的名字不能是白皮书中已经包含的类型名，如List这些内定的名字
        """
        if self.name in FIELD:
        #  or self.name in [i.replace("Field","") for i in FIELD]:
            raise ValidationError(
                f"{self.name} is dsdl build-in value name, please rename it."
                f"Build-in value names are: {','.join(FIELD)}."
            )
        
        check_name_format(self.name)



class DSDLParser(Parser, ABC):
    def __init__(self, report_flag: bool):
        self.struct_name = set()
        self.struct_name_params = defaultdict(list)
        self.define_map = defaultdict(StructORClassDomain)
        self.dsdl_version = None
        self.meta = dict()
        self.report_flag = report_flag

    def _parse(self, data_file: str, library_path: str):
        """
        将yaml文件中的模型（struct）和标签(label)部分校验之后读入变量self.define_map中
            input_file_list: 读入的yaml文件
        """
        ########################################################################################
        # 1. 校验train.yaml文件中必需的字段
        with open(data_file, "r") as f:
            desc = yaml_load(f, Loader=YAMLSafeLoader)

        # 校验必须有meta和$dsdl-version字段，见白皮书2.1
        try:
            self.dsdl_version = desc["$dsdl-version"]  # 存版本号，后续应该会使用（目前木有用）
        except KeyError as e:
            err_msg = f"data yaml must contains {e} section"
            if self.report_flag:
                temp_check_item = CheckLogItem(
                    def_name="all", msg=f"DefineSyntaxError: {err_msg}"
                )
                CHECK_LOG.sub_struct.append(temp_check_item)
                return
            raise DefineSyntaxError(err_msg)
        try:
            self.meta = desc["meta"]  # 存版meta信息，后续应该会使用（目前木有用）
        except KeyError as e:
            err_msg = f"data yaml must contains {e} section."
            if self.report_flag:
                temp_check_item = CheckLogItem(
                    def_name="all", msg=f"DefineSyntaxError: {err_msg}"
                )
                CHECK_LOG.sub_struct.append(temp_check_item)
                return
            raise DefineSyntaxError(err_msg)

        # 校验必须有data字段和data中的sample-type字段
        try:
            data_sample_type = desc["data"]["sample-type"]
        except KeyError as e:
            err_msg = (
                f"data yaml must contain `data` section and `data` section must have `sample-type`."
            )
            if self.report_flag:
                temp_check_item = CheckLogItem(
                    def_name="all", msg=f"DefineSyntaxError: {err_msg}"
                )
                CHECK_LOG.sub_struct.append(temp_check_item)
                return
            raise DefineSyntaxError(err_msg)

        # 校验必须有data字段和data中的sample-type字段
        try:
            global_info_type = desc["data"]["global-info-type"]
        except KeyError as e:
            warning_msg = f"{e}, `global-info-type` is not defined."
            if self.report_flag:
                temp_check_item = CheckLogItem(
                    def_name="all", msg=f"DefineSyntaxWarning: {warning_msg}"
                )
                CHECK_LOG.sub_struct.append(temp_check_item)
            warnings.warn(warning_msg, DefineSyntaxWarning)

        # import原则：优先import `-p`指定的路径，木有报错；如果`-p`木有指定，先import 本地路径，没有的话import dsdl/library路径
        import_list = []
        if "$import" in desc:
            _import = desc["$import"]
            if library_path:
                for p in _import:
                    # ceph仅能读取绝对路径，使用normpath和replace来规范
                    temp_p = os.path.normpath(os.path.join(library_path, p.strip() + ".yaml")).replace('s3:/','s3://')
                    if os.path.exists(temp_p):
                            import_list.append(temp_p)
                    else:
                        err_msg = (
                            f"{temp_p} does not exist, please check the path or give the right path using `-p`."
                        )
                        if self.report_flag:
                            temp_check_item = CheckLogItem(
                                def_name="all", msg=f"DSDLImportError: {err_msg}"
                            )
                            CHECK_LOG.sub_struct.append(temp_check_item)
                            return
                        raise DSDLImportError(err_msg)
            else:
                library_path = os.path.dirname(data_file)
                for p in _import:
                    temp_p = os.path.normpath(os.path.join(library_path, p.strip() + ".yaml")).replace('s3:/','s3://')
                    if os.path.exists(temp_p):
                        import_list.append(temp_p)
                    else:
                        temp_p = os.path.normpath(os.path.join(library_path+'/../defs/', p.strip() + ".yaml")).replace('s3:/','s3://')
                        print("temp_p:",temp_p)
                        if os.path.exists(temp_p):
                            import_list.append(temp_p)
                        else:
                            err_msg = (
                                f"{p} does not exist in neither `{library_path}` nor `defs/`, please check the path or give the right path using `-p`."
                            )
                            if self.report_flag:
                                temp_check_item = CheckLogItem(
                                    def_name="all", msg=f"DSDLImportError: {err_msg}"
                                )
                                CHECK_LOG.sub_struct.append(temp_check_item)
                                return
                            raise DSDLImportError(err_msg)

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

        ########################################################################################
        # 2. 校验train.yaml文件中import导入的文件，包括def.yaml、class-domain.yaml、global.yaml等
        for define_name, define_value in class_defi.items():
            if define_name.startswith("$"):
                continue
            try:
                define_type = define_value["$def"]
            except KeyError as e:
                err_msg = f"{define_name} section must contain {e} sub-section."
                if self.report_flag:
                    temp_check_item = CheckLogItem(
                        def_name="all", msg=f"DefineSyntaxError: {err_msg}"
                    )
                    CHECK_LOG.sub_struct.append(temp_check_item)
                    return
                raise DefineSyntaxError(err_msg)
            if define_type == "struct" or define_type == "class_domain":
                if define_name in self.struct_name:
                    err_msg = f"{define_name} has defined."
                    if self.report_flag:
                        temp_check_item = CheckLogItem(
                            def_name="all", msg=f"DuplicateDefineWarning: {err_msg}"
                        )
                        CHECK_LOG.sub_struct.append(temp_check_item)
                        return
                    raise DuplicateDefineWarning(err_msg)
                self.struct_name.add(define_name)
                self.struct_name_params[define_name] = define_value.get("$params", [])

        # loop for `class_defi` section，deal with each `struct` and `class_domain`
        for define_name, define_value in class_defi.items():
            if define_name.startswith("$"):
                # skip section like: $dsdl-version
                continue

            # each yaml file must contain '$def' section
            define_type = define_value["$def"]

            if define_type == "struct":
                # 判断struct名字是否符合规范
                try:
                    define_info = StructORClassDomain(name=define_name)
                except Exception as e:
                    if self.report_flag:
                            temp_check_item = CheckLogItem(
                                def_name=TypeEnum.STRUCT.value,
                                msg=f"Error in `{define_name}`, {e}",
                            )
                            CHECK_LOG.sub_struct.append(temp_check_item)
                            return
                    raise ValidationError(f"Error in `{define_name}`, {e}")
                define_info.type = TypeEnum.STRUCT
                struct_params = define_value.get("$params", [])
                FIELD_PARSER = ParserField(self.struct_name_params, self.struct_name,struct_params)
                field_list = dict()
                for raw_field in define_value["$fields"].items():
                    field_name = raw_field[0].strip()
                    field_type = raw_field[1].strip()
                    # 判断field_name是否为python保留字和是符合命名规范
                    try:
                        check_name_format(field_name)
                    except ValidationError as e:
                        if self.report_flag:
                            temp_check_item = CheckLogItem(
                                def_name=TypeEnum.STRUCT.value,
                                msg=f"Error in `{define_name}`, {e}",
                            )
                            CHECK_LOG.sub_struct.append(temp_check_item)
                            return
                        raise ValidationError(f"Error in `{define_name}`, {e}")

                    try:
                        field_list[field_name] = FIELD_PARSER.pre_parse_struct_field(field_name, field_type)
                    except Exception as e:
                        if self.report_flag:
                            temp_check_item = CheckLogItem(
                                def_name=TypeEnum.STRUCT.value, msg=f"{e}"
                            )
                            CHECK_LOG.sub_struct.append(temp_check_item)
                            return
                        raise Exception(e)
                # deal with `$optional` section after `$fields` section，
                # because we must ensure filed in `$optional` is the `filed_name` in `$fields` section.
                temp = define_value.get("$optional", set())
                option_list = list(set(temp))
                # option_list = []
                # if "$optional" in define_value:
                #     temp = define_value.get("$optional", set())
                #     option_list = list(set(temp))

                define_info.field_list = field_list
                
                define_info.params = struct_params
                define_info.optional_list = option_list

            elif define_type == "class_domain":
                try:
                    if "skeleton" in define_value:
                        CLASS_PARSER = ParserClass(
                            define_name,
                            define_value["classes"],
                            define_value["skeleton"],
                        )
                    else:
                        CLASS_PARSER = ParserClass(define_name, define_value["classes"])
                except Exception as e:
                    if self.report_flag:
                        temp_check_item = CheckLogItem(
                            def_name=TypeEnum.CLASS_DOMAIN.value, msg=f"{e}"
                        )
                        CHECK_LOG.sub_struct.append(temp_check_item)
                        return
                    raise e
                define_info = StructORClassDomain(name=CLASS_PARSER.class_name)
                # verify each ele (in other words: each label) of `class_domain`, and save in define_info
                define_info.type = TypeEnum.CLASS_DOMAIN
                define_info.field_list = CLASS_PARSER.class_field
                # define_info.parent = CLASS_PARSER.super_class_list
                define_info.skeleton = CLASS_PARSER.skeleton
            else:
                err_msg = f"error type {define_type} in yaml, type must be class_domain or struct."
                if self.report_flag:
                    temp_check_item = CheckLogItem(
                        def_name=TypeEnum.CLASS_DOMAIN.value,
                        msg=f"DefineSyntaxError: {err_msg}",
                    )
                    CHECK_LOG.sub_struct.append(temp_check_item)
                    return
                raise DefineSyntaxError(err_msg)

            self.define_map[define_info.name] = define_info

        CHECK_LOG.flag = 1

    def _generate(self) -> Optional[str]:
        """
        将内存里面的模型（struct）和标签(label)部分输出成ORM模型（python代码）
        """
        # check define cycles. 如果有环形（就是循环定义）那是不行滴～
        # -------------------------------------------------------------,这里是否需要校验循环定义的情况
        define_graph = nx.DiGraph()
        define_graph.add_nodes_from(self.define_map.keys())
        for key, val in self.define_map.items():
            if val.type == TypeEnum.STRUCT:
                for fieldname in list(val.field_list.keys()):
                    for k in self.define_map.keys():
                        if k in val.field_list[fieldname]:
                            define_graph.add_edge(k, key)
        if not nx.is_directed_acyclic_graph(define_graph):
            err_msg = "define cycle found."
            if self.report_flag:
                temp_check_item = CheckLogItem(def_name="all", msg=f"{err_msg}")
                CHECK_LOG.sub_struct.append(temp_check_item)
                return
            raise err_msg

        dsdl_py = "# Generated by the dsdl parser. DO NOT EDIT!\n"
        dsdl_py += "from dsdl.geometry import ClassDomain\n"
        dsdl_py += "from dsdl.fields import *\n\n\n"
        # ordered_keys = list(nx.topological_sort(define_graph))
        # for idx, key in enumerate(ordered_keys):
        ordered_keys = list(nx.topological_sort(define_graph))
        for idx,key in enumerate(ordered_keys):
        # for key,val in self.define_map.items():
            val = self.define_map[key]
            if val.type == TypeEnum.STRUCT:
                dsdl_py += f"class {key}(Struct):\n"
                if val.params:
                    dsdl_py += f"""    __params__ = {val.params}\n"""
                if val.field_list:
                    dsdl_py += """    __fields__ = {\n"""
                    for field_name in val.field_list:
                        dsdl_py += f"""        "{field_name}": {val.field_list[field_name]},\n"""
                    dsdl_py += """    }\n"""
                if val.optional_list:
                    dsdl_py += f"""    __optional__ = {val.optional_list}\n"""
            if val.type == TypeEnum.CLASS_DOMAIN:
                dsdl_py += f"ClassDomain(\n"
                dsdl_py += f"""    name = "{key}",\n"""
                dsdl_py += "    classes = ["
                for ele_class in val.field_list:
                    dsdl_py += f""""{ele_class.label_value}","""
                dsdl_py += "],\n"
                if val.skeleton:
                    dsdl_py += f"""    skeleton = {val.skeleton}\n"""
                dsdl_py += ")\n"
            if idx != len(ordered_keys) - 1:
                dsdl_py += "\n\n"

        if self.report_flag:
            temp_check_item = CheckLogItem(
                def_name=TypeEnum.CLASS_DOMAIN.value,
                msg=f"success parser class dom",
                flag=1,
            )
            CHECK_LOG.sub_struct.append(temp_check_item)
            temp_check_item = CheckLogItem(
                def_name=TypeEnum.STRUCT.value, msg=f"success parser all strcut", flag=1
            )
            CHECK_LOG.sub_struct.append(temp_check_item)
            temp_check_item = CheckLogItem(
                def_name=TypeEnum.STRUCT.value,
                msg=f"success parser all parameters",
                flag=1,
            )
            CHECK_LOG.sub_struct.append(temp_check_item)
            CHECK_LOG.flag = 1
        return dsdl_py

    def process(
        self, data_file: str, library_path: str, output_file: str
    ) -> Optional[str]:
        self._parse(data_file, library_path)
        if self.report_flag and CHECK_LOG.flag:
            dsdl_py = self._generate()
        elif not self.report_flag:
            dsdl_py = self._generate()
        else:
            dsdl_py = None
            print('dsdl_py is None! The following is the specific log:\n')
            print(CHECK_LOG.to_struct())
        if dsdl_py:
            print(
                f"Convert Yaml File to Python Code Successfully!\n"
                f"Yaml file (source): {data_file}\n"
                f"Output file (output): {output_file}"
            )
            
        if output_file:
            with open(output_file, "w") as of:
                print(dsdl_py, file=of)
        return dsdl_py


def dsdl_parse(
    dsdl_yaml: str,
    dsdl_library_path: str = None,
    output_file: str = None,
    report_flag: bool = False,
) -> Optional[str]:
    """
    Main function of parser yaml files to .py dsdl struct definition code.

    Arguments:
        dsdl_yaml: file path of `data definition yaml file`;
        dsdl_library_path: file path of '`$import` path' in `dsdl_yaml` file.
        output_file: output file path. if None, return string, else, generate .py file in output file path.
        report_flag: if return report

    Returns:
        Optional[str]: if output_file=None, return string of dsdl definition .py file;
                       else generate a .py file in `output_file` path.
    """
    dsdl_parser = DSDLParser(report_flag)
    res = dsdl_parser.process(dsdl_yaml, dsdl_library_path, output_file)
    return res

def check_dsdl_parser(
    dsdl_yaml: str,
    dsdl_library_path: str = None,
    output_file: str = None,
    report_flag: bool = False,
):
    dsdl_py = dsdl_parse(
        dsdl_yaml=dsdl_yaml,
        dsdl_library_path=dsdl_library_path,
        output_file=output_file,
        report_flag=report_flag,
    )
    res = {"dsdl_py": dsdl_py}
    if report_flag:
        res["check_log"] = json.dumps(CHECK_LOG.to_struct())
    return res

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
)
def parse(dsdl_yaml: str, dsdl_library_path: str = None):
    """
    a separate cli tool function for user to parser yaml files to .py dsdl struct definition code.

    Arguments:
        dsdl_yaml: file path of `data definition yaml file`;
        dsdl_library_path: file path of '`$import` path' in `dsdl_yaml` file.

    Returns:
        None: generate a .py file in the same folder of `dsdl_yaml` file.
    """
    dsdl_name = os.path.splitext(os.path.basename(dsdl_yaml))[0]
    output_file = os.path.join(os.path.dirname(dsdl_yaml), f"{dsdl_name}.py")
    dsdl_parse(dsdl_yaml, dsdl_library_path, output_file)

# if __name__ == '__main__':
#     # parse()

#     # # 遍历方式获取dsdl数据集
#     url = 's3://odl-dsdl/dsdl/'
#     contents = client.list(url)
#     ann_files = []
#     for content in contents:
#         if content.endswith('/'):
#             for content1 in client.list(url+content):
#                 if content1.startswith('set'):
#                     for content2 in client.list(url+content+content1):
#                         if content2.endswith('yaml'):
#                             ann_files.append(url+content+content1+content2)
#                             # break
#                     # break
#         else:
#             print('object:', content)
#     # ann_files = open('new_parser/fail_parser.txt','r').readlines()
#     # ann_files = ['s3://odl-dsdl/dsdl/DIOR_RotDet_full/set-test/rotated_test.yaml']
#     print(f'dsdl数据集共{len(ann_files)}个')
#     ff = open('./new_parser/fail_parser.txt','w')
#     for i,ann_file in enumerate(ann_files):
#         dataset = ann_file.split('/')[4]
#         taskname = dataset.split('_')[-2]
#         datasetname = '_'.join(dataset.split('_')[:-2])
#         unique_name = ann_file.split('/')[-1].split('.')[0]
#         try:
#             dsdl_py = dsdl_parse(ann_file, dsdl_library_path=None,output_file=f'./new_parser/data/dsdl_new/{taskname}_{datasetname}_{unique_name}_new.py',report_flag=True)
#             exec(dsdl_py)
#             print('-----------------',i,dataset, 'exec success!')

#         except:
#             print (traceback.format_exc ())
#             print('-----------------',i,dataset, 'parser fail!', ann_file)

#             ff.write(ann_file+'\n')
#             ff.flush()
#     ff.close()

# 

    # pf = ParseField(set(['KeyPointLocalObject','ImageMedia','KeyPointSample']))
    # print(pf.pre_parse_struct_field(field_name=None, raw_field_type = 'Str[is_attr=True,List[etype=ImageMedia[cdom0=$cdom0],isoptional=True,arg1 = 1],arg2=2]'))
