class Field:
    def __init__(self, optional=False):
        self._optional = optional

    @property
    def is_optional(self):
        return self._optional

    def __str__(self):
        return "<%s>" % self.__class__.__name__

    def validate(self, value):
        """
        Validate value and raise ValidationError if necessary.
        """
        return value

    @classmethod
    def extract_key(cls):
        field_cls_name = cls.__name__
        return "$" + field_cls_name.replace("Field", "").lower()
