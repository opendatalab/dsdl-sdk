class ValidationError(RuntimeError):
    pass


class StructHasDefinedError(RuntimeError):
    pass


class StructNotFoundError(RuntimeError):
    pass


class DefineSyntaxError(SyntaxError):
    pass
