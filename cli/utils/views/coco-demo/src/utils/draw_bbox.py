from typing import List

import cv2
import numpy as np

from src.types import Array, Color

WHITE = (255, 255, 255)


def text_in_rectangle(  # pylint: disable=too-many-arguments
    image: Array,
    text: str,
    x1: int,
    y1: int,
    color: Color,
    font_scale=0.75,
    thickness=2,
    font_face=cv2.FONT_HERSHEY_DUPLEX,
    text_color: Color = WHITE,
) -> Array:
    (text_w, text_h), _ = cv2.getTextSize(
        text, fontFace=font_face, fontScale=font_scale, thickness=thickness
    )
    image = cv2.rectangle(
        image, (x1, y1), (x1 + text_w + 2, y1 - text_h - 4), color, -1
    )
    image = cv2.putText(
        image,
        text,
        (x1 + 1, y1 - 2),
        fontFace=font_face,
        fontScale=font_scale,
        color=text_color,
        thickness=thickness,
    )
    return image


def draw_bboxes(
    image: Array,
    bboxes: Array,
    colors: List[Color],
    class_names: List[str],
    alpha=0.2,
) -> Array:
    processed_image = image.copy()
    for bbox, color in zip(bboxes, colors):
        height, width = bbox[3] - bbox[1], bbox[2] - bbox[0]
        canvas = image.copy()
        patch = np.full((height, width, 3), color, dtype=np.uint8)
        canvas[bbox[1] : bbox[3], bbox[0] : bbox[2]] = patch
        processed_image = cv2.addWeighted(
            processed_image, 1 - alpha, canvas, alpha, 0.0
        )
    for bbox, color in zip(bboxes, colors):
        processed_image = cv2.rectangle(
            processed_image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2
        )
    font_scale = min(image.shape[:2]) / 1200 + 0.5
    thickness = round(font_scale * 2 + 0.5)
    for bbox, color, class_name in zip(bboxes, colors, class_names):
        processed_image = text_in_rectangle(
            processed_image,
            class_name,
            bbox[0],
            bbox[1],
            font_scale=font_scale,
            thickness=thickness,
            color=color,
        )
    return processed_image
