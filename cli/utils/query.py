"""
admin module handles parquet operations
"""
import os.path
import duckdb
import yaml

from utils import admin
import pyarrow.parquet as pq
import pyarrow as pa
from utils.oss_ops import ops
from pyarrow import fs

aws_access_key_id = "ailabminio"
aws_secret_access_key = "123123123"
endpoint_url = "http://10.140.0.94:9800"
region_name = "ailab"
default_bucket = "dsdldata"


def get_dataset_info(dataset_name):
    db_client = admin.DBClient()
    if not db_client.is_dataset_local_exist(dataset_name):
        print("there is no dataset named %s locally" % dataset_name)
        exit()
    yml_path = os.path.join(db_client.get_local_dataset_path(dataset_name), 'parquet', 'dataset.yaml')
    with open(yml_path, 'r') as f:
        dataset_dict = yaml.safe_load(f)
    return dataset_dict


class ParquetReader:
    """
    A Class to read parquet file
    """

    def __init__(self, parquet_path, endpoint=None, access_key_id=None, secret_access_key=None, url_stype='path',
                 use_ssl=False):
        """
        Construct the parquet reader based on the parquet file path
        @param parquet_path:
        """
        self.cursor = duckdb.connect(database=':memory:')
        if not parquet_path.lower().startswith("s3"):
            self.path_flag = "local"
            self.parquet_path = parquet_path
        else:
            if endpoint is None:
                print("s3 info lacks endpoint")
                exit()
            if access_key_id is None:
                print("s3 info lacks access_key_id")
                exit()
            if secret_access_key is None:
                print("s3 info lacks secret_access_key")
                exit()

            self.endpoint = endpoint
            self.access_key_id = access_key_id
            self.secret_access_key = secret_access_key
            self.url_stype = url_stype
            self.use_ssl = "true" if use_ssl else "false"
            self.path_flag = "s3"
            self.parquet_path = parquet_path
            self.parquet_key = parquet_path[5:]

            self.fs = fs.S3FileSystem(
                access_key=aws_access_key_id,
                secret_key=secret_access_key,
                endpoint_override=endpoint_url,
            )

    def __create_dataset_view(self):
        if self.path_flag == "local":
            view_sql = """create or replace view dataset as 
            select * 
            from parquet_scan('%s');
            """ % self.parquet_path
        elif self.path_flag == "s3":
            self.cursor.execute("INSTALL httpfs;")
            self.cursor.execute("LOAD httpfs;")
            self.cursor.execute("set s3_endpoint='%s'" % self.endpoint)
            self.cursor.execute("set s3_access_key_id='%s'" % self.access_key_id)
            self.cursor.execute("set s3_secret_access_key='%s'" % self.secret_access_key)
            self.cursor.execute("set s3_url_style = '%s'" % self.url_stype)
            self.cursor.execute("set s3_use_ssl=%s" % self.use_ssl)
            view_sql = """create or replace view dataset as 
            select * 
            from read_parquet('%s');
            """ % self.parquet_path

        self.cursor.execute(view_sql)

    def select(self, select_cols='*', filter_cond='', limit=None, offset=None, samples=None):
        """
        Select data from parquet file
        @param select_cols: columns you want to select
        @param filter_cond: specify filters to apply to the data
        @param limit: restrict the amount of rows fetched
        @param offset: indicate at which position to start reading the values
        @param samples: query on a sample from the base table
        @return: a dataframe of data selected from the parquet
        """
        self.__create_dataset_view()

        query_sql = "select {cols} from dataset".format(cols=select_cols)

        # add where condition
        if filter_cond:
            query_sql = query_sql + ' where ' + filter_cond

        # add limit
        if limit:
            query_sql = query_sql + ' limit ' + str(limit)

        # add offset
        if offset:
            query_sql = query_sql + ' offset ' + str(offset)

        # add random samples
        if samples:
            # to do: implement %
            query_sql = 'select * from (' + query_sql + ') using sample %d rows' % samples

        # print(query_sql)
        df = self.cursor.execute(query_sql).fetch_df()
        return df

    def get_metadata(self):
        """
        Get metadata from parquet schema
        @return: 2 dicts of metadata: dsdl meta and statistics
        """
        if self.path_flag == "local":
            if not os.path.exists(self.parquet_path):
                raise Exception("parquet file does not exist")

            meta_dict = pq.read_schema(self.parquet_path)

        elif self.path_flag == "s3":
            meta_dict = pq.read_schema(self.parquet_key, filesystem=self.fs)

        stat_meta = eval(meta_dict.metadata[b'statistics'])
        return stat_meta

    def get_schema(self):
        """
        Get the schema of a parquet
        @return: a parquet schema
        """
        if self.path_flag == "local":
            if not os.path.exists(self.parquet_path):
                raise Exception("parquet file does not exist")
            schema = pq.read_schema(self.parquet_path)

        elif self.path_flag == "s3":
            schema = pq.read_schema(self.parquet_key, filesystem=self.fs)

        return schema

    def query(self, sql):
        self.__create_dataset_view()
        return self.cursor.execute(sql).fetch_df()


