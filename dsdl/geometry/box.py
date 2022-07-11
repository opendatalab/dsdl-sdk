from typing import TypeVar, List
import numpy as np

_ELE_TYPE = TypeVar("_ELE_TYPE", int, float)


class BBox:

    def __init__(
            self,
            x: _ELE_TYPE,
            y: _ELE_TYPE,
            width: _ELE_TYPE,
            height: _ELE_TYPE
    ):
        self._data = [x, y, width, height]

    @property
    def x(self) -> _ELE_TYPE:
        return self._data[0]

    @property
    def y(self) -> _ELE_TYPE:
        return self._data[1]

    @property
    def width(self) -> _ELE_TYPE:
        return self._data[2]

    @property
    def height(self) -> _ELE_TYPE:
        return self._data[3]

    @property
    def xmin(self) -> _ELE_TYPE:
        return self._data[0]

    @property
    def ymin(self) -> _ELE_TYPE:
        return self._data[1]

    @property
    def xmax(self) -> _ELE_TYPE:
        return self._data[0] + self._data[2]

    @property
    def ymax(self) -> _ELE_TYPE:
        return self._data[1] + self._data[3]

    @property
    def area(self) -> _ELE_TYPE:
        return self.width * self.height

    @property
    def xyxy(self) -> List[_ELE_TYPE]:
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @property
    def xywh(self) -> List[_ELE_TYPE]:
        return [self.xmin, self.ymin, self.width, self.height]

    def to_int(self):
        self._data = [int(_) for _ in self._data]

    def to_float(self):
        self._data = [float(_) for _ in self._data]

    def visualize(self, image, draw_obj, palette, **kwargs):
        color = (0, 255, 0)
        if "label" in kwargs:
            for label in kwargs["label"].values():
                if label.category_name not in palette:
                    palette[label.category_name] = tuple(np.random.randint(0, 255, size=[3]))

                color = palette[label.category_name]
        draw_obj.rectangle(self.xyxy, outline=color, width=2)
        return draw_obj

    def __repr__(self):
        return str(self.xyxy)
