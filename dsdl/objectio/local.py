import os
from contextlib import contextmanager
from .base import BaseFileReader


class LocalFileReader(BaseFileReader):

    @contextmanager
    def load(self, file):
        fp = os.path.join(self.working_dir, file)
        f = open(fp, "rb")
        try:
            yield f
        finally:
            f.close()
