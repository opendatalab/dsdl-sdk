"""
DSDL General Fields, Including:
1. BoolField
2. IntField
3. NumField
4. StrField
5. ListField
6. DictField
"""
from .field import Field
from .struct import Struct
from ..exception import ValidationError
from typing import List, Dict, Union, Any
from ..objectio import BaseFileReader


class BoolField(Field):
    """A DSDL Field to validate and return a boolean value.

    Examples:
        >>> bool_field = BoolField()
        >>> value = True
        >>> bool_field.validate(value)
        True
    """

    def validate(self, value: bool) -> bool:
        """Validate whether the given value is a valid boolean value.

        Args:
            value: A value to be validated whether it is a boolean value.

        Returns:
            The value which has been validated.
        """
        if value not in [True, False]:
            raise ValidationError(f"BoolField Error: expect True/False, got {value}")
        return value


class IntField(Field):
    """A DSDL Field to validate and return an int value.

    Examples:
        >>> int_field = IntField()
        >>> value = 1.0
        >>> int_field.validate(value)
        1
    """

    def validate(self, value: int) -> int:
        """Validate whether the given value is a valid integer value.

        Args:
            value: A value to be validated whether it is an integer value.

        Returns:
            The value which has been validated.
        """
        try:
            return int(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"IntField Error: expect int, got {value}")


class NumField(Field):
    """A DSDL Field to validate and return a float value.

    Examples:
        >>> float_field = NumField()
        >>> value = 1
        >>> float_field.validate(value)
        1.0
    """

    def validate(self, value: float) -> float:
        """Validate whether the given value is a valid float value.

        Args:
            value: A value to be validated whether it is a float value.

        Returns:
            The value which has been validated.
        """
        try:
            return float(value)
        except (ValueError, TypeError) as _:
            raise ValidationError(f"NumField Error: expect num, got {value}")


class StrField(Field):
    """A DSDL Field to validate and return a str value.

    Examples:
        >>> str_field = StrField()
        >>> value = "test"
        >>> str_field.validate(value)
        "test"
    """

    def validate(self, value: str) -> str:
        """Validate whether the given value is a valid str value.

        Args:
            value: A value to be validated whether it is a str value.

        Returns:
            The value which has been validated.
        """
        try:
            return "" + value
        except TypeError as _:
            raise ValidationError(f"StrField Error: expect str value, got {value}")


class ListField(Field):
    def __init__(self, ele_type: Union[Field, Struct], ordered: bool = False, *args, **kwargs):
        """A DSDL Field to validate all the value in the given list and return a list of validated object.

        Examples:
            >>> list_field = ListField(ele_type=DictField(), ordered=False)
            >>> value = [{"a": 1}, {"b": 2}, {"c": 3}]
            >>> list_field.validate(value)
            [{"a": 1}, {"b": 2}, {"c": 3}]

        Args:
            ele_type: The field type of the element in the given list value.
            ordered: Whether the order of the elements in the list should be contained.

        Attributes:
            ele_type(Union[Field, Struct]): The field type or struct type of the element in the given list value.
            ordered(bool): Whether the order of the elements in the list should be contained.
            file_reader(BaseFileReader): The file reader object which is needed when the ele_type is ImageField, LabelMapField or InstanceMapField.
            prefix(str): A helper prefix string which is used when initializing a Struct object.
            flatten_dic(Dict[str, Any]): A helper dict which is used in a Struct object.
        """
        self.ordered = ordered
        self.ele_type = ele_type
        self.file_reader = None
        self.prefix = None
        self.flatten_dic = None
        super().__init__(*args, **kwargs)

    def validate(self, value: List[Any]) -> List[Union[Field, Struct]]:
        """Validate all the value in the given list and return a list of validated object.

        Args:
            value: A given list whose elements are to be validated.

        Returns:
            A list of validated object.
        """
        if hasattr(self.ele_type, "set_file_reader"):
            self.ele_type.set_file_reader(self.file_reader)
        if isinstance(self.ele_type, Field):
            if self.prefix is not None and self.flatten_dic is not None:
                field_key = self.ele_type.extract_key()
                field_dic = self.flatten_dic.setdefault(field_key, {})
                res = [self.ele_type.validate(_) for _ in value]
                paths = [f"{self.prefix}/{ind}" for ind in range(len(res))]
                _ = [field_dic.update({k: v}) for k, v in zip(paths, res)]
            else:
                res = [self.ele_type.validate(_) for _ in value]

        elif isinstance(self.ele_type, Struct):
            res = [
                self.ele_type.__class__(
                    file_reader=self.file_reader,
                    prefix=f"{self.prefix}/{i}",
                    flatten_dic=self.flatten_dic, **item)
                for i, item in enumerate(value)
            ]
        else:
            raise ValidationError(
                f"Wrong ele_type in ListField, only 'Struct' or 'Field' are permitted, but got '{type(self.ele_type)}'")
        return res

    def set_file_reader(self, file_reader: BaseFileReader) -> None:
        """Set the `file_reader` attribute for the current `ListField` object.

        Args:
            file_reader: The given file reader object to replace one in the current `ListField` object.

        Returns:
            `None`
        """
        self.file_reader = file_reader

    def set_prefix(self, prefix: str) -> None:
        """Set the `prefix` attribute for the current `ListField` object.

        Args:
            prefix: The given prefix to replace one in the current `ListField` object.

        Returns:
            `None`
        """
        self.prefix = prefix

    def set_flatten_dic(self, dic: Dict[str, Any]) -> None:
        """Set the `flatten_dic` attribute for the current `ListField` object.

         Args:
             prefix: The given flatten_dic to replace one in the current `ListField` object.

         Returns:
             `None`
         """
        self.flatten_dic = dic


class DictField(Field):
    """A DSDL Field to validate and return a dict value.

    Examples:
        >>> dic_field = DictField()
        >>> value = {"1": "a"}
        >>> dic_field.validate(value)
        {"1": "a"}
    """

    def validate(self, value: Dict) -> Dict:
        """Validate whether the given value is a valid dict value.

        Args:
            value: A value to be validated whether it is a dict value.

        Returns:
            The value which has been validated.
        """
        if not isinstance(value, dict):
            raise ValidationError(f"DictField Error: expect dict value, got {value.__class__}")
        return value
