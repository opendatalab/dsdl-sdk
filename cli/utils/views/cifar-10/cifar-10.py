# import the Package
import os
import sys
import base64
from io import BytesIO
import urllib

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../../")

import duckdb
import streamlit as st
from PIL import Image
import pandas as pd

from utils.admin import DBClient

class_name = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]


def main():
    st.title("CIFAR-10")
    st.sidebar.title("CIFAR-10")
    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        [
            "Show dataset introductions",
            "Show dataset details",
            "Show source code",
            "Explore the app",
        ],
    )
    if app_mode == "Show dataset introductions":
        st.sidebar.success("Displaying the introductions of dataset.")
        st.write(INTRO_DOC_STR)
    elif app_mode == "Show dataset details":
        st.sidebar.success("Displaying the details of dataset.")
        st.json(DATASET_DOC_STR, expanded=True)
    elif app_mode == "Show source code":
        st.sidebar.success("Displaying the dataset source code.")
        st.code(CODE_FILE_STR, language="python")
    elif app_mode == "Explore the app":
        st.sidebar.success("Exploring the dataset.")
        explore_app()


def parquet_filter(
    parquet_path, select_cols="*", filter_cond="", limit=None, offset=None, samples=None
):
    cursor = duckdb.connect(database=":memory:")
    view_sql = (
        """create or replace view dataset as select * from parquet_scan('%s');"""
        % parquet_path
    )
    cursor.execute(view_sql)
    query_sql = "select {cols} from dataset".format(cols=select_cols)

    # add where condition
    if filter_cond:
        query_sql = query_sql + " where " + filter_cond

    # add limit
    if limit:
        query_sql = query_sql + " limit " + str(limit)

    # add offset
    if offset:
        query_sql = query_sql + " offset " + str(offset)

    # add random samples
    if samples:
        # to do: implement %
        query_sql = "select * from (" + query_sql + ") using sample %d rows" % samples

    # print(query_sql)
    df = cursor.execute(query_sql).fetch_df()
    return df


def explore_app():
    # the following varibles should be read from dsdl database by duckdb
    dbcli = DBClient()
    dataset_dir_path = dbcli.get_local_dataset_path("CIFAR-10")
    parquet_dir_path = os.path.join(dataset_dir_path, "parquet")
    parquet_train_file = os.path.join(parquet_dir_path, "train.parquet")
    parquet_test_file = os.path.join(parquet_dir_path, "test.parquet")

    TRAIN_DF = parquet_filter(
        parquet_path=parquet_train_file,
        select_cols="*",
        filter_cond="",
        limit=None,
        offset=None,
        samples=None,
    )
    TEST_DF = parquet_filter(
        parquet_path=parquet_test_file,
        select_cols="*",
        filter_cond="",
        limit=None,
        offset=None,
        samples=None,
    )

    TRAIN_DF["split"] = "train"
    TEST_DF["split"] = "test"
    DF = pd.concat([TRAIN_DF, TEST_DF], ignore_index=True)
    # DF['path'] = dataset_dir_path + DF['image']
    DF["path"] = DF["image"].apply(lambda x: os.path.join(dataset_dir_path, x))
    DF["thumbnail"] = DF.path.map(lambda x: image_formatter(x))
    DF = pd.DataFrame(
        {
            "name": DF["image"],
            "label": DF["label"],
            "split": DF["split"],
            "path": DF["path"],
            "thumbnail": DF["thumbnail"],
        }
    )

    DF_HTML = convert_df(DF.head(100))

    pd.set_option("display.max_colwidth", None)
    st.markdown(DF_HTML, unsafe_allow_html=True)


@st.cache
def convert_df(input_df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return input_df.to_html(
        formatters={"img": image_formatter},
        escape=False,
    )


def get_thumbnail(path):
    i = Image.open(path)
    i.thumbnail((320, 320), Image.Resampling.LANCZOS)
    return i


def image_base64(im):
    if isinstance(im, str):
        im = get_thumbnail(im)
    with BytesIO() as buffer:
        im.save(buffer, "jpeg")
        return base64.b64encode(buffer.getvalue()).decode()


def image_formatter(im):
    return f'<img src="data:image/jpeg;base64,{image_base64(im)}">'


intro_doc_path = "https://huggingface.co/datasets/cifar10/raw/main/README.md"
dataset_doc_path = "https://huggingface.co/datasets/cifar10/raw/main/dataset_infos.json"
code_file_path = "https://huggingface.co/datasets/cifar10/raw/main/cifar10.py"

# Download a single file and make its content available as a string.
@st.experimental_singleton(show_spinner=False)
def get_web_file_content_as_string(url):
    """
    Get raw data content from a web file.

    :param  type: local or web
    :returns file content in string format
    """
    response = urllib.request.urlopen(url)
    return response.read().decode("utf-8")


INTRO_DOC_STR = get_web_file_content_as_string(intro_doc_path)
DATASET_DOC_STR = get_web_file_content_as_string(dataset_doc_path)
CODE_FILE_STR = get_web_file_content_as_string(code_file_path)


if __name__ == "__main__":
    main()
