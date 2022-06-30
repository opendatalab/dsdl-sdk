# Generated by the dsdl parser. DO NOT EDIT!

from dsdl.types import *
from enum import Enum


class VOCClassDom(Enum):
    CAR = "car"
    AEROPLANE = "aeroplane"
    HORSE = "horse"
    PERSON = "person"
    BOTTLE = "bottle"
    BICYCLE = "bicycle"
    BOAT = "boat"
    DOG = "dog"
    TVMONITOR = "tvmonitor"
    CHAIR = "chair"
    DININGTABLE = "diningtable"
    POTTEDPLANT = "pottedplant"
    TRAIN = "train"
    CAT = "cat"
    BIRD = "bird"
    SOFA = "sofa"
    SHEEP = "sheep"
    MOTORBIKE = "motorbike"
    BUS = "bus"
    COW = "cow"


class COCOClassDom(Enum):
    PERSON = "person"
    BICYCLE = "bicycle"
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    AIRPLANE = "airplane"
    BUS = "bus"
    TRAIN = "train"
    TRUCK = "truck"
    BOAT = "boat"
    BENCH = "bench"
    BIRD = "bird"
    CAT = "cat"
    DOG = "dog"
    HORSE = "horse"
    SHEEP = "sheep"
    COW = "cow"
    ELEPHANT = "elephant"
    BEAR = "bear"
    ZEBRA = "zebra"
    GIRAFFE = "giraffe"
    BACKPACK = "backpack"
    UMBRELLA = "umbrella"
    HANDBAG = "handbag"
    TIE = "tie"
    SUITCASE = "suitcase"
    FRISBEE = "frisbee"
    SKIS = "skis"
    SNOWBOARD = "snowboard"
    KITE = "kite"
    SKATEBOARD = "skateboard"
    SURFBOARD = "surfboard"
    BOTTLE = "bottle"
    CUP = "cup"
    FORK = "fork"
    KNIFE = "knife"
    SPOON = "spoon"
    BOWL = "bowl"
    BANANA = "banana"
    APPLE = "apple"
    SANDWICH = "sandwich"
    ORANGE = "orange"
    BROCCOLI = "broccoli"
    CARROT = "carrot"
    PIZZA = "pizza"
    DONUT = "donut"
    CAKE = "cake"
    CHAIR = "chair"
    COUCH = "couch"
    BED = "bed"
    TOILET = "toilet"
    TV = "tv"
    LAPTOP = "laptop"
    MOUSE = "mouse"
    REMOTE = "remote"
    KEYBOARD = "keyboard"
    MICROWAVE = "microwave"
    OVEN = "oven"
    TOASTER = "toaster"
    SINK = "sink"
    REFRIGERATOR = "refrigerator"
    BOOK = "book"
    CLOCK = "clock"
    VASE = "vase"
    SCISSORS = "scissors"
    TOOTHBRUSH = "toothbrush"


class COCOClassFullDom(Enum):
    PERSON = "person"
    BICYCLE = "bicycle"
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    AIRPLANE = "airplane"
    BUS = "bus"
    TRAIN = "train"
    TRUCK = "truck"
    BOAT = "boat"
    BENCH = "bench"
    BIRD = "bird"
    CAT = "cat"
    DOG = "dog"
    HORSE = "horse"
    SHEEP = "sheep"
    COW = "cow"
    ELEPHANT = "elephant"
    BEAR = "bear"
    ZEBRA = "zebra"
    GIRAFFE = "giraffe"
    HAT = "hat"
    BACKPACK = "backpack"
    UMBRELLA = "umbrella"
    SHOE = "shoe"
    HANDBAG = "handbag"
    TIE = "tie"
    SUITCASE = "suitcase"
    FRISBEE = "frisbee"
    SKIS = "skis"
    SNOWBOARD = "snowboard"
    KITE = "kite"
    SKATEBOARD = "skateboard"
    SURFBOARD = "surfboard"
    BOTTLE = "bottle"
    PLATE = "plate"
    CUP = "cup"
    FORK = "fork"
    KNIFE = "knife"
    SPOON = "spoon"
    BOWL = "bowl"
    BANANA = "banana"
    APPLE = "apple"
    SANDWICH = "sandwich"
    ORANGE = "orange"
    BROCCOLI = "broccoli"
    CARROT = "carrot"
    PIZZA = "pizza"
    DONUT = "donut"
    CAKE = "cake"
    CHAIR = "chair"
    COUCH = "couch"
    BED = "bed"
    MIRROR = "mirror"
    WINDOW = "window"
    DESK = "desk"
    TOILET = "toilet"
    DOOR = "door"
    TV = "tv"
    LAPTOP = "laptop"
    MOUSE = "mouse"
    REMOTE = "remote"
    KEYBOARD = "keyboard"
    MICROWAVE = "microwave"
    OVEN = "oven"
    TOASTER = "toaster"
    SINK = "sink"
    REFRIGERATOR = "refrigerator"
    BLENDER = "blender"
    BOOK = "book"
    CLOCK = "clock"
    VASE = "vase"
    SCISSORS = "scissors"
    TOOTHBRUSH = "toothbrush"


class LocalObjectEntry(Struct):
    bbox = BBoxField()
    label = LabelField(dom=COCOClassFullDom)


class ObjectDetectionSample(Struct):
    image = ImageField()
    objects = ListField(ele_type=LocalObjectEntry())
