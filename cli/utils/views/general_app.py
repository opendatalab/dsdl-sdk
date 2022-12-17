import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image

from dsdl.tools import studio_view


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
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        os._exit(e.code)

    dataset_name = args.dataset_name
    task_type = args.task_type
    number = args.number

    generator = studio_view(dataset_name, task_type)

    image_list = []
    i = 0
    for image in generator:
        if i == number:
            break
        else:
            image_list.append(image)
        i += 1

    st.title("Files")

    display_images(image_list, max_images=numbers)


def display_images(
    images: [PilImage],
    columns=5,
    width=20,
    height=8,
    max_images=100,
    label_wrap_length=50,
    label_font_size=8,
):
    if not images:
        print("No images to display.")
        return
    if len(images) > max_images:
        print(f"Showing {max_images} images of {len(images)}:")
        images = images[0:max_images]
    height = max(height, int(len(images) / columns) * height)
    plt.figure(figsize=(width, height))
    for i, image in enumerate(images):
        plt.subplot(int(len(images) / columns + 1), columns, i + 1)
        plt.imshow(image)
        if hasattr(image, "filename"):
            title = image.filename
            if title.endswith("/"):
                title = title[0:-1]
            title = os.path.basename(title)
            title = textwrap.wrap(title, label_wrap_length)
            title = "\n".join(title)
            plt.title(title, fontsize=label_font_size)


if __name__ == "__main__":
    main()
