class BaseGeometry:

    def visualize(self, image, palette, **kwargs):
        pass

    def __repr__(self):
        return self.__class__.__name__ + " object"