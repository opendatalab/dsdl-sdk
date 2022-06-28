import yaml
import os
from typing import Any


class ConfigBase:
    def _get_config_field(self, field: str) -> Any:
        # 获取field值
        raise NotImplementedError

    def _get_field_type(self, field: str) -> type:
        # 获取field的类型
        if field in self.__annotations__:
            return self.__annotations__[field]

    @classmethod
    def _parse_field_type(cls, _type, value):
        func = getattr(cls, f"_parse_{_type.__name__}", cls._parse_str)
        return func(value)

    @staticmethod
    def _parse_bool(value: str) -> bool:
        return value.lower() not in frozenset(("0", "", "false"))

    @staticmethod
    def _parse_str(value) -> str:
        return str(value)

    @staticmethod
    def _parse_int(value: str) -> int:
        try:
            return int(value)
        except ValueError:
            return 0

    @staticmethod
    def _parse_float(value: str) -> float:
        try:
            return float(value)
        except ValueError:
            return 0

    @staticmethod
    def _parse_list(value: str) -> list:
        return value.split(",")

    def __str__(self):
        res = []
        for attribute, value in self.__dict__.items():
            try:
                res.append(str(attribute) + "=" + str(value))
            except:
                continue
        return " ".join(res)

    def fetch(self):
        for field in self.__annotations__.keys():
            setattr(self, field, self._get_config_field(field))


class YamlConfig(ConfigBase):
    def __init__(self, yaml_path):
        with open(yaml_path) as fin:
            self.config_dict = yaml.load(fin, Loader=yaml.SafeLoader)
        self.DSDL_LIBRARY_PATH = (
            self.config_dict["DSDL_LIBRARY_PATH"]
            if "DSDL_LIBRARY_PATH" in self.config_dict
            else getattr(self, "DSDL_LIBRARY_PATH")
        )

    def _get_config_field(self, field: str):
        if field in self.config_dict:
            res = self.config_dict[field]
        else:
            res = getattr(self, field)
        if field != "DSDL_LIBRARY_PATH":
            if res == os.path.basename(res):
                return os.path.join(self.DSDL_LIBRARY_PATH, res)
            else:
                return res
        else:
            return self.DSDL_LIBRARY_PATH

    def fetch(self):
        # 如果config.yaml里面不存在，先判断我们给定默认config.py中存在不，不存在就用其他值赋值
        if (
            "STRUCT_YAML" not in self.config_dict.keys()
            and "CLASS_YAML" not in self.config_dict.keys()
        ):

            if not getattr(self, "STRUCT_YAML"):
                setattr(self, "STRUCT_YAML", self._get_config_field("DATA_YAML"))
            if not getattr(self, "CLASS_YAML"):
                setattr(self, "CLASS_YAML", self._get_config_field("DATA_YAML"))
        elif (
            "STRUCT_YAML" in self.config_dict.keys()
            and "CLASS_YAML" not in self.config_dict.keys()
        ):
            if not getattr(self, "CLASS_YAML"):
                setattr(self, "CLASS_YAML", self._get_config_field("STRUCT_YAML"))
        elif (
            "STRUCT_YAML" not in self.config_dict.keys()
            and "CLASS_YAML" in self.config_dict.keys()
        ):
            if not getattr(self, "STRUCT_YAML"):
                setattr(self, "STRUCT_YAML", self._get_config_field("CLASS_YAML"))
        for field in self.__annotations__.keys():
            setattr(self, field, self._get_config_field(field))
