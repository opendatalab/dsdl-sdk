class ValidationError(RuntimeError):
    pass


class ClassHasDefinedError(RuntimeError):
    pass


class ClassNotFoundError(RuntimeError):
    pass


class DefineSyntaxError(SyntaxError):
    pass


class DSDLImportError(ImportError):
    pass


class DefineTypeError(TypeError):
    pass


class FileReadError(TypeError):
    pass


