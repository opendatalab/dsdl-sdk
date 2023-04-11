from .base_geometry import BaseGeometry
import io
from .utils import video_decode, video_encode
from fastjsonschema import compile
import numpy as np


def _compile_schema(schema):
    schema = schema.copy()
    schema["$schema"] = "http://json-schema.org/draft-07/schema"
    res = compile(schema)
    return res


class Video(BaseGeometry):
    DEFAULT_BACKEND = "decord"
    ALL_BACKENDS = ("decord", "pyav", "pims")
    ENCODE_DEFAUTL_KWARGS = {
        "decord": {
            "num_threads": 1
        },
        "pyav": {},
        "pims": {
            "mode": "accurate"
        }
    }

    ENCODE_SCHEMA = {
        "decord": _compile_schema({
            "type": "object",
            "properties": {
                "num_threads": {"type": "integer", "minimum": 1}
            },
            "minProperties": 1,
            "maxProperties": 1,
            "required": ["num_threads"]
        }),

        "pyav": _compile_schema({
            "type": "object",
            "minProperties": 0,
            "maxProperties": 0,
        }),

        "pims": _compile_schema({
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["accurate", "efficient"]}
            },
            "minProperties": 1,
            "maxProperties": 1,
            "required": ["mode"]
        })
    }

    DECODE_DEFAULT_KWARGS = {
        "decord": {
            "mode": "accurate"
        },

        "pyav": {
            "mode": "accurate",
            "multi_thread": False
        },

        "pims": {}
    }

    DECODE_SCHEMA = {
        "decord": _compile_schema({
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["accurate", "efficient"]}
            },
            "minProperties": 1,
            "maxProperties": 1,
            "required": ["mode"]
        }),
        "pyav": _compile_schema({
            "type": "object",
            "properties": {
                "mode": {"type": "string", "enum": ["accurate", "efficient"]},
                "multi_thread": {"type": "boolean"}
            },
            "minProperties": 2,
            "maxProperties": 2,
            "required": ["mode", "multi_thread"]
        }),
        "pims": _compile_schema({
            "type": "object",
            "minProperties": 0,
            "maxProperties": 0,
        }),
    }

    def __init__(self, value, file_reader):
        """A Geometry class which abstracts a Video object.

        Args:
            value: The relative path of the current video object.
            file_reader: The file reader object of the current video object.
        """
        self._loc = value
        self._reader = file_reader
        self.namespace = None
        _splits = value.split(".")
        if len(_splits) > 1:
            self._ext = value.split(".")[-1].lower()
        else:
            self._ext = ""

        self.backend = None
        self.video_reader = None
        self.frame_num = None
        self.encode_args = None

    def set_namespace(self, struct_obj):
        self.namespace = struct_obj
        self._reader = struct_obj.file_reader

    @property
    def location(self):
        """
        Returns:
            The relative path of the current image.
        """
        return self._loc

    def to_bytes(self):
        """Turn Video object to bytes.

        Returns:
            The bytes of the current video.
        """
        return io.BytesIO(self._reader.read(self._loc))

    def init_video_reader(self, backend=DEFAULT_BACKEND, **kwargs):
        assert backend in self.ALL_BACKENDS
        all_args = self.ENCODE_DEFAUTL_KWARGS[backend]
        all_args.update(kwargs)
        self.ENCODE_SCHEMA[backend](all_args)
        video_reader, frame_num = video_encode(backend, self.to_bytes(), **all_args)
        self.backend = backend
        self.encode_args = all_args
        self.video_reader = video_reader
        self.frame_num = frame_num
        return video_reader, frame_num

    def to_array(self, frame_ids: np.ndarray, **kwargs):
        """Turn Video object to a numpy.ndarray list.

        Returns:
            The `np.ndarray` object of the current image.
        """
        all_args = self.DECODE_DEFAULT_KWARGS[self.backend]
        all_args.update(kwargs)
        self.DECODE_SCHEMA[self.backend](all_args)
        imgs = video_decode(self.backend, self.video_reader, frame_ids, **all_args)
        return imgs

    def __repr__(self):
        return f"path:{self.location}"
