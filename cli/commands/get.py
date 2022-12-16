"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""
import os
import shutil

import yaml
from commands.cmdbase import CmdBase
from commands.const import DEFAULT_LOCAL_STORAGE_PATH, DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from commons.exceptions import CLIException, ExistCode
from commons.stdio import print_stdout
from loguru import logger
from utils import admin, query
from utils.oss_ops import ops

default_path = DEFAULT_LOCAL_STORAGE_PATH

aws_access_key_id = query.aws_access_key_id
aws_secret_access_key = query.aws_secret_access_key
endpoint_url = query.endpoint_url
region_name = query.region_name
default_bucket = query.default_bucket


class Get(CmdBase):
    """
    Example command
    """

    aws_access_key_id = "ailabminio"
    aws_secret_access_key = "123123123"
    endpoint_url = "10.140.0.94:9800"
    region_name = "ailab"

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        select_parser = subparsers.add_parser(
            'get',
            help='download data from repo',
            example="get.example",
            description='download data from repo',
        )

        select_parser.add_argument(
            "dataset_name",
            action=EnvDefaultVar,
            envvar=DSDL_CLI_DATASET_NAME,
            type=str,
            help=
            'dataset name. The arg is optional only when the default dataset name was set by cd command.',
        )
        select_parser.add_argument(
            "-s",
            "--split",
            type=str,
            help=
            'split name of the dataset, such as train/test/validation split.',
            metavar='')
        # select_parser.add_argument("-p", "--part", type=str,
        #                            help='The part name of the dataset, such as label/media.',
        #                            metavar='')
        select_parser.add_argument("-o",
                                   "--output",
                                   type=str,
                                   help='target saving path.',
                                   metavar='')
        select_parser.add_argument(
            "--label",
            action="store_true",
            help='download label data only.',
        )

        return select_parser

    def cmd_entry(self, cmdargs, config, *args, **kwargs):
        """
        Entry point for the command

        Args:
            self:
            cmdargs:
            config:

        Returns:

        """
        conf_dict = admin.get_config_dict()

        # get params
        dataset_name = cmdargs.dataset_name
        split_name = cmdargs.split
        output = cmdargs.output if cmdargs.output else 'default'
        try:
            output_path = conf_dict['storage'][
                cmdargs.output]['path'] if cmdargs.output else default_path
        except Exception as e:
            error_info = str(
                e
            ) + "\n" + "get output path error, output refers to the storage name, the storage path and name are required to be set with config command"
            raise CLIException(ExistCode.STORAGE_NOT_EXIST, error_info)
        label_flag = cmdargs.label

        # construct class of s3 client
        s3_client = ops.OssClient(endpoint_url=endpoint_url,
                                  aws_access_key_id=aws_access_key_id,
                                  aws_secret_access_key=aws_secret_access_key,
                                  region_name=region_name)

        # construct class of sqlite client
        db_client = admin.DBClient()

        # get dataset list in remote repo
        if not s3_client.is_dataset_remote_exist(default_bucket, dataset_name):
            reminder = "there is no dataset named %s in remote repo" % dataset_name
            logger.info(reminder)
            raise CLIException(ExistCode.DATASET_NOT_EXIST_REMOTE, reminder)
        else:
            self.__check_disk_usage(dataset_name, output_path,
                                    s3_client)  # check local disk usage

        # dataset & split flag of existence
        dataset_exist_flag = db_client.is_dataset_local_exist(dataset_name)
        split_exist_flag = db_client.is_split_local_exist(
            dataset_name, split_name)

        # get dataset dir/parquet dir/s3 parquet prefix/media dir/s3 media prefix
        dataset_dir = os.path.join(
            output_path, dataset_name) if not db_client.get_local_dataset_path(
                dataset_name) else db_client.get_local_dataset_path(
                    dataset_name)
        s3_parquet_prefix = dataset_name + "/parquet/"
        parquet_dir = os.path.join(dataset_dir, 'parquet')
        s3_media_prefix = dataset_name + "/media/"
        media_dir = os.path.join(dataset_dir, 'media')
        s3_yml_prefix = dataset_name + "/yml/"
        yml_dir = os.path.join(dataset_dir, 'yml')
        remote_split_list = s3_client.list_splits(default_bucket, dataset_name)
        dataset_info_path = os.path.join(parquet_dir, 'dataset.yaml')

        # get the whole dataset
        if not split_name:
            label_exist_flag = db_client.is_dataset_label_downloaded(
                dataset_name)
            media_exist_flag = db_client.is_dataset_media_downloaded(
                dataset_name)

            # check whether the dataset locally exists
            if dataset_exist_flag:
                if label_exist_flag and media_exist_flag:
                    reminder = 'The dataset "%s" has already been all downloaded in %s.' % (
                        dataset_name, dataset_dir)
                    print_stdout(reminder)
                    exit()

            # download a new dataset
            if not dataset_exist_flag:
                if not os.path.exists(dataset_dir):
                    os.mkdir(dataset_dir)
                print_stdout("saving to %s" % dataset_dir)

                # download dataset
                if not label_flag:
                    s3_client.download_directory(default_bucket,
                                                 dataset_name + '/',
                                                 dataset_dir)
                else:
                    print_stdout("parquet folder: ")
                    s3_client.download_directory(default_bucket,
                                                 s3_parquet_prefix,
                                                 parquet_dir)
                    print_stdout("yml folder: ")
                    s3_client.download_directory(default_bucket, s3_yml_prefix,
                                                 yml_dir)
                print_stdout("register local dataset...")

                # get meta info of dataset to insert into sqlite
                parquet_list = [
                    obj['Key'].split("/")[-1]
                    for obj in s3_client.list_objects(
                        default_bucket, dataset_name + '/parquet/')
                    if str(obj['Key']).endswith(".parquet")
                ]

                with open(dataset_info_path, 'r') as f:
                    dataset_dict = yaml.safe_load(f)

                if 'task' in dataset_dict['dsdl_meta']['dataset']['meta'].keys():
                    task_type = dataset_dict['dsdl_meta']['dataset']['meta']['task']
                if 'Task' in dataset_dict['dsdl_meta']['dataset']['meta'].keys():
                    task_type = dataset_dict['dsdl_meta']['dataset']['meta']['Task']
                stat = dataset_dict['statistics']
                dataset_media_num = stat['dataset_stat']['media_num']
                dataset_media_size = stat['dataset_stat']['media_size']

                if not label_flag:
                    db_client.register_dataset(dataset_name, task_type, output,
                                               dataset_dir, 1, 1,
                                               dataset_media_num,
                                               dataset_media_size)

                    # get meta info of split to insert into sqlite
                    for split in parquet_list:
                        stat = query.ParquetReader(
                            os.path.join(dataset_dir, 'parquet',
                                         split)).get_metadata()
                        split_media_num = stat['split_stat']['media_num']
                        split_media_size = stat['split_stat']['media_size']
                        db_client.register_split(dataset_name,
                                                 split.replace(".parquet",
                                                               ""), 'official',
                                                 1, 1, split_media_num,
                                                 split_media_size)
                else:
                    db_client.register_dataset(dataset_name, task_type, output,
                                               dataset_dir, 1, 0,
                                               dataset_media_num,
                                               dataset_media_size)

                    # get meta info of split to insert into sqlite
                    for split in parquet_list:
                        stat = query.ParquetReader(
                            os.path.join(dataset_dir, 'parquet',
                                         split)).get_metadata()
                        split_media_num = stat['split_stat']['media_num']
                        split_media_size = stat['split_stat']['media_size']
                        db_client.register_split(dataset_name,
                                                 split.replace(".parquet",
                                                               ""), 'official',
                                                 1, 0, split_media_num,
                                                 split_media_size)

            # dataset has already been partly downloaded
            else:
                print_stdout("check label data...")
                if label_exist_flag:
                    print_stdout("label data has been all downloaded")
                else:
                    download_split_list = [
                        split_name for split_name in remote_split_list
                        if not db_client.is_split_local_exist(
                            dataset_name, split_name)
                    ]
                    download_file_list = [
                        split_name + '.parquet'
                        for split_name in download_split_list
                    ]
                    if len(download_file_list) == 0:
                        print_stdout("label data has been all downloaded")
                    else:
                        print_stdout("download missing label files")
                        s3_client.download_list(default_bucket,
                                                download_file_list,
                                                s3_parquet_prefix, parquet_dir)

                        print_stdout("register local split...")
                        for split in download_file_list:
                            stat = query.ParquetReader(
                                os.path.join(parquet_dir,
                                             split)).get_metadata()
                            split_media_num = stat['split_stat']['media_num']
                            split_media_size = stat['split_stat']['media_size']
                            db_client.register_split(
                                dataset_name, split.replace(".parquet",
                                                            ""), 'official', 1,
                                1, split_media_num, split_media_size)

                print_stdout("check media data...")
                if media_exist_flag:
                    print_stdout("media data has been all downloaded")
                else:
                    if not os.path.exists(media_dir):
                        os.mkdir(media_dir)
                    print_stdout("download missing media files")
                    s3_client.download_directory(default_bucket,
                                                 s3_media_prefix, media_dir)

                s3_client.download_directory(default_bucket, s3_yml_prefix,
                                             yml_dir)

                print_stdout("update dataset info...")
                try:
                    db_client.cursor.execute(
                        "update dataset set label_data=?, media_data=?, updated_time=datetime('now','localtime') where dataset_name=?",
                        [1, 1, dataset_name])
                    db_client.cursor.execute(
                        "update split set label_data=?, media_data=?, updated_time=datetime('now','localtime') where dataset_name=?",
                        [1, 1, dataset_name])
                    db_client.conn.commit()
                except Exception as e:
                    raise CLIException(ExistCode.SQLITE_OPERATION_ERROR,
                                       str(e))

        # download a split of dataset
        else:
            if split_name in remote_split_list:

                s3_parquet_key = s3_parquet_prefix + split_name + '.parquet'
                s3_datainfo_key = s3_parquet_prefix + 'dataset.yaml'
                parquet_path = db_client.get_local_split_path(dataset_name, split_name) \
                    if split_exist_flag else os.path.join(parquet_dir, split_name + '.parquet')

                if not split_exist_flag:
                    if not os.path.exists(dataset_dir):
                        os.mkdir(dataset_dir)
                    if not os.path.exists(parquet_dir):
                        os.mkdir(parquet_dir)

                    s3_client.download_file(default_bucket, s3_parquet_key,
                                            parquet_path)
                    s3_client.download_file(default_bucket, s3_datainfo_key,
                                            dataset_info_path)
                    parquet_reader = query.ParquetReader(parquet_path)
                    s3_media_keys = parquet_reader.select(
                        'image')['image'].tolist()

                    if not label_flag:
                        if not os.path.exists(media_dir):
                            os.mkdir(media_dir)

                        s3_client.download_list(default_bucket, s3_media_keys,
                                                dataset_name + "/",
                                                dataset_dir)

                    print_stdout("register local split...")
                    if not dataset_exist_flag:
                        with open(dataset_info_path, 'r') as f:
                            dataset_dict = yaml.safe_load(f)

                        if 'task' in dataset_dict['dsdl_meta']['dataset']['meta'].keys():
                            task_type = dataset_dict['dsdl_meta']['dataset']['meta']['task']
                        if 'Task' in dataset_dict['dsdl_meta']['dataset']['meta'].keys():
                            task_type = dataset_dict['dsdl_meta']['dataset']['meta']['Task']
                        stat = dataset_dict['statistics']
                        dataset_media_num = stat['dataset_stat']['media_num']
                        dataset_media_size = stat['dataset_stat']['media_size']

                        db_client.register_dataset(dataset_name, task_type,
                                                   output, dataset_dir, 0, 0,
                                                   dataset_media_num,
                                                   dataset_media_size)

                        stat = query.ParquetReader(parquet_path).get_metadata()
                        split_media_num = stat['split_stat']['media_num']
                        split_media_size = stat['split_stat']['media_size']
                        if label_flag:
                            db_client.register_split(dataset_name, split_name,
                                                     'official', 1, 0,
                                                     split_media_num,
                                                     split_media_size)
                        else:
                            db_client.register_split(dataset_name, split_name,
                                                     'official', 1, 1,
                                                     split_media_num,
                                                     split_media_size)
                    else:
                        stat = query.ParquetReader(parquet_path).get_metadata()
                        split_media_num = stat['split_stat']['media_num']
                        split_media_size = stat['split_stat']['media_size']
                        if label_flag:
                            db_client.register_split(dataset_name, split_name,
                                                     'official', 1, 0,
                                                     split_media_num,
                                                     split_media_size)
                        else:
                            db_client.register_split(dataset_name, split_name,
                                                     'official', 1, 1,
                                                     split_media_num,
                                                     split_media_size)

                else:
                    local_db_split_dict = db_client.get_sqlite_dict_list(
                        "select * from split where dataset_name='%s' and split_name='%s'"
                        % (dataset_name, split_name))[0]
                    label_data = local_db_split_dict['label_data']
                    media_data = local_db_split_dict['media_data']
                    if label_data == 1 and media_data == 1:
                        print_stdout("the split has been fully downloaded")
                        exit()
                    elif label_data == 1 and media_data == 0:
                        if label_flag:
                            print_stdout(
                                "label data of the split has been downloaded")
                        else:
                            if not os.path.exists(media_dir):
                                os.mkdir(media_dir)
                            parquet_reader = query.ParquetReader(parquet_path)
                            s3_media_keys = parquet_reader.select(
                                'image')['image'].tolist()
                            s3_client.download_list(default_bucket,
                                                    s3_media_keys,
                                                    dataset_name + "/",
                                                    dataset_dir)
                            print_stdout("update split info...")
                            try:
                                db_client.cursor.execute(
                                    "update split set media_data=?, updated_time=datetime('now','localtime') where dataset_name=? and split_name=?",
                                    [1, dataset_name, split_name])
                                db_client.conn.commit()
                            except Exception as e:
                                raise CLIException(
                                    ExistCode.SQLITE_OPERATION_ERROR, str(e))

            else:
                if not split_exist_flag:
                    reminder = "can not find the split named %s of dataset %s neither in remote repo nor in local storage" % (
                        split_name, dataset_name)
                    logger.info(reminder)
                    raise CLIException(ExistCode.SPLIT_NOT_EXIST, reminder)

                parquet_path = db_client.get_local_split_path(
                    dataset_name, split_name)

                local_db_split_dict = db_client.get_sqlite_dict_list(
                    "select * from split where dataset_name='%s' and split_name='%s'"
                    % (dataset_name, split_name))[0]
                label_data = local_db_split_dict['label_data']
                media_data = local_db_split_dict['media_data']
                if label_data == 1 and media_data == 1:
                    print_stdout("the split has been fully downloaded")
                    exit()
                elif label_data == 1 and media_data == 0:
                    if label_flag:
                        print_stdout(
                            "label data of the split has been downloaded")
                    else:
                        if not os.path.exists(media_dir):
                            os.mkdir(media_dir)
                        parquet_reader = query.ParquetReader(parquet_path)
                        s3_media_keys = parquet_reader.select(
                            'image')['image'].tolist()
                        s3_client.download_list(default_bucket, s3_media_keys,
                                                dataset_name + "/",
                                                dataset_dir)
                        print_stdout("update split info...")
                        try:
                            db_client.cursor.execute(
                                "update split set media_data=?, updated_time=datetime('now','localtime') where dataset_name=? and split_name=?",
                                [1, dataset_name, split_name])
                            db_client.conn.commit()
                        except Exception as e:
                            raise CLIException(
                                ExistCode.SQLITE_OPERATION_ERROR, str(e))

    def __check_disk_usage(self, dataset_name: str, output_path: str,
                           s3_client: ops.OssClient):
        """

        Args:
            dataset_name: uniq dataset name
            output_path: dataset download full path
            s3_client: reuse s3 client

        Returns: None

        """
        # check local disk usage
        # 1. is space less than 10G
        # 2. is space less than the size of the dataset

        if os.path.exists(output_path):  # only check local path
            total, used, free = shutil.disk_usage(output_path)
            # 1.
            if free < 10 * 1024 * 1024 * 1024:
                reminder = "the disk space is less than 10G, please check the disk space"
                logger.warning(reminder)
                raise CLIException(ExistCode.DISK_SPACE_NOT_ENOUGH, reminder)
            # 2.
            # get dataset size from network
            yaml_content = s3_client.read_file(
                default_bucket, f"{dataset_name}/parquet/dataset.yaml")
            dataset_sz_bytes = yaml.safe_load(
                yaml_content)['statistics']['dataset_stat']['media_size']
            if free * 0.96 <= dataset_sz_bytes:
                reminder = "the disk space is less than the size of the dataset, please use config to add another storage path"
                logger.warning(reminder)
                raise CLIException(ExistCode.DISK_SPACE_NOT_ENOUGH, reminder)
