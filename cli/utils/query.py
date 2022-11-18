"""
admin module handles parquet operations
"""
import os.path
import duckdb
from utils import admin
import pyarrow.parquet as pq
import pyarrow as pa


class ParquetReader:
    """
    A Class to read parquet file
    """
    def __init__(self, parquet_path):
        """
        Construct the parquet reader based on the parquet file path
        @param parquet_path:
        """
        self.parquet_path = parquet_path

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
        cursor = duckdb.connect(database=':memory:')
        view_sql = """create or replace view dataset as 
        select * 
        from parquet_scan('%s');
        """ % self.parquet_path
        cursor.execute(view_sql)
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
        df = cursor.execute(query_sql).fetch_df()
        return df

    def get_metadata(self):
        """
        Get metadata from parquet schema
        @return: 2 dicts of metadata: dsdl meta and statistics
        """
        if not os.path.exists(self.parquet_path):
            raise Exception("parquet file does not exist")

        meta_dict = pq.read_schema(self.parquet_path)

        dsdl_meta = eval(meta_dict.metadata[b'dsdl_meta'])
        stat_meta = eval(meta_dict.metadata[b'statistics'])
        return dsdl_meta, stat_meta

    def get_schema(self):
        """
        Get the schema of a parquet
        @return: a parquet schema
        """
        if not os.path.exists(self.parquet_path):
            raise Exception("parquet file does not exist")

        schema = pq.read_schema(self.parquet_path)
        return schema


class SplitReader(ParquetReader):
    """
    A class to read parquet base on dataset name and split name
    """
    def __init__(self, dataset_name, split_name):
        self.db_client = admin.DBClient()
        self.parquet_path = self.db_client.get_local_split_path(dataset_name, split_name)
        super(SplitReader, self).__init__(self.parquet_path)


class DSDLParquet:
    """
    A class to handle operations of dsdl parquet file
    """
    def __init__(self, dataframe, parquet_path, schema, dsdl_meta=None, statistics=None):
        self.parquet_path = parquet_path
        self.meta_dict = schema.metadata
        if dsdl_meta:
            self.meta_dict[b'dsdl_meta'] = str(dsdl_meta)
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
    def __init__(self, dataset_name, split_name):
        self.db_client = admin.DBClient()
        if not self.db_client.is_dataset_local_exist(dataset_name):
            raise Exception('There is no local dataset named %s' % dataset_name)
        self.dataset_name = dataset_name
        self.dataset_path = self.db_client.get_local_dataset_path(self.dataset_name)
        self.split_name = split_name
        self.parquet_path = os.path.join(self.dataset_path, 'parquet', self.split_name + '.parquet')

    def is_local_exist(self):
        """
        Check whether the split is locally existed
        @return:
        """
        return self.db_client.is_split_local_exist(self.dataset_name, self.split_name)

    def save(self, dataframe, schema, dsdl_meta, statistics):
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
        dsdl_parquet = DSDLParquet(dataframe, self.parquet_path, schema, dsdl_meta, statistics)
        dsdl_parquet.save()
        self.db_client.register_split(self.dataset_name, self.split_name, media_num, media_size)


if __name__ == '__main__':
    db_client = admin.DBClient()
    path = db_client.get_local_split_path('CIFAR-10', 'train')
    split_reader = SplitReader('CIFAR-10', 'train')

    print(split_reader.select(filter_cond="label='bird'", select_cols="image,label", samples=1500,
                              limit=800, offset=100))
    dsdl_meta, stat_meta = split_reader.get_metadata()
    print(dsdl_meta)
    print(stat_meta)
    #
    df = split_reader.select(filter_cond="label='bird'", select_cols="image,label", samples=1500,
                             limit=800, offset=100)
    schema = split_reader.get_schema()
    meta = split_reader.get_metadata()
    split = DSDLParquet(df, 'D:\\DSDL_STORE\\test2.parquet', schema, statistics={'test': 'test'})
    split.save()

    parquet_reader = ParquetReader('D:\\DSDL_STORE\\test2.parquet')
    dsdl_meta, stat_meta = parquet_reader.get_metadata()
    print(dsdl_meta)
    print(stat_meta)
