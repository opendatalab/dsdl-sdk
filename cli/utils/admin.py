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


def __get_default_path():
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
    label_data boolean,
    media_data boolean,
    dataset_media_file_num bigint,
    dataset_media_file_bytes bigint,
    created_time timestamp,
    updated_time timestamp,
    primary key(dataset_name)
    );
    '''
    cursor.execute(create_table_sql)

    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS split(
    dataset_name varchar, 
    split_name varchar,
    split_media_file_num bigint,
    split_media_file_bytes bigint, 
    created_time timestamp,
    updated_time timestamp,
    primary key(dataset_name, split_name),
    CONSTRAINT fk_dataset  
    FOREIGN KEY (dataset_name)  
    REFERENCES departments(dataset_name)  
    );
    '''
    cursor.execute(create_table_sql)

    cursor.close()


# get db dir path, create one if not exists
def __get_default_db_path():
    path = os.path.join(__get_default_path(), DB_NAME)
    if not os.path.exists(path):
        print("initialize default db file...")
        initialize_db(path)
    return path


# get dataset local storage path
def get_local_dataset_path(dataset_name):
    cursor = sqlite3.connect(database=DB_PATH)
    res = cursor.execute("select dataset_path from dataset where dataset_name=?", [dataset_name]).fetchone()
    cursor.close()
    if res:
        return res[0]
    else:
        raise Exception('There is no dataset named %s' % dataset_name)


def get_local_split_path(dataset_name, split_name):
    dataset_path = get_local_dataset_path(dataset_name)
    cursor = sqlite3.connect(database=DB_PATH)
    split_data = cursor.execute("select * from split where dataset_name=? and split_name=?",
                                [dataset_name, split_name]).fetchone()
    split_path = os.path.join(dataset_path, 'parquet', '%s.parquet' % split_name)
    if split_data and os.path.exists(split_path):
        return split_path
    else:
        raise Exception('There is no split named %s in dataset %s or the file is lost' % (split_name, dataset_name))


# get table header in sqlite
def get_sqlite_table_header(table):
    cursor = sqlite3.connect(database=DB_PATH)
    res = cursor.execute("PRAGMA table_info('%s')" % table).fetchall()
    cursor.close()
    return [x[1] for x in res]


# get sqlite table data in a list of dict
def get_sqlite_dict_list(sql, header):
    res_list = []
    cursor = sqlite3.connect(database=DB_PATH)
    res = cursor.execute(sql).fetchall()
    for r in res:
        res_list.append(dict(zip(header, r)))
    return res_list


# get sqlite table data in a dataframe
def get_sqlite_dataframe(sql, header):
    dict_list = get_sqlite_dict_list(sql, header)
    dataframe = pd.DataFrame.from_dict(data=dict_list, )
    return dataframe


# sum file size of file list
def get_size_sum(file_list):
    sum_size = 0
    for f in file_list:
        sum_size += os.path.getsize(f)
    return sum_size


# split register in sqlite
def register_split(dataset_name, split_name, media_num, media_size):
    cursor = sqlite3.connect(database=DB_PATH)
    cursor.execute(
        "insert or replace into split values (?,?,?,?,datetime('now','localtime'),datetime('now','localtime'))",
        [dataset_name, split_name, media_num, media_size])
    cursor.commit()


# dataset register in sqlite
def register_dataset(dataset_name, dataset_path, label, media, media_num, media_size):
    cursor = sqlite3.connect(database=DB_PATH)
    cursor.execute(
        "insert or replace into dataset values (?,?,?,?,?,?,datetime('now','localtime'),datetime('now','localtime'))",
        [dataset_name, dataset_path, label, media, media_num, media_size])
    cursor.commit()


# delete split register in sqlite
def delete_split(dataset_name, split_name):
    cursor = sqlite3.connect(database=DB_PATH)
    cursor.execute(
        "delete from split where dataset_name=? and split_name=?",
        [dataset_name, split_name])
    cursor.commit()


# delete dataset register in sqlite
def delete_dataset(dataset_name):
    cursor = sqlite3.connect(database=DB_PATH)
    cursor.execute(
        "delete from split where dataset_name=?",
        [dataset_name])
    cursor.execute(
        "delete from dataset where dataset_name=?",
        [dataset_name])
    cursor.commit()


if __name__ == '__main__':
    print(DB_PATH)
    print(DB_DIR_PATH)
    default_path = __get_default_path()
    print(default_path)
    db_path = __get_default_db_path()
    print(db_path)
    print(get_local_dataset_path('CIFAR-10'))
    print(get_local_split_path('CIFAR-100', 'test'))
    print(get_sqlite_table_header('dataset'))
    print(get_sqlite_dict_list('select * from dataset', get_sqlite_table_header('dataset')))
    # print(get_sqlite_dataframe('select * from dataset', get_sqlite_table_header('dataset')))
    df = get_sqlite_dataframe('select * from dataset', get_sqlite_table_header('dataset'))
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
