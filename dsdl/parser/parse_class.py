import warnings

from .utils import *
from dsdl.exception import DefineSyntaxError, ValidationError
from dsdl.warning import DefineSyntaxWarning
from dataclasses import dataclass, field
import re
from typing import Optional


@dataclass()
class EleClass:
    label_value: str
    super_categories: Optional[List[str]] = field(default_factory=list)


class ParserClass:
    def __init__(self, class_name: str, class_value: List[str], skeleton: List = None):
        self.class_name = self._parse_class_name(raw_name=class_name)
        self.class_field = self._parse_class_value(class_value=class_value)
        self.skeleton = self._parse_skeleton(skeleton=skeleton)

    @staticmethod
    def _parse_class_name(raw_name: str) -> str:
        # 判断是否为python保留字
        try:
            check_name_format(raw_name)
        except ValidationError as e:
            raise ValidationError(f"Error with class-dom name, {e}")
        return raw_name

    def _parse_skeleton(self, skeleton: List) -> Optional[List[List[int]]]:
        if not skeleton:
            return None
        else:
            if isinstance(skeleton, list):
                if all(isinstance(item, list) for item in skeleton):
                    for item in skeleton:
                        if not all(
                                isinstance(ele, int) and len(item) == 2 for ele in item
                        ):
                            raise DefineSyntaxError(
                                f"Error in skeleton of {self.class_name}: skeleton must be list of list of int."
                            )
                    return skeleton
                else:
                    raise DefineSyntaxError(
                        f"Error in skeleton of {self.class_name}: skeleton must be list of list of int."
                    )
            else:
                raise DefineSyntaxError(
                    f"Error in skeleton of {self.class_name}: skeleton must be list of list of int."
                )

    def _check_label_name(self, label_name: str) -> str:
        if "." in label_name:
            check_flag = re.search(r"^[\w.]+$", label_name)
            if label_name.startswith("."):
                raise DefineSyntaxError(f"`{label_name}` is not allowed. Label in class-dom can't starts with dot `.`")
            if not check_flag:
                warn_msg = (
                    f"`{label_name}` is not recommended."
                    f" we recommend use alphanumeric letters (a-z, A-Z and 0-9), and underscores (_) "
                    f"for label in class-dom (with hierarchical structure)."
                )
                warnings.warn(
                    warn_msg,
                    DefineSyntaxWarning,
                )
        else:
            check_flag = re.search(r"^[\w\s]+$", label_name)
            if not check_flag:
                warn_msg = (
                    f"`{label_name}` is not recommended."
                    f" we recommend use space, alphanumeric letters (a-z, A-Z and 0-9), and underscores (_) "
                    f"for label in class-dom (without hierarchical structure)."
                )
                warnings.warn(
                    warn_msg,
                    DefineSyntaxWarning,
                )
        return label_name.strip()

    def _parse_class_value(self, class_value: List[str]) -> List[EleClass]:
        class_field = list()
        for value in class_value:
            value = self._check_label_name(value)
            ele_class = EleClass(label_value=value, super_categories=None)
            class_field.append(ele_class)
        return class_field
