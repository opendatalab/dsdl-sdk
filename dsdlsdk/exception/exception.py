class SDKException(Exception):

    def __init__(self, message):
        super().__init__(message)


class DatasetPathNotExists(SDKException):

    def __init__(self, message):
        super().__init__(message)
