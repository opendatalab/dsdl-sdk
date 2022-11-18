import os
import logging
from minio import Minio
import time

bucket_name = 'dsdldata'


class OSS_OPS:
    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url, region_name):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.endpoint_url = endpoint_url
        self.region_name = region_name

        self.s3_client = Minio(endpoint=self.endpoint_url, access_key=self.aws_access_key_id,
                               secret_key=self.aws_secret_access_key, region=self.region_name, secure=False)

    def download_file(self, bucket, remote_file, local_file):
        """
        download a file from s3
        :param bucket: bucket name
        :param remote_file: remote file name
        :param local_file: local file name
        :return:
        """
        try:
            self.s3_client.fget_object(bucket, remote_file, local_file)
        except Exception as e:
            logging.error(e)
            return False
        return True

    def list_objects(self, bucket, remote_directory='', recursive=False):
        """
        list objects in a bucket
        :param bucket:
        :return:
        """
        obj_list = self.s3_client.list_objects(
            bucket_name=bucket,
            prefix=remote_directory,
            recursive=recursive,
        )
        obj_list = list(obj_list)
        # print("total file number: %d" % len(obj_list))
        return obj_list

    def get_all_dir(self, dirs, bucket, remote_directory):
        dirs.append(remote_directory)
        child_list = self.list_objects(bucket=bucket, remote_directory=remote_directory)
        child_dir_list = [x for x in child_list if x.is_dir]
        if len(child_dir_list) != 0:
            for child_dir in child_dir_list:
                self.get_all_dir(dirs, bucket, child_dir.object_name)

    def print_progress(self, iteration, total, start_time, prefix='', suffix='', decimals=1, bar_length=100):
        """
        Call in a loop to create a terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            barLength   - Optional  : character length of bar (Int)
        """
        import sys
        format_str = "{0:." + str(decimals) + "f}"
        percent = format_str.format(100 * (iteration / float(total)))
        filled_length = int(round(bar_length * iteration / float(total)))
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        dur = time.perf_counter() - start_time
        sys.stdout.write('\r%s |%s| %ds %s%s %s' % (prefix, bar, dur, percent, '%', suffix)),
        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()

    def download_directory(self, bucket, remote_directory, local_directory):
        """
        download a directory from s3
        :param bucket: bucket name
        :param remote_directory: remote directory name
        :param local_directory: local directory name
        :return:
        """
        print("check local path...")
        dirs_list = []
        self.get_all_dir(dirs=dirs_list, bucket=bucket, remote_directory=remote_directory)
        for d in dirs_list:
            path = os.path.join(local_directory, d)
            if not os.path.exists(path):
                os.mkdir(path)

        print("start download...")
        try:
            file_list = self.list_objects(bucket, remote_directory, recursive=True)
            process = 0
            file_number = len(file_list)
            start_time = time.perf_counter()

            self.print_progress(process, file_number, start_time, prefix='Downloading', suffix='Complete',
                                bar_length=50)

            for file in file_list:
                local_file = os.path.join(local_directory, file.object_name)
                self.download_file(bucket, file.object_name, local_file)
                process += 1
                self.print_progress(process, file_number, start_time, prefix='Download', suffix='Complete',
                                    bar_length=50)
        except Exception as e:
            logging.error(e)
            return False
        print('Download Complete')
        return True


if __name__ == '__main__':
    aws_access_key_id = "ailabminio"
    aws_secret_access_key = "123123123"
    endpoint_url = "10.140.0.94:9800"
    region_name = "ailab"
    minio_client = OSS_OPS(endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id,
                           aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    # objs = minio_client.list_objects('dsdldata', 'CIFAR-10/parquet')
    # for obj in objs:
    #     print(obj.object_name, obj.is_dir)

    dir_list = []
    minio_client.get_all_dir(dir_list, 'testdata', 'test_data/')
    print(dir_list)

    # for d in dir_list:
    #     path = os.path.join('D:\\', d)
    #     print(path)
    #     if not os.path.exists(path):
    #         os.mkdir(path)

    # minio_client.download_file('dsdldata', 'CIFAR-10/media/000000042381.png', 'D:\DSDL_DATA\CIFAR-10/media/000000042381.png')
    # minio_client.download_directory('dsdldata', 'CIFAR-10/', 'D:\\DSDL_DATA')
