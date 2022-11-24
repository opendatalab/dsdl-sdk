"""
一个命令的实现例子

Examples:
    $python cli.py example --show tell me the truth
    >> Namespace(show=["'tell", 'me', 'the', "truth'"], command_handler=<bound method Example.cmd_entry of <commands.example.Example object at 0x0000017E6FD1DB40>>)
    >> ["'tell", 'me', 'the', "truth'"]
"""
import os

from commands.cmdbase import CmdBase
from commands.const import DSDL_CLI_DATASET_NAME
from commons.argument_parser import EnvDefaultVar
from utils import admin, query


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
        select_parser.add_argument("--dataset_name", action=EnvDefaultVar, envvar=DSDL_CLI_DATASET_NAME,
                                   type=str,
                                   help='Dataset name. The arg is optional only when the default dataset name was set by cd command.',
                                   metavar='')
        select_parser.add_argument("--split_name", type=str, required=True,
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
        select_parser.add_argument("--export_name", type=str,
                                   help='Save the select result as a split and use the given name to name it',
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
        filter = cmdargs.filter
        # fields = '*' if cmdargs.fields is None else cmdargs.fields
        fields = '*'
        limit = cmdargs.limit
        offset = cmdargs.offset
        random = cmdargs.random
        export_name = cmdargs.export_name

        split_reader = query.SplitReader(dataset_name, split_name)
        df = split_reader.select(select_cols=fields, filter_cond=filter, limit=limit, offset=offset, samples=random)
        print(df)

        if export_name is not None:
            sub_split = query.Split(dataset_name, export_name)
            question = 'The split "%s" has already existed. Do you want to replace it? (y/n)' % export_name
            if sub_split.is_local_exist():
                if not input(question) in ("y", "Y"):
                    exit()

            media_path = [os.path.join(sub_split.dataset_path, x) for x in df['image'].tolist()]
            media_stat = admin.get_media_stat(media_path)
            media_num = media_stat['media_num']
            media_size = media_stat['media_size']

            split_stat = {'media_num': media_num, 'media_size': media_size}

            meta, stat = split_reader.get_metadata()
            stat['split_stat'] = split_stat

            schema = split_reader.get_schema()
            sub_split.save(df, schema, 'user-defined', 1, 1, meta, stat)
            print("The parquet has exported to %s" % sub_split.parquet_path)

            # to do operations about fields
            # a, b = query.get_parquet_metadata(parquet_path)
            # print(a)
            # print(b)
            #
            # for n in query.get_parquet_schema(parquet_path):
            #     print(n)
