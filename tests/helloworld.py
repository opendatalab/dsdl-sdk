from dsdl.types import *
from enum import Enum


class MyClassDom(Enum):
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"
    TIGER = "tiger"


class TestListItem(Struct):
    val = NumField()
    i_list = ListField(IntField())


class ImageClassificationSample(Struct):
    image = ImageField()
    label = LabelField(dom=MyClassDom)
    valid = BoolField()
    val = NumField()
    i_val = IntField()
    p = CoordField()
    label_list = ListField(LabelField(dom=MyClassDom))
    i_list = ListField(IntField())
    item_list = ListField(TestListItem())
    a = IntField()
