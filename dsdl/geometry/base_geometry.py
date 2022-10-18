class BaseGeometry:

    def visualize(self, image, palette, **kwargs):
        return image

    def __repr__(self):
        return self.__class__.__name__ + " object"