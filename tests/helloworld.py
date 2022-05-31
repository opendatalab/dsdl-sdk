from dsdl.types import *
from enum import Enum


class MyClassDom(Enum):
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"
    TIGER = "tiger"


class ImageClassificationSample(Struct):
    image = ImageField()
    label = LabelField(dom=MyClassDom)
    valid = BoolField()
    val = NumField()
    ival = IntField()
    p = CoordField()
