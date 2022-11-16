"""

References:
    https://developer.aliyun.com/article/740160
    https://docs.python.org/zh-cn/3/library/argparse.html
"""
import os.path
import duckdb
from utils import admin
import pyarrow.parquet as pq
import pyarrow as pa


# def get_parquet_path(dataset, split):
#     dataset_path = admin.get_local_dataset_path(dataset)
#     file_name = split + '.parquet'
#     parquet_path = os.path.join(dataset_path, 'parquet', file_name)
#     return parquet_path


def parquet_filter(parquet_path, select_cols='*', filter_cond='', limit=None, offset=None, samples=None):
    cursor = duckdb.connect(database=':memory:')
    view_sql = """create or replace view dataset as 
    select * 
    from parquet_scan('%s');
    """ % parquet_path
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


def split_filter(dataset_name, split_name, select_cols, filter_cond, limit, offset, samples):
    parquet_path = admin.get_local_split_path(dataset_name, split_name)
    return parquet_filter(parquet_path=parquet_path, select_cols=select_cols, filter_cond=filter_cond, limit=limit,
                          offset=offset, samples=samples)


def get_parquet_metadata(parquet_path):
    if not os.path.exists(parquet_path):
        raise Exception("parquet file does not exist")

    meta_dict = pq.read_schema(parquet_path)

    dsdl_meta = eval(meta_dict.metadata[b'dsdl_meta'])
    stat_meta = eval(meta_dict.metadata[b'statistics'])
    return dsdl_meta, stat_meta


def get_metadata(dataset_name, split_name):
    parquet_path = admin.get_local_split_path(dataset_name, split_name)
    return get_parquet_metadata(parquet_path)


def get_parquet_schema(parquet_path):
    if not os.path.exists(parquet_path):
        raise Exception("parquet file does not exist")

    schema = pq.read_schema(parquet_path)
    return schema


def get_schema(dataset_name, split_name):
    parquet_path = admin.get_local_split_path(dataset_name, split_name)
    return get_parquet_schema(parquet_path)


def save_parquet(dataframe, parquet_path, schema, dsdl_meta=None, statistics=None):
    meta_dict = schema.metadata

    if dsdl_meta:
        meta_dict[b'dsdl_meta'] = str(dsdl_meta)
    if statistics:
        meta_dict[b'statistics'] = str(statistics)

    schema = schema.with_metadata(meta_dict)

    # output parquet file
    # print('start writing...')
    table_write = pa.Table.from_pandas(dataframe, schema=schema, preserve_index=False)
    pq.write_table(table_write, parquet_path)

# def save_split(dataset_name, split_name, dataframe, parquet_path, schema, dsdl_meta=None, statistics=None):
#     meta_dict = schema.metadata
#     dsdl_meta_dict = meta_dict[b'dsdl_meta'] if dsdl_meta is None else dsdl_meta
#     stat_meta_dict = meta_dict[b'statistics'] if statistics is None else statistics

if __name__ == '__main__':
    path = admin.get_local_split_path('CIFAR-10', 'train')
    print(path)
    print(parquet_filter(parquet_path=path, filter_cond="label='bird'", select_cols="image,label", samples=1500,
                         limit=800, offset=100))
    dsdl_meta, stat_meta = get_metadata('CIFAR-10', 'train')
    # print(dsdl_meta)
    # print(stat_meta)

    df = parquet_filter(parquet_path=path, filter_cond="label='bird'", select_cols="image,label", samples=1500,
                        limit=800, offset=100)
    schema = get_parquet_schema(path)
    meta = get_parquet_metadata(path)
    save_parquet(df, 'D:\\DSDL_STORE\\test.parquet', schema, statistics={'test': 'test'})

    dsdl_meta, stat_meta = get_parquet_metadata('D:\\DSDL_STORE\\test.parquet')
    print(dsdl_meta)
    print(stat_meta)
