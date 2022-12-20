import argparse
import os

import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image

from dsdl.tools import StudioView


def main():
    parser = argparse.ArgumentParser(description="streamlit app inside odl-cli.")

    parser.add_argument(
        "--dataset-name",
    )
    parser.add_argument(
        "--task-type",
    )
    parser.add_argument(
        "--number",
        type=int,
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        os._exit(e.code)

    dataset_name = args.dataset_name
    task_type = args.task_type
    number = args.number

    # ex. iterator = StudioView("CIFAR-10", "classification", n=10, shuffle=True)
    iterator = StudioView(dataset_name, task_type, n=number, shuffle=True)

    image_list = []
    i = 0
    for image in iterator:
        if i == number:
            break
        else:
            image_list.append(image)
        i += 1

    st.title("Files")

    # display_images(image_list, max_images=number)
    image_grid_main(image_list, number)


def image_grid_main(images: [Image], max_images):
    st.title("Image Grid Display")
    if not images:
        print("No images to display.")
        return
    if len(images) > max_images:
        print(f"Showing {max_images} images of {len(images)}:")
        images = images[0:max_images]
    n = st.number_input("Select Grid Width", 1, 5, 3)

    groups = []
    for i in range(0, len(images), n):
        groups.append(images[i : i + n])

    for group in groups:
        cols = st.columns(n)
        for i, image_file in enumerate(group):
            cols[i].image(image_file)


if __name__ == "__main__":
    main()
