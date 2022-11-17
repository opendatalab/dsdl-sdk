"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""
import os

from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME, DEFAULT_LOCAL_STORAGE_PATH
from commons.argument_parser import EnvDefaultVar
from utils import admin, query
from utils.oss_ops import ops
from utils.minio_ops import ops

aws_access_key_id = "ailabminio"
aws_secret_access_key = "123123123"
endpoint_url = "10.140.0.94:9800"
region_name = "ailab"
# default_path = 'D:\\DSDL_DATA'
default_path = DEFAULT_LOCAL_STORAGE_PATH
default_bucket = "dsdldata"


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
        select_parser = subparsers.add_parser('get', help='download data from repo',
                                              example="select.example",
                                              description='Download data from repo', )

        select_parser.add_argument("--dataset_name", action=EnvDefaultVar, envvar=DSDL_CLI_DATASET_NAME,
                                   type=str,
                                   help='Dataset name. The arg is optional only when the default dataset name was set by cd command.',
                                   metavar='')
        select_parser.add_argument("-s", "--split_name", type=str,
                                   help='The split name of the dataset, such as train/test/validation or self-defined split.',
                                   metavar='')
        select_parser.add_argument("-o", "--output", type=str,
                                   help='Target saving path.',
                                   metavar='')

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
        dataset_name = cmdargs.dataset_name
        split_name = cmdargs.split_name
        output_path = cmdargs.output if cmdargs.output else default_path

        minio_client = ops.OSS_OPS(endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key, region_name=region_name)

        remote_dataset_list = [x.object_name.replace('/', '') for x in minio_client.list_objects(default_bucket) if
                               x.is_dir]
        if dataset_name not in remote_dataset_list:
            print("there is no dataset named %s in remote repo" % dataset_name)
            exit()

        try:
            dataset_dir = admin.get_local_dataset_path(dataset_name)
            question = 'The dataset "%s" has already existed in %s. Do you want to replace it? (y/n)' % (
                dataset_name, dataset_dir)
            if not input(question) in ("y", "Y"):
                exit()
        except Exception as e:
            pass

        admin.delete_dataset(dataset_name)
        dataset_dir = os.path.join(output_path, dataset_name)
        print("saving to %s" % dataset_dir)

        minio_client.download_directory(default_bucket, dataset_name + '/', output_path)
        print("register local dataset...")
        parquet_list = [obj.object_name.split("/")[-1] for obj in
                        minio_client.list_objects(default_bucket, dataset_name + '/parquet/')]
        _, stat = query.get_parquet_metadata(os.path.join(dataset_dir, 'parquet', parquet_list[0]))
        dataset_media_num = stat['dataset_stat']['media_num']
        dataset_media_size = stat['dataset_stat']['media_size']

        admin.register_dataset(dataset_name, dataset_dir, 1, 1, dataset_media_num, dataset_media_size)
        for split in parquet_list:
            _, stat = query.get_parquet_metadata(os.path.join(dataset_dir, 'parquet', split))
            split_media_num = stat['split_stat']['media_num']
            split_media_size = stat['split_stat']['media_size']
            admin.register_split(dataset_name, split.replace(".parquet", ""), split_media_num, split_media_size)
