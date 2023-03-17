from fastapi import APIRouter
from dsdl.server.scheme import BaseResponse, CheckParam
from dsdl.parser import dsdl_parse, CHECK_LOG
from typing import List
import json

router = APIRouter()


@router.post("/parse_yaml")
def parse_and_check_yaml(
        param: CheckParam
) -> List[dict]:
    """
        该接口是在输入各种条件以后返回所有的该数据库符合要求的数据的页数
    Args:\n
        param:\n
            dsdl_yaml: 数据的yaml文件，一般是train.yaml、test.yaml(必须)
            dsdl_library_path: 其他yaml存放路径，默认的其他yaml存放路径是`dsdl/dsdl_library`
            output_file: 生成.py文件路径，默认None，以字符串格式返回
            report_flag: 是否生成报告json，是的话会在"check_log"中返回
    """
    dsdl_py = dsdl_parse(dsdl_yaml=param.dsdl_yaml, dsdl_library_path=param.dsdl_library_path,
                         output_file=param.output_file, report_flag=param.check_flag)
    res = {"dsdl_py": dsdl_py}
    if param.check_flag:
        res["check_log"] = json.dumps(CHECK_LOG.to_struct())
    return BaseResponse.decorate(res)




