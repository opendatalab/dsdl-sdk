from contextlib import contextmanager


class BaseFileReader:

    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    @contextmanager
    def load(self, file):
        raise NotImplementedError
