from dsdl.exception import DefineSyntaxError, DefineTypeError
from .utils import *
from dataclasses import dataclass


@dataclass()
class EleStruct:
    name: str
    type: str


class ParserField:
    def __init__(self, struct_name):
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
        ]
        self.TYPES_TIME = ["Date", "Time"]
        self.TYPES_LABEL = ["Label"]
        self.TYPES_LIST = ["List"]
        self.TYPES_ALL = self.TYPES_WITHOUT_PARS + self.TYPES_TIME + self.TYPES_LABEL + self.TYPES_LIST
        self.is_attr = set()
        self.optional = set()
        self.struct = struct_name  # field 中包含的struct，后续校验用

    def parse_list_filed(self, field_name: str, field_type: str, param_list: List[str]) -> str:
        """
        解析处理List类型的field
        """

        def sanitize_etype(field_name, val: str) -> str:
            """
            验证List类型中的etype是否存在（必须存在）且是否为合法类型
            """
            return self.pre_parse_struct_field(field_name, val)

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
                    f"invalid value {val} in ordered of List {field_name}."
                )

        ele_type, ordered = None, None
        if len(param_list) == 2:
            ele_type = param_list[0].strip()
            ordered = param_list[1].strip()
        elif len(param_list) == 1:
            ele_type = param_list[0].strip()
        else:
            raise DefineSyntaxError(f"invalid parameters {param_list} in List.")

        if ele_type.startswith("etype"):
            # if ele_type like "etype=LocalObjectEntry[cdom=$objectdom]", split by "="
            # else if ele_type like "LocalObjectEntry[cdom=$objectdom]", do nothing.
            ele_type = ele_type.split("=", 1)
            if len(ele_type) == 2:
                if ele_type[0].strip() != "etype":
                    raise DefineSyntaxError(f"List types must contains parameters `etype`.")
                ele_type = ele_type[1].strip()
            else:
                raise DefineSyntaxError(f"invalid parameters {', '.join(param_list)} in {field_type} {field_name}.")

        res = field_type + "Field("
        if ele_type:
            ele_type = sanitize_etype(field_name, ele_type)
            res += "ele_type=" + ele_type
        else:
            raise DefineSyntaxError(f"List types must contains parameters `etype`.")
        if ordered:
            ordered = ordered.split("=")[-1]
            ordered = sanitize_ordered(ordered)
            res += ", ordered=" + ordered
        return res + ")"

    @staticmethod
    def parse_time_field(field_type: str, param_list: List[str]) -> str:
        """
        解析处理Time, Date类型的field
        """

        def sanitize_fmt(val: str) -> str:
            """
            Date, Time中对ftm部分的校验，是用来严格限制特定格式或者字符。
            防止yaml里有一些异常代码注入到生成的Python 代码里被执行起来。
            """
            val = val.strip("\"'")
            return f'"{val}"'

        param_dict = dict()
        for param in param_list:
            parts = param.split("=")
            parts = [i.strip() for i in parts]
            # 需要考虑参数省略的情况，因为dom经常省略
            if len(parts) == 2:
                field_para = parts[0]
                field_var = parts[1]
            elif len(parts) == 1:
                field_para = "fmt"
                field_var = parts[0]
            else:
                raise DefineSyntaxError(f"invalid parameters {param} in {field_type}.")

            if field_para != "fmt":
                raise DefineSyntaxError(
                    f"invalid parameters {field_para} in {field_type}."
                )

            if field_para in param_dict:
                raise ValueError(f"duplicated param {param} in {field_type}.")
            else:
                param_dict[field_para] = sanitize_fmt(field_var)

        return (
            field_type
            + "Field("
            + ", ".join([f"{k}={v}" for k, v in param_dict.items()])
            + ")"
        )

    @staticmethod
    def parse_label_field(field_type: str, param_list: List[str]) -> str:
        """
        解析处理Label类型的field
        """

        def sanitize_dom(val: str) -> str:
            """
            Label中对dom部分的校验，是用来严格限制特定格式或者字符。
            防止yaml里有一些异常代码注入到生成的Python 代码里被执行起来。
            """
            if not val.isidentifier():
                raise DefineSyntaxError(f"invalid dom: {val}")
            return val

        param_dict = dict()
        if not param_list:
            raise DefineSyntaxError(f"{field_type} must contains parameter `dom`")
        for param in param_list:
            parts = param.split("=")
            parts = [i.strip() for i in parts]
            # 需要考虑参数省略的情况，因为dom经常省略
            if len(parts) == 2:
                field_para = parts[0]
                field_var = parts[1]
            elif len(parts) == 1:
                field_para = "dom"
                field_var = parts[0]
            else:
                raise DefineSyntaxError(
                    f"invalid parameters {param_list} in {field_type}."
                )
            if field_para != "dom":
                raise DefineSyntaxError(
                    f"invalid parameters {field_para} in {field_type}."
                )

            if field_para in param_dict:
                raise ValueError(f"duplicated param {param} in {field_type}.")
            else:
                param_dict[field_para] = sanitize_dom(field_var)

        return (
            field_type
            + "Field("
            + ", ".join([f"{k}={v}" for k, v in param_dict.items()])
            + ")"
        )

    def parse_field(self, field_name: str, field_type: str, params_list: List[str] = None) -> str:
        """
        校验struct类型的每个字段的入口函数，对不同情况（Int,Image,List...）的字段进行校验并读入内存。
            raw_field_type: like: Int, Image, Label[dom=MyClassDom], List[List[Int], ordered = True], ....
        """
        if field_type in self.TYPES_WITHOUT_PARS:
            # 不带参数的不需要校验，直接可以转化为python代码（注意区分yaml中的模型部分到ORM的校验和通过ORM读入数据的校验，
            # 后者在dataset.py中定义，你脑子里想的Int也需要校验是数据的校验。）
            if params_list:
                raise DefineSyntaxError(f"{field_type} should not contains parameters.")
            return field_type + "Field()"
        elif field_type in self.TYPES_LIST:
            # 带参数的List类型的字段的校验
            # （因为List类型比较特殊，里面可以包含List，Label等各种其他字段，涉及递归，所以单独拿出来）
            if not params_list:
                raise DefineSyntaxError(f"{field_type} must contains parameters.")
            return self.parse_list_filed(field_name, field_type, params_list)
        elif field_type in self.TYPES_TIME:
            # 带参数的Date, Time类型的字段的校验
            return self.parse_time_field(field_type, params_list)
        elif field_type in self.TYPES_LABEL:
            # 带参数的Label类型的字段的校验
            return self.parse_label_field(field_type, params_list)
        else:
            # Struct类型的字段的校验
            if field_type not in self.struct:
                raise DefineTypeError(f"No type {field_type} in DSDL.")
            return field_type + "()"

    def pre_parse_struct_field(self, field_name: str, raw_field_type: str) -> str:
        # 将所有field可能都有的一些参数提取出来，类似is_attr、optional等
        raw_field_type = raw_field_type.strip()
        fixed_params = re.findall(r"\[(.*)\]", raw_field_type)
        if len(fixed_params) >= 2:
            raise DefineSyntaxError(f"Error in definition of {raw_field_type} in DSDL.")
        elif len(fixed_params) == 0:
            field_type = self.parse_field(field_name=field_name, field_type=raw_field_type)
        else:
            k_v_list = fixed_params[0]
            field_type = raw_field_type.replace("[" + k_v_list + "]", "")
            # below can split 'etype=LocalObjectEntry[cdom=COCO2017ClassDom, optional=True], optional=True' to
            # ['etype=LocalObjectEntry[cdom=COCO2017ClassDom', 'optional=True]', 'optional=True']
            k_v_list = re.split(r',\s*(?![^\[]*\])', k_v_list)
            k_v_list = [i.strip() for i in k_v_list]
            other_filed = set()
            for k_v in k_v_list:
                if k_v.startswith("is_attr"):
                    if k_v.endswith("=True"):
                        self.is_attr.add(field_name)
                elif k_v.startswith("optional"):
                    if k_v.endswith("=True"):
                        self.optional.add(field_name)
                else:
                    other_filed.add(k_v)
            field_type = self.parse_field(
                field_type=field_type, params_list=list(other_filed), field_name=field_name
            )
        return field_type
