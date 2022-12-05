# import the Package
import os
import sys
import base64
from io import BytesIO
import argparse

sys.path.append(f"{os.path.dirname(os.path.abspath(__file__))}/../../")

import streamlit as st
from PIL import Image
import pandas as pd

from utils.query import SplitReader


def main():
    parser = argparse.ArgumentParser(description="streamlit app inside odl-cli.")

    parser.add_argument(
        "--dataset-name",
    )
    parser.add_argument(
        "--split-name",
        default="train",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        os._exit(e.code)

    dataset_name = args.dataset_name
    split_name = args.split_name
    st.title("Files")
    explore_app(dataset_name, split_name)


def explore_app(dataset_name: str, split_name: str):
    split_name = "train"  # currently only support train split
    split_reader = SplitReader(dataset_name, split_name)

    SPLIT_DF = pd.DataFrame()

    SPLIT_DF["file_path"] = split_reader.get_image_samples(10)
    SPLIT_DF["split"] = split_name
    SPLIT_DF["thumbnail"] = SPLIT_DF.file_path.map(lambda x: image_formatter(x))
    DF = pd.DataFrame(
        {
            "thumbnail": SPLIT_DF["thumbnail"],
            "split": SPLIT_DF["split"],
        }
    )

    DF_HTML = convert_df(DF)

    pd.set_option("display.max_colwidth", -1)
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
    i.thumbnail((1280, 1280), Image.LANCZOS)
    return i


def image_base64(im):
    if isinstance(im, str):
        im = get_thumbnail(im)
    with BytesIO() as buffer:
        im.save(buffer, "jpeg")
        return base64.b64encode(buffer.getvalue()).decode()


def image_formatter(im):
    return f'<img src="data:image/jpeg;base64,{image_base64(im)}">'


if __name__ == "__main__":
    main()