class SplitReader(ParquetReader):
    """
    A class to read parquet base on dataset name and split name
    """

    def __init__(self, dataset_name, split_name):
        self.dataset_name = dataset_name
        self.split_name = split_name
        self.db_client = admin.DBClient()
        self.parquet_path = ''
        self.dataset_yaml_path = ''

        if self.db_client.is_split_local_exist(dataset_name, split_name):
            self.parquet_path = self.db_client.get_local_split_path(dataset_name, split_name)
            self.dataset_yaml_path = os.path.join(self.db_client.get_local_dataset_path(dataset_name),
                                                  'parquet/dataset.yaml')
        else:
            self.s3_client = ops.OssClient(endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id,
                                           aws_secret_access_key=aws_secret_access_key, region_name=region_name)
            if self.s3_client.is_split_remote_exist(default_bucket, dataset_name, split_name):
                self.parquet_path = "s3://%s/%s/parquet/%s.parquet" % (default_bucket, dataset_name, split_name)
                self.dataset_yaml_path = "s3://%s/%s/parquet/dataset.yaml" % (default_bucket, dataset_name)

        if not self.parquet_path:
            print("Can not find the split named %s of dataset %s neither in local nor remote repo" % (
                split_name, dataset_name))
            exit()

        super(SplitReader, self).__init__(self.parquet_path, endpoint_url.replace("http://", ""), aws_access_key_id,
                                          aws_secret_access_key)

    def get_image_samples(self, sample_number):
        image_list = []
        if self.path_flag == "local":
            with open(self.dataset_yaml_path, 'r') as f:
                dataset_dict = yaml.safe_load(f)
            path_field = dataset_dict["dsdl_meta"]["struct"]["media_field"] if "media_field" in \
                                                                               dataset_dict["dsdl_meta"][
                                                                                   "struct"].keys() else "image"
            if type(path_field) == type([]):
                path_field = path_field[0]
            field_last_name = path_field.split(".")[-1]
            image_list = self.select(path_field, samples=sample_number)[field_last_name].tolist()
            dataset_path = self.db_client.get_local_dataset_path(self.dataset_name)
            image_list = [os.path.join(dataset_path, img) for img in image_list]
        elif self.path_flag == "s3":
            dataset_dict = yaml.safe_load(self.s3_client.read_file(default_bucket, self.dataset_yaml_path))
            path_field = dataset_dict["dsdl_meta"]["struct"]["media_field"] if "media_field" in \
                                                                               dataset_dict["dsdl_meta"][
                                                                                   "struct"].keys() else "image"
            field_last_name = path_field.split(".")[-1]
            image_list = self.select(path_field, samples=sample_number)[field_last_name].tolist()
            dataset_path = "s3://%s/%s/" % (default_bucket, self.dataset_name)
            image_list = [dataset_path + img for img in image_list]
        return image_list


class DSDLParquet:
    """
    A class to handle operations of dsdl parquet file
    """

    def __init__(self, dataframe, parquet_path, schema, statistics=None):
        self.parquet_path = parquet_path
        self.meta_dict = schema.metadata
        if statistics:
            self.meta_dict[b'statistics'] = str(statistics)

        self.dataframe = dataframe
        self.schema = schema.with_metadata(self.meta_dict)
        self.table = pa.Table.from_pandas(self.dataframe, schema=self.schema, preserve_index=False)

    def save(self):
        """
        Save the dsdl parquet to a specified path
        @return:
        """
        pq.write_table(self.table, self.parquet_path)


