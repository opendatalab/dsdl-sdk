"""
oss ops module handles s3 operations
"""
import datetime as dt
import logging
import os
import time

import human_readable
from boto3.session import Session
from botocore.exceptions import ClientError
from commons.exceptions import CLIException, ExistCode
from commons.stdio import print_stdout
from loguru import logger


def print_progress(iteration,
                   total,
                   start_time,
                   prefix='',
                   suffix='',
                   decimals=1,
                   bar_length=100):
    """
    Call in a loop to create a terminal progress bar
    @param iteration:   - Required  : current iteration (Int)
    @param total:       - Required  : total iterations (Int)
    @param start_time:  - Required  : process start time (Float)
    @param prefix:      - Optional  : prefix string (Str)
    @param suffix:      - Optional  : suffix string (Str)
    @param decimals:    - Optional  : positive number of decimals in percent complete (Int)
    @param bar_length:  - Optional  : character length of bar (Int)
    @return:
    """
    import sys
    format_str = "{0:." + str(decimals) + "f}"
    percent = format_str.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    dur = time.perf_counter() - start_time
    avg_speed = iteration / dur
    est_seconds = (total - iteration) // max(1, avg_speed)  # TODO 改为瞬时速度的评估
    delta = dt.timedelta(seconds=est_seconds)
    est_tm = human_readable.precise_delta(delta,
                                          suppress=["days"],
                                          formatting='%.0f')
    sys.stdout.write('\r%s |%s| %s%s, Eta %s                  ' %
                     (prefix, bar, percent, '%', est_tm))
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


