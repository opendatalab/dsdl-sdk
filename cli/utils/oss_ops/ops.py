import os
import logging
from boto3.session import Session
from botocore.exceptions import ClientError


class OSS_OPS:
    def __init__(self, aws_access_key_id,aws_secret_access_key,endpoint_url,region_name):
        aws_access_key_id = aws_access_key_id
        aws_secret_access_key = aws_secret_access_key
        endpoint_url = endpoint_url
        region_name = region_name

        session = Session(aws_access_key_id, aws_secret_access_key)
        self.s3_client = session.client("s3", endpoint_url=endpoint_url, region_name=region_name)

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

    def list_objects(self, bucket, remote_directory=None):
        """
        list objects in a bucket
        :param bucket:
        :return: file list
        """
        file_list = []
        response_generator = self._list_obj_scluster(bucket, remote_directory)
        for content in response_generator:
            file_list.append(content["Key"])
        return file_list

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
            if not response.get("IsTruncated") or len(file_desc)==0:
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
