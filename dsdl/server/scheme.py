from typing import Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    err_code: int
    err_msg: str

    @staticmethod
    def decorate(target: dict, code: int = 0, msg: str = "success"):
        """
        修饰器，给字典对象添加返回公共头部
        :param target: 要修改的字典
        :param code: 错误码(0为正确)
        :param msg: 错误描述(success为成功)
        :return: 新的字典
        """
        target["err_code"] = code
        target["err_msg"] = msg
        return target


class CheckParam(BaseModel):
    dsdl_yaml: str
    dsdl_library_path: str = "dsdl/dsdl_library"
    output_file: Optional[str] = None
    check_flag: bool = 1


