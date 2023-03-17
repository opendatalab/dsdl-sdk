from .special import *
from .generic import *
from .unstructure import *
from .struct import *
from .base_field import List

__special_fields__ = [
    "Coord",
    "Coord3D",
    "Interval",
    "BBox",
    "RotatedBBox",
    "Polygon",
    "Label",
    "Keypoint",
    "Text",
    "ImageShape",
    "InstanceID",
    "UniqueID",
    "Date",
    "Time"
]

__generic_fields__ = [
    "Bool",
    "Int",
    "Num",
    "Str",
    "Dict",
    "List"
]

__unstructure_fields__ = [
    "Image",
    "LabelMap",
    "InstanceMap"
]

__all__ = __unstructure_fields__ + __generic_fields__ + __special_fields__ + ["Struct"]
