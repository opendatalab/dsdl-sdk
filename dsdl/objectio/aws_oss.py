from boto3.session import Session
import os
from contextlib import contextmanager
from .base import BaseFileReader


class AwsOSSFileReader(BaseFileReader):

    def __init__(self, working_dir, bucket_name, access_key_id, access_key_secret, endpoint, region):
        super().__init__(working_dir)
        self.bucket_name = bucket_name
        self.session = Session(access_key_id, access_key_secret)
        self.s3_client = self.session.client("s3",
                                             endpoint_url=endpoint,
                                             region_name=region,
                                             use_ssl=False)

    @contextmanager
    def load(self, file):
        fp = f"{self.working_dir.strip('/')}/{file.strip('/')}"
        try:
            try:
                data = self.s3_client.get_object(Bucket=self.bucket_name, Key=fp)
                contents = data['Body']
            except Exception as e:
                raise RuntimeError(f"{e}. Failed to read '{fp}' from bucket '{self.bucket_name}'.")
            yield contents
        finally:
            pass
