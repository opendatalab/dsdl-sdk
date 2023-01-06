from __future__ import annotations

import abc
import json
import os
import sys
import typing
from typing import (Any, ClassVar, Dict, Iterable, List, Optional, Tuple, Type,
                    Union)



def list_datasets(detail=False):
    """Lists the available datasets.
    Args:
        info (False): whether to return detailed inforather than just their names
    Returns:
        a list of dataset names or info dicts
    """
    if detail:
        return _list_dataset_detail()

    return _list_datasets()


def dataset_exists(name):
    """Checks if the dataset exists.
    Args:
        name: the name of the dataset
    Returns:
        True/False
    """
    conn = get_db_conn()
    # FIXME
    return bool

def load_dataset(name):
    """Loads the dataset with the given name.

    Args:
        name: the name of the dataset
    Returns:
        a :class:`Dataset`
    """
    return Dataset(name, _create=False)

class Dataset():
    def __init__(self,
                 name = None
                 _create = True):
        pass
    
class BuilderConfig():
    """
    Base class for `DatasetBuilder` data configuration.

    """
    def _torch_format(self, str):
        pass
    
    def _tf_format(self,str):
        pass
    
    pass

class DatasetBuilder():
    """
    Abstract base class for all datasets.



    DatasetBuilder usage:

    CIFAR_builder = dsdl.builder("CIFAR-10")
    CIFAR_info = CIFAR_builder.info
    CIFAR_builder.download_and_prepare()
    datasets = CIFAR_builder.as_dataset()

    train_dataset, test_dataset = datasets["train"], datasets["test"]

    train_dataset = train_dataset.shuffle(1024).batch(128)
    features = tf.compat.v1.data.make_one_shot_iterator(train_dataset).get_next()
    image, label = features['image'], features['label']
    """
    

    def get_metadata(self):
        pass

    def __init__(
        self,
        data_dir = None,
        config = None,
        version = None):
        pass

    def version(self):
        pass
    
    def release_notes(self):
        pass
    
    def data_dir(self):
        pass


    # def download_and_prepare(
    #     self,
    #     download_dir: Optional[str] = None,
    #     download_config: Optional[str] = None,
    #     file_format: Union[None, str] = None,) -> None:
    #     """Downloads dataset for reading.

    #     Args:
    #     download_dir: `str`, Defaults to "~/dsdl/".
    #     download_config: `config`, further configuration for downloading and preparing dataset.
    #     file_format: 

    #     Raises:
    #     IOError: if there is not enough disk space available.
    #     RuntimeError: when the config cannot be found.
    #     """
    #     pass