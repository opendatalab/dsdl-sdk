import numpy as np
from PIL import Image, ExifTags
from typing import Tuple, Any
import io
from ..exception import FileReadError


def get_image_rotation(image: Image) -> int:
    """Get the rotation degree from the image file's exif message.

    Arguments:
        image: A PIL.Image object.

     Returns:
         The degree read from image's exif message.
    """
    try:
        for k, v in ExifTags.TAGS.items():
            if v == "Orientation":
                break
        orientation_degree_map = {3: 180, 6: 270, 8: 90}
        return orientation_degree_map.get(image._getexif()[k], 0)
    except Exception:
        return 0


def bytes_to_numpy(bytes_: io.BytesIO) -> np.ndarray:  # type: ignore[type-arg]
    """
    Transfer bytes into numpy array.

    Arguments:
        bytes_: The bytes to transfer.

    Raises:
        FileReadError: When `bytes_` cannot be loaded as an image.

    Returns:
        The transferred numpy array.
    """
    try:
        image = Image.open(bytes_)
    except Exception as e:
        raise FileReadError(f"Failed to convert bytes to an array. {e}") from None
    rotation = get_image_rotation(image)
    if rotation:
        image = image.rotate(rotation, expand=True)
    if image.mode == "RGB":
        shape: Tuple[int, ...] = (image.size[1], image.size[0], 3)
        dtype: Any = np.uint8
    elif image.mode == "RGBA":
        shape: Tuple[int, ...] = (image.size[1], image.size[0], 4)
        dtype: Any = np.uint8
    elif image.mode == "P":
        shape = (image.size[1], image.size[0])
        dtype = np.uint8
    elif image.mode == "I":
        shape = (image.size[1], image.size[0])
        dtype = np.int32
    elif image.mode == "L":
        shape = (image.size[1], image.size[0])
        dtype = np.uint8
    elif image.mode == "LA":
        shape = (image.size[1], image.size[0], 2)
        dtype = np.uint8
    else:
        raise FileReadError("Currently unsupported image type")
    image_ = np.array(image.getdata(), dtype=dtype).reshape(*shape)
    return image_
