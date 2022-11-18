import logging
import os

from boto3.session import Session
from botocore.exceptions import ClientError


def get_dir_list(path_list):
    dir_list = sorted(set([os.path.dirname(x['Key']) for x in path_list]))
    print(dir_list)


class OSS_OPS:
    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url, region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        self.session = Session(aws_access_key_id, aws_secret_access_key)
        self.s3_client = self.session.client("s3", endpoint_url=endpoint_url, region_name=region_name, use_ssl=False)

    def list_buckets(self):
        response = dict(self.s3_client.list_buckets())
        bucket_list = [x['Name'] for x in response['Buckets']]
        return bucket_list

    def list_object(self, bucket, prefix, delimiter=''):
        obj_list = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix, Delimiter=delimiter)

        for page in pages:
            for obj in page['Contents']:
                obj_list.append(obj)
        return obj_list

    def get_all_dir(self, dirs, bucket, remote_directory):
        dirs.append(remote_directory)
        child_list = set()
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=remote_directory, Delimiter='/')

        for page in pages:
            if 'CommonPrefixes' in page.keys():
                for p in page['CommonPrefixes']:
                    child_list.add(p['Prefix'])

        child_dir_list = sorted(child_list)
        if len(child_dir_list) != 0:
            for child_dir in child_dir_list:
                self.get_all_dir(dirs, bucket, child_dir)

    # def get_all_dir(self, dirs, bucket, remote_directory):
    #     dirs.append(remote_directory)
    #     child_list = self.list_objects(bucket=bucket, remote_directory=remote_directory)
    #     child_dir_list = [x for x in child_list if x.is_dir]
    #     if len(child_dir_list) != 0:
    #         for child_dir in child_dir_list:
    #             self.get_all_dir(dirs, bucket, child_dir.object_name)

    def download_file(self, bucket, remote_file, local_file):
        """
        download a file from s3
        :param bucket: bucket name
        :param remote_file: remote file name
        :param local_file: local file name
        :return:
        """
        try:
            self.s3_client.download_file(bucket, remote_file, local_file)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def upload_file(self, local_file, bucket, remote_file=None):
        """
        upload a local file to s3
        :param local_file: file to upload
        :param bucket: bucket to upload to
        :param remote_file: destination file name to be saved
        :return:
        """
        if remote_file is None:
            remote_file = local_file
        try:
            self.s3_client.upload_file(local_file, bucket, remote_file, ExtraArgs={"ACL": "public-read"})
        except ClientError as e:
            logging.error(e)
            return False
        return True

    # def list_objects(self, bucket, remote_directory=None):
    #     """
    #     list objects in a bucket
    #     :param bucket:
    #     :return: file list
    #     """
    #     file_list = []
    #     response_generator = self._list_obj_scluster(bucket, remote_directory)
    #     for content in response_generator:
    #         file_list.append(content["Key"])
    #     return file_list

    def _list_obj_scluster(self, bucket, remote_directory=None):
        """
        list objects in a bucket
        :param bucket:
        :return: file_list [file_name]
        """
        marker = None
        file_list = []

        while True:
            list_kwargs = dict(MaxKeys=1000, Bucket=bucket, Prefix=remote_directory)
            if marker:
                list_kwargs['Marker'] = marker
            response = self.s3_client.list_objects(**list_kwargs)
            file_desc = response.get("Contents", [])
            yield from file_desc
            if not response.get("IsTruncated") or len(file_desc) == 0:
                break
            marker = file_desc[-1]['Key']

    def obj_is_exist(self, bukcet, obj_name):
        '''
        check if a s3 object already  exists
        :param bukcet: bucket name
        :param obj_name: object name
        :return: True if exists, else False
        '''
        try:
            self.s3_client.head_object(Bucket=bukcet, Key=obj_name)
        except ClientError:
            return False
        return True

    def download_directory(self, bucket, remote_directory, local_directory):
        """
        download a directory from s3
        :param bucket: bucket name
        :param remote_directory: remote directory name
        :param local_directory: local directory name
        :return:
        """

        if not os.path.exists(local_directory):
            os.makedirs(local_directory)

        try:
            file_list = self.list_objects(bucket, remote_directory)
            for file in file_list:
                if file.startswith(remote_directory):
                    file_name = file.replace(remote_directory, "").replace("/", "")
                    local_file = os.path.join(local_directory, file_name)
                    self.download_file(bucket, file, local_file)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def create_directory(self, bucket, directory):
        """
        create a directory in s3
        :param bucket: bucket name
        :param directory: directory name
        :return:
        """
        try:
            self.s3_client.put_object(Bucket=bucket, Key=(directory + "/"))
        except ClientError as e:
            logging.error(e)
            return False
        return True


if __name__ == '__main__':
    aws_access_key_id = "ailabminio"
    aws_secret_access_key = "123123123"
    endpoint_url = "https://10.140.0.94:9800"
    region_name = "ailab"

    s3_client = OSS_OPS(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                        endpoint_url=endpoint_url, region_name=region_name)

    # print(s3_client.list_buckets())
    # obj_list = s3_client.list_object('testdata', 'test_data/', '/')
    # print(len(obj_list))
    # print(get_dir_list(obj_list))
    # for obj in obj_list:
    #     print(obj)
    # t = ['test_data/', 'test_data/1/', 'test_data/1/2/', 'test_data/1/2/4/', 'test_data/1/5/', 'test_data/3/',
    #      'test_data/3/6/', 'test_data/3/6/7/']

    # response = s3_client.s3_client.list_objects_v2(Bucket='dsdldata', Prefix='CIFAR-10/', Delimiter='/')
    # print(response)
    # for prefix in response['CommonPrefixes']:
    #     print(prefix['Prefix'][:-1])

    dl = []
    s3_client.get_all_dir(dl, 'testdata', 'test_data/')
    print(dl)
