"""

References:
    https://developer.aliyun.com/article/740160
    https://docs.python.org/zh-cn/3/library/argparse.html
"""
import os.path
import duckdb
import admin


def get_parquet_path(dataset, split):
    dataset_path = admin.get_local_dataset_path(dataset)
    file_name = split + '.parquet'
    parquet_path = os.path.join(dataset_path, 'parquet', file_name)
    return parquet_path


def parquet_filter(parquet_path, filter_cond, limit=0, select_cols='*'):
    cursor = duckdb.connect(database=':memory:')
    view_sql = """create or replace view dataset as 
    select * 
    from parquet_scan('%s');
    """ % parquet_path
    cursor.execute(view_sql)
    if limit:
        query_sql = "select " + ','.join(select_cols) + 'from dataset where ' + filter_cond + ' limit ' + str(limit)
    else:
        query_sql = "select " + ','.join(select_cols) + 'from dataset where ' + filter_cond
    df = cursor.execute(query_sql).fetch_df()
    return df


if __name__ == '__main__':
    print(get_parquet_path('CIFAR-10', 'train'))
    path = get_parquet_path('CIFAR-10', 'train')
    print(parquet_filter(path, "label='bird'", limit=20))
