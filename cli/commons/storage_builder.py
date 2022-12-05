import re
import shutil
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from boto3 import Session
from commons.exceptions import CLIException, ExistCode

from dsdlsdk.storage import LocalDiskStorage, S3Storage, SftpStorage, Storage


class StorageBuilder(object):

    @staticmethod
    def build_by_name(storage_name: str, config: Dict) -> Storage:
        """
        Build storage client by name
        Args:
            storage_name:
            config:

        Returns:

        """
        if "storage" in config.keys():
            storage_config = config['storage'].get(storage_name, None)
            if storage_config is not None:
                path = storage_config.get('path', None)
                if path is not None:
                    if path.startswith('s3://'):
                        endpoint = storage_config.get('endpoint', None)
                        access_key = storage_config.get('ak', None)
                        secret_key = storage_config.get('sk', None)
                        return S3Storage(path, endpoint, access_key,
                                         secret_key)
                    elif path.startswith('sftp://'):
                        return SftpStorage()
                    else:
                        return LocalDiskStorage()
                else:
                    raise CLIException(ExistCode.NOT_SUPPORTED_STORE_PATH,
                                       f'unsupported storage path: {path}')
            else:
                raise CLIException(
                    ExistCode.STORAGE_NAME_NOT_EXIST,
                    f"storage name key `{storage_name}' not found in config")
        else:
            raise CLIException(
                ExistCode.STORAGE_NOT_EXIST,
                f"storage named `{storage_name}' not found in config")


if __name__ == "__main__":
    s: Storage = StorageBuilder.build_by_name(
        "s3", {
            "storage": {
                "s3": {
                    "endpoint": "http://10.140.0.94:9800",
                    "access_key": "ailabminio",
                    "secret_key": "123123123",
                    "path": "s3://testdata"
                }
            }
        })
    b = s.remove_tree("s3://testdata/.dsdl")
    print(b)
