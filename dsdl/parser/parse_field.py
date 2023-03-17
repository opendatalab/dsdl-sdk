
import re
from dataclasses import dataclass
from typing import Optional, Set, Dict
from typing import List as _List

# 先导入dsdl.fields这里FIELD才可以生效
from dsdl.fields import *
from dsdl.geometry import FIELD
from dsdl.exception import DefineSyntaxError
from .utils import *

@dataclass()
class EleStruct:
    name: str
    type: str


class ParserField():
    def __init__(self,
                    struct_name_params: Dict,
                    struct_name: Set[str], 
                    struct_params: str = None):
        self.struct_name_params = struct_name_params # 所有struct及params，后续校验cdom用
        self.struct = struct_name  # field 中包含的struct，后续校验用
        self.struct_params = struct_params
    
    def pre_parse_struct_field(
        self, field_name: Optional[str], raw_field_type: str
    ) -> str:
        """
        校验struct类型的每个字段的入口函数，对不同情况（Int,Image,List...）的字段进行校验并读入内存。
            field_name: like: "category_id", "category", "annotation", None, ....
            raw_field_type: like: Int, Label[dom=$cdom0], List[List[Int], ordered = True], 'dom=$cdom0', ....
        """
        # Image->Image(), List[KeyPointLocalObject] -> List(KeyPointLocalObject())
        # List[etype=KeyPointLocalObject[cdom0=$cdom0]] -> List(etype=KeyPointLocalObject(cdom0=$cdom0))
        raw_field_type = raw_field_type.strip()
        fixed_params = re.findall(r"\[(.*)\]", raw_field_type)
        if len(fixed_params)==0:
           field_type = self.parse_type(raw_field_type)
        else:
            k_v_list_ori = fixed_params[0]
            raplace_field_type = raw_field_type.replace("[" + k_v_list_ori + "]", "")
            # below can split 'etype=LocalObjectEntry[cdom=COCO2017ClassDom, optional=True], optional=True' to
            # ['etype=LocalObjectEntry[cdom=COCO2017ClassDom', 'optional=True]', 'optional=True'],保持原有顺序
            k_v_list_ori = re.split(r",\s*(?![^\[]*\])", k_v_list_ori)
            k_v_list = list(set([i.strip() for i in k_v_list_ori]))
            k_v_list.sort(key = k_v_list_ori.index)
            new_list = []

            for k_v in k_v_list:
                # k_v_temp = k_v.replace(" ", "")
                if not check_is_bracket_pair(k_v):
                    raise DefineSyntaxError(
                        f"Error in field with value of `{raw_field_type}`. Check the `{k_v}` part."
                    )
                if raplace_field_type in self.struct:
                    # 判断cdom,和调用struct的params对应
                    k =  k_v.split('=')[0]
                    if k in self.struct_name_params[raplace_field_type]:
                        
                        if len(k_v.split('='))<2:
                            raise DefineSyntaxError( f"{k_v} is {raplace_field_type} params, should have '='")
                        cdom_name =  k_v.split('=')[1] 
                
                        # 校验cdom_name是否符合定义
                        if cdom_name.replace('$','') not in self.struct_params:
                            raise DefineSyntaxError(
                                    f"definition error of dom '{cdom_name}' not in $params `{self.struct_params}`, "
                                    f"check cdom is defined correctly."
                                )
                        cdom_name = '"' + cdom_name + '"'
                        k_v =  k_v.replace( k_v.split('=')[1], cdom_name)
                elif k_v.startswith(('dom','cdom')):
                    k = k_v.split('=')[0]
                    if len(k_v.split('='))<2:
                        raise DefineSyntaxError( f"{k_v} is {raplace_field_type} params, should have '='")
                    cdom_name =  k_v.split('=')[1] 
                    if cdom_name.replace('$','') not in self.struct_params:
                        raise DefineSyntaxError(
                                    f"definition error of dom '{cdom_name}' not in $params `{self.struct_params}`, "
                                    f"check cdom is defined correctly."
                                )
                    cdom_name = '"' + cdom_name + '"'
                    k_v =  k_v.replace( k_v.split('=')[1], cdom_name)

                new_list.append(k_v)

            field_type = self.parse_type(raplace_field_type, new_list)
        return field_type

    
    def parse_type(
        self,
        field_type: str,
        param_list: _List[str] = None,
        ) -> str:
        """
        校验具体type并形成.py需要格式。
        field_type: like: Int, Label, List,  'dom=$cdom0', ....
        param_list: like: None, ['dom=$cdom0'], ['List[Int]', 'ordered = True'], None, ....
        """
        if field_type.startswith('List'):
            field_type = self.parse_list_field(field_type,param_list)
            return field_type
        # 非List开头，暂时不考虑嵌套的情况
        else:
            params_str = ''
            # eg. optional=True, cdom=$cdom, BBox,
            # -------------------------------------------------------------这里以fieldlist来判断,并添加格式判断
            if field_type in FIELD or field_type in self.struct:
                check_name_format(field_type)
                # 计算param
                if param_list:
                    for param in param_list:
                        # eg. optional=True, cdom=$cdom, BBox, NewType[is_optional=True]
                        param_str = self.pre_parse_struct_field(field_name=None,raw_field_type=param)
                        params_str += (param_str + ',')
                    params_str = params_str[:-1]
                return field_type + '(' + params_str + ')'
            else:
                if param_list:
                    raise DefineSyntaxError(f'definition error of {field_type} has {param_list}, please check field ')
                
                if field_type.split('=')[-1]=='true':
                    field_type = field_type.replace(field_type.split('=')[-1],'True')
                if field_type.split('=')[-1]=='false':
                    field_type = field_type.replace(field_type.split('=')[-1],'False')
                return field_type
            

    def parse_list_field(self, 
                         field_type: str, 
                         param_list: _List[str]
                         ) -> str:
        """
        解析处理List类型的field
        """
        # field_type:List
        # param_list:[etype=KeyPointLocalObject[cdom0=$cdom0],ordered=True] or Bbox
        # 这里不进行etype识别，有什么转什么,识别到的struct需要显式定义为etype=xxx
        res = field_type + "("
        if param_list:
            for param in param_list:
                if param.startswith('etype'):
                    ele_type_name = param.split("=",1)[0].strip()
                    if len(param.split("=",1))<2:
                        raise DefineSyntaxError( f"{param} is list etype params, should have '='")
                    ele_type = param.split("=",1)[1].strip()

                    ele_type = self.pre_parse_struct_field(field_name=None, raw_field_type=ele_type)
                    res += (ele_type_name + "=" + ele_type + ',')
                else:
                    ele_type = self.pre_parse_struct_field(field_name=None, raw_field_type=param)
                    res += (ele_type+ ',')
            res = res[:-1]
            
        return res + ')'