import oss2
import os
from contextlib import contextmanager
from .base import BaseFileReader


class AliOSSFileReader(BaseFileReader):
    """
    该类的作用为读取 阿里云OSS上面的文件
    """

    def __init__(self, working_dir, bucket_name, access_key_id, access_key_secret, endpoint):
        super().__init__(working_dir)
        auth = oss2.Auth(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)

    @contextmanager
    def load(self, file):
        fp = os.path.join(self.working_dir, file)
        object_stream = self.bucket.get_object(fp)
        try:
            yield object_stream
        finally:
            if object_stream.client_crc != object_stream.server_crc:
                print("The CRC checksum between client and server is inconsistent!")
