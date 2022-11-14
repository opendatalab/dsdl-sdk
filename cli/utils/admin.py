"""

References:
    https://developer.aliyun.com/article/740160
    https://docs.python.org/zh-cn/3/library/argparse.html
"""
# import duckdb
import sqlite3
import os
import pandas as pd
from tabulate import tabulate
from commands import const

DB_PATH = const.SQLITE_DB_PATH
DB_DIR_PATH = const.DEFAULT_CONFIG_DIR
DB_NAME = const.__SQLITE_DB_NAME


def get_default_path():
    path = DB_DIR_PATH
    if not os.path.exists(path):
        print("initialize default directory...")
        os.mkdir(path)
    return path


def initialize_db(db_file):
    cursor = sqlite3.connect(database=db_file)
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS dataset(
    dataset_name varchar, 
    dataset_path varchar,
    split_name varchar,
    label_data boolean,
    media_data boolean,
    split_media_file_num bigint,
    split_media_file_bytes bigint, 
    dataset_media_file_num bigint,
    dataset_media_file_bytes bigint,
    created_time timestamp,
    updated_time timestamp,
    primary key(dataset_name));
    '''
    cursor.execute(create_table_sql)
    cursor.close()


def get_default_db_path():
    path = os.path.join(get_default_path(), DB_NAME)
    if not os.path.exists(path):
        print("initialize default db file...")
        initialize_db(path)
    return path


def get_local_dataset_path(dataset_name):
    cursor = sqlite3.connect(database=get_default_db_path())
    res = cursor.execute("select dataset_path from dataset where dataset_name=?", [dataset_name]).fetchone()
    cursor.close()
    if res:
        return res[0]
    else:
        raise Exception('There is no dataset named %s' % dataset_name)


def get_sqlite_table_header(table):
    cursor = sqlite3.connect(database=get_default_db_path())
    res = cursor.execute("PRAGMA table_info('%s')" % table).fetchall()
    cursor.close()
    return [x[1] for x in res]


def get_sqlite_dict_list(sql, header):
    res_list = []
    cursor = sqlite3.connect(database=get_default_db_path())
    res = cursor.execute(sql).fetchall()
    for r in res:
        res_list.append(dict(zip(header, r)))
    return res_list


def get_sqlite_dataframe(sql, header):
    dict_list = get_sqlite_dict_list(sql, header)
    dataframe = pd.DataFrame.from_dict(data=dict_list, )
    return dataframe


if __name__ == '__main__':
    print(DB_PATH)
    print(DB_DIR_PATH)
    default_path = get_default_path()
    print(default_path)
    db_path = get_default_db_path()
    print(db_path)
    print(get_local_dataset_path('CIFAR-10'))
    print(get_sqlite_table_header('dataset'))
    print(get_sqlite_dict_list('select * from dataset', get_sqlite_table_header('dataset')))
    # print(get_sqlite_dataframe('select * from dataset', get_sqlite_table_header('dataset')))
    df = get_sqlite_dataframe('select * from dataset', get_sqlite_table_header('dataset'))
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