class Split:
    """
    A class to handle a split
    """

    def __init__(self, dataset_name, split_name, storage_path=''):
        self.db_client = admin.DBClient()
        self.dataset_name = dataset_name
        self.split_name = split_name

        if not self.db_client.is_dataset_local_exist(dataset_name):
            print('There is no local dataset named %s, create local path...' % dataset_name)
            if not storage_path:
                print("no storage path given...")
                exit()
            else:
                self.dataset_path = os.path.join(storage_path, dataset_name)
                self.parquet_folder_path = os.path.join(self.dataset_path, 'parquet')
                self.media_folder_path = os.path.join(self.dataset_path, 'media')
                for p in [self.dataset_path, self.parquet_folder_path, self.media_folder_path]:
                    if not os.path.exists(p):
                        os.mkdir(p)
                self.dataset_info_path = os.path.join(self.parquet_folder_path, 'dataset.yaml')
                self.s3_client = ops.OssClient(endpoint_url=endpoint_url, aws_access_key_id=aws_access_key_id,
                                               aws_secret_access_key=aws_secret_access_key, region_name=region_name)
                self.s3_client.download_file(default_bucket, dataset_name + '/parquet/dataset.yaml',
                                             self.dataset_info_path)

        else:
            self.dataset_path = self.db_client.get_local_dataset_path(self.dataset_name)
            self.parquet_folder_path = os.path.join(self.dataset_path, 'parquet')
            self.media_folder_path = os.path.join(self.dataset_path, 'media')

        self.parquet_path = os.path.join(self.parquet_folder_path, self.split_name + '.parquet')

    def is_local_exist(self):
        """
        Check whether the split is locally existed
        @return:
        """
        return self.db_client.is_split_local_exist(self.dataset_name, self.split_name)

    def save(self, dataframe, schema, type, label, media, statistics):
        """
        Save the split
        @param dataframe: data in dataframe format
        @param schema:
        @param dsdl_meta:
        @param statistics:
        @return:
        """
        media_num = statistics['split_stat']['media_num']
        media_size = statistics['split_stat']['media_size']
        dsdl_parquet = DSDLParquet(dataframe, self.parquet_path, schema, statistics)
        dsdl_parquet.save()
        self.db_client.register_split(self.dataset_name, self.split_name, type, label, media, media_num, media_size)


if __name__ == '__main__':
    db_client = admin.DBClient()
    path = db_client.get_local_split_path('CIFAR-10', 'train')
    split_reader = SplitReader('CIFAR-10-Auto', 'train')

    # print(split_reader.select(filter_cond="label='bird'", select_cols="image,label", samples=1500,
    #                           limit=800, offset=100))
    # dsdl_meta, stat_meta = split_reader.get_metadata()
    # print(dsdl_meta)
    # print(stat_meta)
    # #
    # df = split_reader.select(filter_cond="label='bird'", select_cols="image,label", samples=1500,
    #                          limit=800, offset=100)
    # schema = split_reader.get_schema()
    # meta = split_reader.get_metadata()
    # split = DSDLParquet(df, 'D:\\DSDL_STORE\\test2.parquet', schema, statistics={'test': 'test'})
    # split.save()
    #
    # parquet_reader = ParquetReader('D:\\DSDL_STORE\\STL-10\\STL-10\\parquet\\train.parquet')
    # dsdl_meta, stat_meta = parquet_reader.get_metadata()
    # print(dsdl_meta)
    # print(stat_meta)
    # meta_dict = pq.read_schema(db_client.get_local_split_path('CIFAR-100', 'train'))
    s3_path = "s3://dsdldata/CIFAR-10/parquet/test.parquet"
    parquet_reader = ParquetReader(s3_path, '10.140.0.94:9800', 'ailabminio', '123123123')
    df = parquet_reader.select(limit=20)
    print(df)
    stat = parquet_reader.get_metadata()
    print(stat)
    schema = parquet_reader.get_schema()
    print(schema)
    # test_df = parquet_reader.query("select * from dataset limit 10")
    # print(test_df)
