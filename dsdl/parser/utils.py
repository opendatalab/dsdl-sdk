from jsonmodels import models, fields, validators
import keyword
from dsdl.exception import ValidationError

class CheckLogItem(models.Base):
    def_name = fields.StringField(
        required=True, validators=validators.Enum("class_domain", "struct", "all")
    )
    yaml = fields.StringField(nullable=True)
    flag = fields.IntField(
        required=True, validators=validators.Enum(0, 1), default=0
    )  # 0:error, 1: right
    msg = fields.StringField(nullable=True)


class CheckLog(models.Base):
    def_name = fields.StringField(
        required=True, validators=validators.Enum("class_domain", "struct", "all")
    )
    flag = fields.IntField(
        required=True, validators=validators.Enum(0, 1), default=0
    )  # 0:error, 1: right
    sub_struct = fields.ListField([CheckLogItem], nullable=True)

def check_name_format(varstr: str):
    if not varstr.isidentifier():
        err_msg = (
            f"`{varstr}` must be a valid identifier. "
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

def check_is_bracket_pair(var_str: str) -> bool:
    """
    check if var_str has bracket in pairs and in order, return True: yes, False: not in pairs or in order
    """
    bracket = {")": "(", "]": "[", "}": "{"}
    b = []
    for i in var_str:
        if i in bracket.values():
            b.append(i)
        elif len(b) > 0 and b[-1] == bracket.get(i):
            b.pop()
        elif i in bracket.keys():
            b.append(i)
        else:
            pass
    if len(b) == 0:
        return True
    else:
        return False


