import os
import json
from boto3.session import Session
from collections import namedtuple
from ...objectio import AwsOSSFileReader
from .base_studio_view import BaseStudioView

s3_config = namedtuple("s3_config", ("ak", "sk", "endpoint", "region", "bucket"))
default_cfg = s3_config("ailabminio", "123123123", "http://10.140.0.94:9800", "ailab", "dsdldata")


class RemoteStudioView(BaseStudioView):

    def __init__(self, dataset_name, task_type, n=None, shuffle=False):
        self.remote_cfg = self._get_s3_config(dataset_name)
        os.system(f"odl-cli get {dataset_name} --label")
        super().__init__(dataset_name, task_type, n=n, shuffle=shuffle)

    def _init_file_reader(self):
        if self.remote_cfg is None:
            raise RuntimeError(f"remote dataset {self.dataset_name} not exist.")
        return AwsOSSFileReader(self.dataset_name,
                                self.remote_cfg.bucket,
                                self.remote_cfg.ak,
                                self.remote_cfg.sk,
                                self.remote_cfg.endpoint,
                                self.remote_cfg.region)

    def _get_s3_config(self, dataset_name):
        config_path = os.path.join(os.path.expanduser("~"), ".dsdl", "dsdl.json")
        with open(config_path, "r") as f:
            storage_info = json.load(f)["storage"]
        cfg_lst = [default_cfg]
        for storage in storage_info.values():
            if "ak" in storage and "sk" in storage and "endpoint" in storage:
                cfg = s3_config(storage["ak"], storage["sk"], storage["endpoint"],
                                storage.get("region", default_cfg.region), storage.get("bucket", default_cfg.bucket))
                cfg_lst.append(cfg)
        res = None
        for cfg in cfg_lst:
            session = Session(cfg.ak, cfg.sk)
            client = session.client("s3", endpoint_url=cfg.endpoint, region_name=cfg.region, use_ssl=False)
            if self.is_dataset_remote_exist(client, cfg.bucket, dataset_name):
                res = cfg
                break
        return res

    @staticmethod
    def is_dataset_remote_exist(client, bucket, dataset_name):

        child_dir_list = set()
        paginator = client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix="", Delimiter='/')

        for page in pages:
            if 'CommonPrefixes' in page.keys():
                for p in page['CommonPrefixes']:
                    child_dir_list.add(p['Prefix'])

        dataset_list = [_.replace('/', '') for _ in child_dir_list]

        return dataset_name in dataset_list
