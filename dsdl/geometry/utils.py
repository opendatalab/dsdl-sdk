import numpy as np
from PIL import Image, ExifTags
from typing import Tuple, Any
import io
from dsdl.exception import FileReadError


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


def video_encode(backend: str, bytes_: io.BytesIO, **kwargs):
    backend = backend.lower()
    assert backend in ("decord", "pyav", "pims")
    video_reader, num_frames = None, 0
    if backend == "decord":
        try:
            import decord
        except ImportError:
            raise ImportError('Please run "pip install decord" to install Decord first.')
        video_reader = decord.VideoReader(bytes_, num_threads=kwargs.get("num_threads", 1))
        num_frames = len(video_reader)

    elif backend == "pyav":
        try:
            import av
        except ImportError:
            raise ImportError('Please run "conda install av -c conda-forge" '
                              'or "pip install av" to install PyAV first.')
        video_reader = av.open(bytes_)
        num_frames = video_reader.streams.video[0].frames

    elif backend == "pims":
        mode = kwargs.get("mode", "accurate")
        assert mode in ['accurate', 'efficient']
        try:
            import pims
        except ImportError:
            raise ImportError('Please run "conda install pims -c conda-forge" '
                              'or "pip install pims" to install pims first.')
        if mode == 'accurate':
            container = pims.PyAVReaderIndexed(bytes_)
        else:
            container = pims.PyAVReaderTimed(bytes_)

        video_reader = container
        num_frames = len(video_reader)

    return video_reader, num_frames


def video_decode(backend: str, video_reader, frame_inds: np.ndarray, **kwargs):
    backend = backend.lower()
    assert backend in ("decord", "pyav", "pims")
    if frame_inds.ndim != 1:
        frame_inds = np.squeeze(frame_inds)

    if backend == "decord":
        mode = kwargs.get("mode", "accurate")
        assert mode in ("accurate", "efficient")
        if mode == "accurate":
            imgs = video_reader.get_batch(frame_inds).asnumpy()
            imgs = list(imgs)
        else:  # efficient
            video_reader.seek(0)
            imgs = list()
            for idx in frame_inds:
                video_reader.seek(idx)
                frame = video_reader.next()
                imgs.append(frame.asnumpy())


    elif backend == "pyav":
        mode = kwargs.get("mode", "accurate")
        assert mode in ("accurate", "efficient")
        imgs = list()
        if kwargs.get("multi_thread", False):
            video_reader.streams.video[0].thread_type = 'AUTO'
        if mode == 'accurate':
            # set max indice to make early stop
            max_inds = frame_inds
            i = 0
            for frame in video_reader.decode(video=0):
                if i > max_inds + 1:
                    break
                imgs.append(frame.to_rgb().to_ndarray())
                i += 1
            # the available frame in pyav may be less than its length,
            # which may raise error
            imgs = [imgs[i % len(imgs)] for i in frame_inds]
        else:  # mode == 'efficient'

            def frame_generator(container, stream):
                """Frame generator for PyAV."""
                for packet in container.demux(stream):
                    for frame in packet.decode():
                        if frame:
                            return frame.to_rgb().to_ndarray()

            for frame in video_reader.decode(video=0):
                backup_frame = frame
                break
            stream = video_reader.streams.video[0]
            for idx in frame_inds:
                pts_scale = stream.average_rate * stream.time_base
                frame_pts = int(idx / pts_scale)
                video_reader.seek(
                    frame_pts, any_frame=False, backward=True, stream=stream)
                frame = frame_generator(video_reader, stream)
                if frame is not None:
                    imgs.append(frame)
                    backup_frame = frame
                else:
                    imgs.append(backup_frame)
    else:  # pims backend
        imgs = [video_reader[idx] for idx in frame_inds]

    del video_reader

    return imgs
