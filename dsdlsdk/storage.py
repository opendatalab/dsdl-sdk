import os.path
import re
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from boto3 import Session

from dsdlsdk.exception.exception import DatasetPathNotExists


class Storage(ABC):
    """
    对config里支持的本地存储方式的一种抽象
    """

    @abstractmethod
    def remove_tree(self, path: str) -> bool:
        """
        删除整个目录
        Returns:

        """
        pass


class LocalDiskStorage(Storage):

    def remove_tree(self, local_path: str) -> bool:
        if not os.path.exists(local_path):
            raise DatasetPathNotExists(f"local path {local_path} not exist")
        try:
            shutil.rmtree(local_path, ignore_errors=True)
            return True
        except Exception as e:
            return False


class S3Storage(Storage):

    def __init__(self, path: str, endpoint: str, access_key: str,
                 secret_key: str):
        self.path = path
        self.bucket, _ = self.__split_s3_path(path)
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        # build s3 client
        self.s3cli = self.__build_s3_cli()

    def remove_tree(self, s3_path: str) -> bool:
        bucket, obj_key = self.__split_s3_path(s3_path)
        for files in self.list_objects(bucket, obj_key):
            self.s3cli.delete_object(Bucket=bucket, Key=files['Key'])

        return True

    def __build_s3_cli(self):
        session = Session(self.access_key, self.secret_key)
        s3_client = session.client("s3",
                                   endpoint_url=self.endpoint,
                                   use_ssl=False)
        return s3_client

    def __split_s3_path(self, s3_path: str) -> Tuple[str, str]:
        """

        Args:
            s3_path:

        Returns:

        """
        s3_path_pattern = re.compile("^s3://([^/]+)(?:/(.*))?$")
        m = s3_path_pattern.match(s3_path)
        if m is None:
            return "", ""
        return m.group(1), (m.group(2) or "")

    def list_objects(self, bucket, prefix, delimiter=''):
        """

        Args:
            bucket:
            prefix:
            delimiter:

        Returns:

        """
        marker = None
        while True:
            list_kwargs = dict(MaxKeys=1000, Bucket=bucket, Prefix=prefix)
            if marker:
                list_kwargs['Marker'] = marker
            response = self.s3cli.list_objects(**list_kwargs)
            contents = response.get("Contents", [])
            yield from contents
            if not response.get("IsTruncated") or len(contents) == 0:
                break
            marker = contents[-1]['Key']


class SftpStorage(Storage):

    def remove_tree(self, path: str) -> bool:
        raise NotImplementedError

    def __init__(self):
        raise NotImplementedError
