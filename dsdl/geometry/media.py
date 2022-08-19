import io
from PIL import Image
import numpy as np


class ImageMedia:

    def __init__(self, location, file_reader):
        self._loc = location
        self._reader = file_reader

    @property
    def location(self):
        return self._loc

    def to_bytes(self):
        return io.BytesIO(self._reader.read())

    def to_image(self):
        return Image.open(self.to_bytes())

    def to_array(self):
        return np.array(self.to_image())

    def __repr__(self):
        return f"path:{self.location}"