class OssClient:
    """
    S3 connection client
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url,
                 region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        self.session = Session(aws_access_key_id, aws_secret_access_key)
        self.s3_client = self.session.client("s3",
                                             endpoint_url=endpoint_url,
                                             region_name=region_name,
                                             use_ssl=False)

    def list_buckets(self):
        """
        List all the bucket names
        @return: A list of bucket names
        """
        response = dict(self.s3_client.list_buckets())
        bucket_list = [x['Name'] for x in response['Buckets']]
        return bucket_list

    def list_objects(self, bucket, prefix, delimiter=''):
        """
        List all objects in a given bucket start with a given prefix
        @param bucket:
        @param prefix:
        @param delimiter:
        @return:
        """
        obj_list = []
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket,
                                   Prefix=prefix,
                                   Delimiter=delimiter)

        for page in pages:
            if 'Contents' in page.keys():
                for obj in page['Contents']:
                    obj_list.append(obj)
        return obj_list

    def get_dir_list(self, bucket, remote_directory):
        """
        List directories in a remote directory
        @param bucket:
        @param remote_directory:
        @return:
        """
        child_dir_list = set()
        paginator = self.s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket,
                                   Prefix=remote_directory,
                                   Delimiter='/')

        for page in pages:
            if 'CommonPrefixes' in page.keys():
                for p in page['CommonPrefixes']:
                    child_dir_list.add(p['Prefix'])

        return sorted(child_dir_list)

    def __get_recursive_dir(self, dirs, bucket, remote_directory):
        """
        A recursive func to get all directories in a remote directory
        @param dirs:
        @param bucket:
        @param remote_directory:
        @return:
        """
        dirs.append(remote_directory)
        # child_list = set()
        # paginator = self.s3_client.get_paginator('list_objects_v2')
        # pages = paginator.paginate(Bucket=bucket, Prefix=remote_directory, Delimiter='/')
        #
        # for page in pages:
        #     if 'CommonPrefixes' in page.keys():
        #         for p in page['CommonPrefixes']:
        #             child_list.add(p['Prefix'])

        child_dir_list = self.get_dir_list(bucket, remote_directory)
        if len(child_dir_list) != 0:
            for child_dir in child_dir_list:
                self.__get_recursive_dir(dirs, bucket, child_dir)

    def get_recursive_dir_list(self, bucket, remote_directory):
        """
        Call a recursive func to get all directories in a remote directory
        @param bucket:
        @param remote_directory:
        @return:
        """
        dir_list = []
        self.__get_recursive_dir(dir_list, bucket, remote_directory)
        dir_list = [dir[len(remote_directory):] for dir in dir_list]
        return dir_list

    def download_file(self, bucket, remote_file, local_file):
        """
        download a file from s3
        :param bucket: bucket name
        :param remote_file: remote file name
        :param local_file: local file name
        :return:
        """
        try:
            if not os.path.exists(local_file):
                self.s3_client.download_file(bucket, remote_file, local_file)
        except ClientError as e:
            logging.error(e)
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
        print_stdout("preparing...")
        dirs_list = self.get_recursive_dir_list(
            bucket=bucket, remote_directory=remote_directory)
        for d in dirs_list:
            path = os.path.join(local_directory, d)
            if not os.path.exists(path):
                os.mkdir(path)

        print_stdout("start download...")

        # print(bucket)
        # print(remote_directory)
        file_list = self.list_objects(bucket, remote_directory)
        process = 0
        file_number = len(file_list)
        start_time = time.perf_counter()

        # print_progress(process, file_number, start_time, prefix='Downloading', suffix='Complete',
        #                bar_length=50)

        for file in file_list:
            file_name = file['Key']
            local_file = os.path.join(local_directory,
                                      file_name[len(remote_directory):])
            if not os.path.exists(local_file):
                self.download_file(bucket, file_name, local_file)
            process += 1
            print_progress(process,
                           file_number,
                           start_time,
                           prefix='Download',
                           suffix='Complete',
                           bar_length=50)

        print_stdout('Download Complete')

    def download_list(self, bucket, media_list, remote_directory,
                      local_directory):
        """
        Download a directory from s3
        @param bucket: bucket name
        @param media_list: a list of media files to download
        @param remote_directory: remote directory name
        @param local_directory: local directory name
        @return:
        """
        print_stdout("preparing...")
        dirs_list = self.get_recursive_dir_list(
            bucket=bucket, remote_directory=remote_directory)
        # print(dirs_list)
        for d in dirs_list:
            path = os.path.join(local_directory, d)
            if not os.path.exists(path):
                os.mkdir(path)

        print_stdout("start download...")

        process = 0
        file_number = len(media_list)
        start_time = time.perf_counter()

        print_progress(process,
                       file_number,
                       start_time,
                       prefix='Downloading',
                       suffix='Complete',
                       bar_length=50)

        for media in media_list:
            file_key = remote_directory + media
            local_file = os.path.join(local_directory, media)
            if not os.path.exists(local_file):
                self.download_file(bucket, file_key, local_file)
            process += 1
            print_progress(process,
                           file_number,
                           start_time,
                           prefix='Download',
                           suffix='Complete',
                           bar_length=50)

        print_stdout('Download Complete')

    def get_sum_size(self, bucket, file_key_list):
        sum = 0
        for key in file_key_list:
            data = self.s3_client.head_object(Bucket=bucket, Key=key)
            size = int(
                data['ResponseMetadata']['HTTPHeaders']['content-length'])
            sum += size
        return sum

    def read_file(self, bucket, remote_file):
        """

        @param bucket:
        @param remote_file:
        @return:
        """
        data = self.s3_client.get_object(Bucket=bucket, Key=remote_file)
        contents = data['Body'].read()
        return contents.decode("utf-8")

    def list_datasets(self, bucket):
        """
        Return a list of dataset names
        @return:
        """
        dataset_list = [
            x.replace('/', '') for x in self.get_dir_list(bucket, '')
        ]
        return dataset_list

    def is_dataset_remote_exist(self, bucket, dataset_name):
        """

        @param bucket:
        @param dataset_name:
        @return:
        """
        dataset_list = self.list_datasets(bucket)
        if dataset_name in dataset_list:
            return True
        else:
            return False

    def list_splits(self, bucket, dataset_name):
        """

        @param bucket:
        @param dataset_name:
        @return:
        """
        if not self.is_dataset_remote_exist(bucket, dataset_name):
            print_stdout("The dataset %s does not exist in remote repo" %
                         dataset_name)
            # logger.info("The dataset %s does not exist in remote repo" % dataset_name)
            exit()
        else:
            parquet_prefix = dataset_name + "/parquet/"
            parquet_name_list = [
                x['Key'][len(parquet_prefix):].replace('.parquet', '')
                for x in self.list_objects(bucket, parquet_prefix)
                if str(x['Key']).endswith(".parquet")
            ]
            return parquet_name_list

    def is_split_remote_exist(self, bucket, dataset_name, split_name):
        """

        @param bucket:
        @param dataset_name:
        @param split_name:
        @return:
        """
        split_list = self.list_splits(bucket, dataset_name)
        if split_name in split_list:
            return True
        else:
            return False

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
            self.s3_client.upload_file(local_file,
                                       bucket,
                                       remote_file,
                                       ExtraArgs={"ACL": "public-read"})
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

    # def _list_obj_scluster(self, bucket, remote_directory=None):
    #     """
    #     list objects in a bucket
    #     :param bucket:
    #     :return: file_list [file_name]
    #     """
    #     marker = None
    #     file_list = []
    #
    #     while True:
    #         list_kwargs = dict(MaxKeys=1000, Bucket=bucket, Prefix=remote_directory)
    #         if marker:
    #             list_kwargs['Marker'] = marker
    #         response = self.s3_client.list_objects(**list_kwargs)
    #         file_desc = response.get("Contents", [])
    #         yield from file_desc
    #         if not response.get("IsTruncated") or len(file_desc) == 0:
    #             break
    #         marker = file_desc[-1]['Key']

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

    # def download_directory(self, bucket, remote_directory, local_directory):
    #     """
    #     download a directory from s3
    #     :param bucket: bucket name
    #     :param remote_directory: remote directory name
    #     :param local_directory: local directory name
    #     :return:
    #     """
    #
    #     if not os.path.exists(local_directory):
    #         os.makedirs(local_directory)
    #
    #     try:
    #         file_list = self.list_objects(bucket, remote_directory)
    #         for file in file_list:
    #             if file.startswith(remote_directory):
    #                 file_name = file.replace(remote_directory, "").replace("/", "")
    #                 local_file = os.path.join(local_directory, file_name)
    #                 self.download_file(bucket, file, local_file)
    #     except ClientError as e:
    #         logging.error(e)
    #         return False
    #     return True

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
    endpoint_url = "http://10.140.0.94:9800"
    region_name = "ailab"

    s3_client = OssClient(aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          endpoint_url=endpoint_url,
                          region_name=region_name)

    # print(s3_client.list_buckets())
    # obj_list = s3_client.list_objects('testdata', 'test_data/', '/')
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

    # s3_client.download_directory('dsdldata', 'Fashion-MNIST/', 'D:\\DSDL_DATA')

    # print(s3_client.get_recursive_dir_list('testdata', 'test_data/'))
    # print(len(s3_client.list_objects('dsdldata', 'CIFAR-10/media/')))
    # obj_list = s3_client.read_file('dsdldata', 'CIFAR-10/parquet/dataset.yaml')
    # print(obj_list)
    # print(s3_client.list_datasets("dsdldata"))
    # print(s3_client.list_splits("dsdldata", "STL-10"))
    # print(s3_client.is_split_remote_exist("dsdldata", "STL-101", "unlabeled1"))
    print(
        s3_client.get_sum_size("dsdldata", [
            'CIFAR-10-Auto/media/000000007605.png',
            'CIFAR-10-Auto/media/000000009822.png'
        ]))
    # print(s3_client.get_dir_list('dsdldata', ''))
