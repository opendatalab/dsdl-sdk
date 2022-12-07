from .utils import *
from dsdl.exception import DefineSyntaxError
from dataclasses import dataclass, field
import re
from typing import Optional, Tuple


@dataclass()
class SuperCategories:
    class_dom: str
    label_value: str


@dataclass()
class EleClassDetail:
    label_value: str
    super_categories: Optional[List[SuperCategories]] = field(default_factory=list)


@dataclass()
class EleClass:
    label_value: str
    super_categories: Optional[List[str]] = field(default_factory=list)


class ParserClass:
    def __init__(self, class_name: str, class_value: List[str], skeleton: List = None):
        self.class_name, self.super_class_list = self._parse_class_name(
            raw_name=class_name
        )
        self.class_field_detail = self._parse_class_value(class_value=class_value)
        self.class_field = self._parse_super_categories()
        self.skeleton = self._parse_skeleton(skeleton=skeleton)

    @staticmethod
    def _parse_class_name(raw_name: str) -> Tuple[str, Optional[List[str]]]:
        super_class = re.findall(r"\[(.*)\]", raw_name)
        if len(super_class) >= 2:
            raise DefineSyntaxError(f"Error in definition of {raw_name} in DSDL.")
        elif len(super_class) == 0:
            class_name = raw_name
            super_class_list = []
        else:
            super_class_list = super_class[0]
            class_name = raw_name.replace("[" + super_class_list + "]", "")
            super_class_list = [i.strip() for i in super_class_list.split(",")]
        return class_name, super_class_list

    def _parse_skeleton(self, skeleton: List) -> Optional[List[List[int]]]:
        if not skeleton:
            return None
        else:
            if isinstance(skeleton, list):
                if all(isinstance(item, list) for item in skeleton):
                    for item in skeleton:
                        if not all(isinstance(ele, int) and len(item)==2 for ele in item):
                            raise DefineSyntaxError(
                                f"Error in skeleton of {self.class_name}: skeleton must be list of list of int.")
                    return skeleton
                else:
                    raise DefineSyntaxError(
                        f"Error in skeleton of {self.class_name}: skeleton must be list of list of int.")
            else:
                raise DefineSyntaxError(f"Error in skeleton of {self.class_name}: skeleton must be list of list of int.")


    def _parse_class_value(self, class_value: List[str]) -> List[EleClassDetail]:
        class_field = list()
        if self.super_class_list:
            for value in class_value:
                super_class_value = re.findall(r"\[(.*?)\]", value)
                assert len(super_class_value) == len(
                    self.super_class_list
                ), f"length of {value} must equal to nums of super_categories."

                label = value.split("[")[0]
                ele_class = EleClassDetail(label_value=label)
                for super_class_name, super_label_value in zip(
                        self.super_class_list, super_class_value
                ):
                    if super_label_value:
                        for super_label in super_label_value.split(","):
                            temp_super = SuperCategories(
                                class_dom=super_class_name, label_value=super_label.strip()
                            )
                            ele_class.super_categories.append(temp_super)
                class_field.append(ele_class)
        else:
            for value in class_value:
                super_class_value = re.findall(r"\[(.*?)\]", value)
                assert (
                        len(super_class_value) == 0
                ), f"length of {value} must equal to nums of super_categories."
                ele_class = EleClassDetail(
                    label_value=value.strip(), super_categories=None
                )
                class_field.append(ele_class)
        return class_field

    def _parse_super_categories(self) -> List[EleClass]:
        class_field = list()
        for ele in self.class_field_detail:
            ele_class = EleClass(label_value=ele.label_value)
            if ele.super_categories:
                ele_class.super_categories = list()
                for super_label in ele.super_categories:
                    temp = (
                            super_label.class_dom
                            + '.get_label("'
                            + super_label.label_value
                            + '")'
                    )
                    ele_class.super_categories.append(temp)
            else:
                ele_class.super_categories = None
            class_field.append(ele_class)
        return class_field
