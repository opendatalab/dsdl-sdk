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
import yaml

aws_access_key_id = query.aws_access_key_id
aws_secret_access_key = query.aws_secret_access_key
endpoint_url = query.endpoint_url
region_name = query.region_name
default_bucket = query.default_bucket

default_path = DEFAULT_LOCAL_STORAGE_PATH


class Select(CmdBase):
    """
    Example command
    """

    def init_parser(self, subparsers):
        """
        Initialize the parser for the command
        document : https://docs.python.org/zh-cn/3/library/argparse.html#

        Args:
            subparsers:

        Returns:

        """
        select_parser = subparsers.add_parser('select', help='Select data from dataset',
                                              example="select.example",
                                              description='Select data from dataset', )  # example 样例文件位于resources/下，普通的文本文件，每个命令写一个
        # select_parser.add_argument("-s", '--show', nargs='?', default='SHOW', help='show example string.....',
        #                            metavar='SS')
        # example_parser.add_argument('--test1', nargs='?', default='x', help='show test1', metavar='a')
        # example_parser.add_argument('--test-1234', nargs='?', default='t', help='show test-1234', metavar='c')
        select_parser.add_argument("dataset_name", action=EnvDefaultVar, envvar=DSDL_CLI_DATASET_NAME,
                                   type=str,
                                   help='Dataset name. The arg is optional only when the default dataset name was set by cd command.',
                                   metavar='')
        select_parser.add_argument("--split-name", type=str, required=True,
                                   help='The split name of the dataset, such as train/test/unlabeled or user self-defined split.',
                                   metavar='')
        select_parser.add_argument("--filter", type=str,
                                   help='Filter data according to given conditions, such as "label=\'bird\'"',
                                   metavar='')
        # select_parser.add_argument("--fields", type=str,
        #                            help='Fields to be selected. All the files will be selected if the arg is not given. Use "," to split fields.',
        #                            metavar='')
        select_parser.add_argument("--limit", type=int,
                                   help='Limit the number of returned records',
                                   metavar='')
        select_parser.add_argument("--offset", type=int,
                                   help='Set the number of rows to skip from the beginning of the returned data before presenting the results',
                                   metavar='')
        select_parser.add_argument("--random", type=int,
                                   # help='Set the number/percent of random samples from the base select result, such as 100 or 5%',
                                   help='Set the number of random samples from the returned select result',
                                   metavar='')
        select_parser.add_argument("--export-name", type=str,
                                   help='Save the select result as a split and use the given name to name it',
                                   metavar='')
        select_parser.add_argument("--output", type=str,
                                   help='The path to save the select result as a new split',
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
        conf_dict = admin.get_config_dict()

        dataset_name = cmdargs.dataset_name
        split_name = cmdargs.split_name
        filter = cmdargs.filter
        # fields = '*' if cmdargs.fields is None else cmdargs.fields
        fields = '*'
        limit = cmdargs.limit
        offset = cmdargs.offset
        random = cmdargs.random
        export_name = cmdargs.export_name
        output = cmdargs.output if cmdargs.output else 'default'
        output_path = conf_dict['storage'][cmdargs.output]['path'] if cmdargs.output else default_path

        db_client = admin.DBClient()
        s3_client = ops.OssClient(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,
                                  endpoint_url=endpoint_url, region_name=region_name)

        # if not db_client.is_dataset_local_exist(dataset_name):
        #     print("there is no dataset named %s locally" % dataset_name)
        #     exit()

        # assert (db_client.is_dataset_local_exist(dataset_name)), "there is no dataset named %s locally" % dataset_name

        if not db_client.is_split_local_exist(dataset_name, split_name):
            print(
                "there is no split named %s of dataset %s locally, search in remote repo" % (split_name, dataset_name))

            if not s3_client.is_split_remote_exist(default_bucket, dataset_name, split_name):
                print("there is no split named %s of dataset %s in remote repo" % (split_name, dataset_name))
                exit()

        split_reader = query.SplitReader(dataset_name, split_name)
        df = split_reader.select(select_cols=fields, filter_cond=filter, limit=limit, offset=offset, samples=random)
        print(df)

        if export_name is not None:
            sub_split = query.Split(dataset_name, export_name, output_path)
            media_download_flag = 0
            question = 'The split "%s" has already existed. Do you want to replace it? (y/n)' % export_name
            if sub_split.is_local_exist():
                if not input(question) in ("y", "Y"):
                    exit()

            if db_client.is_dataset_local_exist(dataset_name):
                path_info = "the dataset %s registered locally, the split has to been exported to %s" % (
                    dataset_name, sub_split.parquet_path)
                split_db_info = db_client.get_sqlite_dict_list(
                    "select * from split where dataset_name='%s' and split_name='%s'" % (dataset_name, split_name))
                if len(split_db_info) != 0:
                    # print(split_db_info)
                    media_download_flag = split_db_info[0]['media_data']

                if media_download_flag:
                    media_path = [os.path.join(sub_split.dataset_path, x) for x in df['image'].tolist()]
                    media_stat = admin.get_media_stat(media_path)
                    media_num = media_stat['media_num']
                    media_size = media_stat['media_size']

                    split_stat = {'media_num': media_num, 'media_size': media_size}

                    stat = split_reader.get_metadata()
                    stat['split_stat'] = split_stat

                    schema = split_reader.get_schema()

                else:
                    media_prefix = "%s/" % dataset_name
                    media_path = [media_prefix + x for x in df['image'].tolist()]
                    media_num = len(set(media_path))
                    media_size = s3_client.get_sum_size(default_bucket, media_path)

                    split_stat = {'media_num': media_num, 'media_size': media_size}
                    stat = split_reader.get_metadata()
                    stat['split_stat'] = split_stat

                    schema = split_reader.get_schema()

            else:
                path_info = "the dataset %s does not exist locally, the split has to been exported to given output %s" % (
                    dataset_name, sub_split.parquet_path)

                media_prefix = "%s/" % dataset_name
                media_path = [media_prefix + x for x in df['image'].tolist()]
                media_num = len(set(media_path))
                media_size = s3_client.get_sum_size(default_bucket, media_path)

                split_stat = {'media_num': media_num, 'media_size': media_size}
                stat = split_reader.get_metadata()
                stat['split_stat'] = split_stat

                schema = split_reader.get_schema()

                yaml_key = '/'.join([dataset_name, 'parquet', 'dataset.yaml'])
                dataset_dict = yaml.safe_load(s3_client.read_file(default_bucket, yaml_key))
                dataset_media_num = dataset_dict["statistics"]["dataset_stat"]['media_num']
                dataset_media_size = dataset_dict["statistics"]["dataset_stat"]['media_size']

                db_client.register_dataset(dataset_name, output, sub_split.dataset_path, 0, 0, dataset_media_num,
                                           dataset_media_size)

            sub_split.save(df, schema, 'user-defined', 1, media_download_flag, stat)
            print(path_info)

            # to do operations about fields
            # a, b = query.get_parquet_metadata(parquet_path)
            # print(a)
            # print(b)
            #
            # for n in query.get_parquet_schema(parquet_path):
            #     print(n)
