from typing import List

import pandas as pd
import streamlit as st
from stqdm import stqdm

from src.constants.colors import COLOR_MAP
from src.utils.display import load_and_annotate_image

st.set_page_config(
    # Change the title of the web page
    "Explore dataset",
    # Change the icon of the web page to a magnifier glass
    page_icon=":mag_right:",
)


def load_all_annotations() -> pd.DataFrame:
    return pd.read_parquet("/nvme/data/coco_demo/data/annotations/coco_val_2020.parquet.gzip")


# Cache the result to avoid reloading the full dataset
# and recomputing everytime we run the app
@st.experimental_memo()
def get_category_count() -> pd.DataFrame:
    return load_all_annotations().category_name.value_counts()


with st.sidebar:
    # Display a summary of the labels in the dataset
    category_count = get_category_count()
    st.write(category_count)
    st.write(f"{len(category_count)} Labels available")

    # Add a multiselect input to selection multiple labels
    available_labels = category_count.index.tolist()
    labels_to_display = st.multiselect("Labels to display", available_labels, default=["toaster"])


# Cache the last three requests
@st.experimental_memo(max_entries=3)
def get_selected_images(selected_categories: List[str]) -> pd.DataFrame:
    # Return all the images containing at least
    # one of the selected categories
    # return all the annotations on the selected images
    all_annotations = load_all_annotations()
    return all_annotations.groupby("image_name").filter(lambda g: g.category_name.isin(selected_categories).any())


annotations = get_selected_images(labels_to_display)
n_images = len(annotations[["image_name", "coco_url"]].drop_duplicates())
with st.sidebar:
    st.write(f"{n_images} images selected")

# Loop on images and display them
for (image_name, coco_url), image_annotations in stqdm(
    annotations.groupby(["image_name", "coco_url"]),
    desc="Displaying Images",
    total=n_images,
):
    st.image(
        load_and_annotate_image(coco_url, image_annotations, color_map=COLOR_MAP),
        caption=image_name,
    )
