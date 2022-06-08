import os
from contextlib import contextmanager


class LocalFileReader:
    def __init__(self, working_dir=""):
        self.working_dir = working_dir

    @contextmanager
    def load(self, file):
        fp = os.path.join(self.working_dir, file)
        f = open(fp, "rb")
        try:
            yield f
        finally:
            f.close()
