"""
admin module handles sqlite operations
"""
import logging
import os
import sqlite3
import json

import pandas as pd
from tabulate import tabulate

from commands import const
from commons.stdio import print_stdout
from loguru import logger
from commons.exceptions import CLIException, ExistCode

# get const path
DB_PATH = const.SQLITE_DB_PATH
DB_DIR_PATH = const.DEFAULT_CONFIG_DIR
DB_NAME = const.__SQLITE_DB_NAME
CONF_PATH = const.DEFAULT_CLI_CONFIG_FILE


def get_config_dict():
    with open(CONF_PATH, 'r') as f:
        return json.loads(f.read())


def __get_default_path() -> str:
    """
    Get the default DSDL directory path
    @return: default DSDL directory path as string
    """
    path = DB_DIR_PATH
    if not os.path.exists(path):
        print("initialize default directory...")
        os.mkdir(path)
    return path


def __get_default_db_path():
    """
    Get the default DSDL sqlite file path
    @return:
    """
    path = os.path.join(__get_default_path(), DB_NAME)
    if not os.path.exists(path):
        print("initialize default db file...")
        initialize_db(path)
    return path


def initialize_db(db_file):
    """
    Initialize sqlite db file in defautl DSDL folder
    @param db_file: default db file path
    @return:
    """
    conn = sqlite3.connect(database=db_file)
    cursor = conn.cursor()
    create_table_sql = '''
    CREATE TABLE IF NOT EXISTS dataset(
    dataset_name varchar, 
    task_type varchar,
    storage_name varchar,
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
    split_type varchar,
    label_data boolean,
    media_data boolean,
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

    conn.commit()
    cursor.close()
    conn.close()


def get_size_sum(file_list):
    """
    Compute total size of a list of files
    @param file_list: a list of file path
    @return: the total size of files
    """
    sum_size = 0
    for f in file_list:
        sum_size += os.path.getsize(f)
    return sum_size


def get_media_stat(media_list):
    """
    Computer statistics of a list of media files
    @param media_list:
    @return: media statistics
    """
    media_list = set(media_list)
    media_num = len(media_list)
    media_size = get_size_sum(media_list)

    media_stat = {'media_num': media_num, 'media_size': media_size}
    return media_stat


class DBClient:
    """
    This class handles operations on DSDL local db
    """

    def __init__(self):
        """
        create connection and cursor to link sqlite
        """
        self.conn = sqlite3.connect(database=DB_PATH)
        self.cursor = self.conn.cursor()

    # def __del__(self):
    #     """
    #     close connection and cursor
    #     @return:
    #     """
    #     self.cursor.close()
    #     self.conn.close()
    def get_sqlite_dict_list(self, sql) -> list:
        """
        Get sql query result as a list of dicts
        @param cursor: a cursor of a db connection
        @param sql: query sql
        @return: the query result as a list of dicts
        """
        cursor = self.cursor
        res_list = []
        res = cursor.execute(sql).fetchall()
        header = [x[0] for x in cursor.description]
        for r in res:
            res_list.append(dict(zip(header, r)))
        return res_list

    def get_sqlite_dataframe(self, sql) -> pd.DataFrame:
        """
        Get sql query result as a pandas dataframe
        @param cursor: a cursor of a db connection
        @param sql: query sql
        @return: the query result as a pandas dataframe
        """
        dict_list = self.get_sqlite_dict_list(sql)
        dataframe = pd.DataFrame.from_dict(data=dict_list)
        return dataframe

    def get_local_dataset_path(self, dataset_name: str):
        """
        Get the local path from sqlite for the given dataset name

        @param dataset_name: the formal dataset name which you want to get local storage path
        @return: the dataset local path get from sqlite db
                 return None if there is no record in database for the given dataset name
        """
        try:
            res = self.cursor.execute("select dataset_path from dataset where dataset_name=?",
                                      [dataset_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        if res:
            return res[0]
        else:
            return None

    def get_local_split_path(self, dataset_name, split_name):
        """
        Get the local path from sqlite for the given dataset name and split name
        @param dataset_name: the formal dataset name
        @param split_name: the split of the dataset, such as train/test
        @return: the split local path get from sqlite db
                 return None if there is no record in database for the given dataset name
        """
        dataset_path = self.get_local_dataset_path(dataset_name)
        try:
            split_data = self.cursor.execute("select * from split where dataset_name=? and split_name=?",
                                             [dataset_name, split_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select split operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        split_path = os.path.join(dataset_path, 'parquet', '%s.parquet' % split_name)
        if split_data and os.path.exists(split_path):
            return split_path
        else:
            return None

    def get_dataset_info_by_name(self, dataset_name:str) -> dict:
        """

        Args:
            dataset_name:

        Returns:

        """
        try:
            res = self.cursor.execute("select * from dataset where dataset_name=?", [dataset_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        if res:
            header = [x[0] for x in self.cursor.description]
            return dict(zip(header, res))
        else:
            return None

    def is_dataset_local_exist(self, dataset_name: str) -> bool:
        """
        Check whether the given dataset exists locally

        @param dataset_name: the formal dataset name which you want to check if exists locally
        @return: if exists, return True, otherwise return False
        """
        if self.get_local_dataset_path(dataset_name):
            return True
        else:
            return False

    def is_split_local_exist(self, dataset_name: str, split_name: str) -> bool:
        """
        Check whether the given split exists locally
        @param dataset_name: the formal dataset name which the target split belong to
        @param split_name: the split name which you want to check if exists locally
        @return: if exists, return True, otherwise return False
        """
        try:
            res = self.cursor.execute("select * from split where dataset_name=? and split_name=?",
                                      [dataset_name, split_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select split operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        if res:
            return True
        else:
            return False

    def register_dataset(self, dataset_name, task_type, storage_name, dataset_path, label, media, media_num,
                         media_size):
        """
        Register a dataset in database
        @param dataset_name: the dataset name
        @param task_type: the task type of the dataset
        @param storage_name: the storage name in conf file
        @param dataset_path: the dataset storage path
        @param label: 1 or 0, whether the label data of dataset is downloaded
        @param media: 1 or 0, whether the media data of dataset is downloaded
        @param media_num: the number of media files
        @param media_size: the number of total media file size
        @return:
        """
        try:
            self.cursor.execute(
                "insert or replace into dataset values (?,?,?,?,?,?,?,?,datetime('now','localtime'),datetime('now','localtime'))",
                [dataset_name, task_type, storage_name, dataset_path, label, media, media_num, media_size])
            self.conn.commit()
        except Exception as e:
            error_info = "Sqlite register dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)

    def register_split(self, dataset_name, split_name, split_type, label, media, media_num, media_size):
        """
        Register a new split in database
        @param dataset_name: the dataset name
        @param split_name: a subset of a dataset
        @param media_num: the number of media files
        @param media_size: the number of total media file size
        @return:
        """
        try:
            self.cursor.execute(
                "insert or replace into split values (?,?,?,?,?,?,?,datetime('now','localtime'),datetime('now','localtime'))",
                [dataset_name, split_name, split_type, label, media, media_num, media_size])
            self.conn.commit()
        except Exception as e:
            error_info = "Sqlite register split operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)

    def delete_split(self, dataset_name, split_name):
        """
        Delete a split from database after it was deleted
        @param dataset_name: the dataset name
        @param split_name: a subset of a dataset
        @return:
        """
        try:
            self.cursor.execute(
                "delete from split where dataset_name=? and split_name=?",
                [dataset_name, split_name])
            self.conn.commit()
        except Exception as e:
            error_info = "Sqlite delete split operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)

    def delete_dataset(self, dataset_name):
        """
        Delete a dataset from database after it was deleted
        @param dataset_name: the dataset name
        @return:
        """
        try:
            self.cursor.execute(
                "delete from split where dataset_name=?",
                [dataset_name])
            self.cursor.execute(
                "delete from dataset where dataset_name=?",
                [dataset_name])
            self.conn.commit()
        except Exception as e:
            error_info = "Sqlite delete dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)

    def is_dataset_label_downloaded(self, dataset_name):
        """
        Whether the label data of a dataset is downloaded
        @param dataset_name: dataset name
        @return:
        """
        try:
            res = self.cursor.execute("select label_data from dataset where dataset_name=?",
                                      [dataset_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        flag = False
        if res:
            if res[0] == 1:
                flag = True

        return flag

    def is_dataset_media_downloaded(self, dataset_name):
        """
        Whether the media data of a dataset is downloaded
        @param dataset_name:
        @return:
        """
        try:
            res = self.cursor.execute("select media_data from dataset where dataset_name=?",
                                      [dataset_name]).fetchone()
        except Exception as e:
            error_info = "Sqlite select dataset operation error: \n" + str(e)
            logger.error(error_info)
            raise CLIException(ExistCode.SQLITE_OPERATION_ERROR, error_info)
        flag = False
        if res:
            if res[0] == 1:
                flag = True

        return flag


if __name__ == '__main__':
    print(DB_PATH)
    print(DB_DIR_PATH)
    default_path = __get_default_path()
    print(default_path)
    db_path = __get_default_db_path()
    print(db_path)
    # print(get_local_dataset_path('CIFAR-10'))
    # print(get_local_split_path('CIFAR-100', 'test'))
    db_client = DBClient()
    print(db_client.get_sqlite_dict_list('select * from dataset'))
    # print(get_sqlite_dataframe('select * from dataset', get_sqlite_table_header('dataset')))
    df = db_client.get_sqlite_dataframe('select * from dataset')
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    # print(db_client.is_split_local_exist('CIFAR-10', 'test2'))
    print(db_client.is_dataset_label_downloaded('CIFAR-10'))
    print(db_client.is_dataset_media_downloaded('CIFAR-10'))
    print(get_config_dict())
