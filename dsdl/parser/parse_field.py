from dsdl.exception import DefineSyntaxError
from .utils import *
from dataclasses import dataclass


@dataclass()
class EleStruct:
    name: str
    type: str


class ParserField:
    def __init__(self):
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
        self.TYPES_WITH_PARS = ["Date", "Label", "Time"]
        self.TYPES_WITH_PARS_SP = ["List"]
        self.is_attr = set()
        self.optional = set()

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

        raw = re.findall(r"\[(.*)\]", raw)
        if not raw:
            raise DefineSyntaxError("List must contains other data type")
        if len(raw) > 1:
            raise DefineSyntaxError("error writing in List definition")
        param_list = raw[0].split(",")
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
            return self.parse_struct_field_with_params(raw_field_type)
        else:
            c_dom = re.findall(r"\[(.*)\]", raw_field_type)
            if c_dom:
                raw_field_type = raw_field_type.replace(
                    "[" + c_dom[0] + "]", "", 1
                ).strip()
            return raw_field_type + "()"
            # raise DefineTypeError(f"No type {raw_field_type} in DSDL.")

    def pre_parse_struct_field(self, field_name: str, raw_field_type: str) -> str:
        raw_field_type = raw_field_type.replace(" ", "")
        fixed_params = re.findall(r"\[(.*)\]", raw_field_type)
        if len(fixed_params) >= 2:
            raise DefineSyntaxError(f"Error in definition of {raw_field_type} in DSDL.")
        elif len(fixed_params) == 0:
            field_type = self.parse_struct_field(raw_field_type=raw_field_type)
        else:
            k_v_list = fixed_params[0]
            field_type = raw_field_type.replace("[" + k_v_list + "]", "")
            k_v_list = k_v_list.split(",")
            other_filed = set()
            for k_v in k_v_list:
                if k_v.startswith("is_attr=True"):
                    self.is_attr.add(field_name)
                elif k_v.startswith("optional=True"):
                    self.optional.add(field_name)
                else:
                    other_filed.add(k_v)
            if other_filed:
                if field_type in self.TYPES_WITHOUT_PARS:
                    raise DefineSyntaxError(
                        f"Error in definition of {raw_field_type} in DSDL."
                    )
                field_type = field_type + "[" + ", ".join(other_filed) + "]"
            field_type = self.parse_struct_field(raw_field_type=field_type)
        return field_type
