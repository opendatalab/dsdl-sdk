class Field:
    def __init__(self):
        pass

    def __str__(self):
        return "<%s>" % self.__class__.__name__

    def validate(self, value):
        """
        Validate value and raise ValidationError if necessary.
        """
        return value
