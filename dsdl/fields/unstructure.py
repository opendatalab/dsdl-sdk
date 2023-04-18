from .base_unstructured_field import UnstructuredObjectField, UnstructuredObjectFieldWithDomain


class Image(UnstructuredObjectField):
    data_schema = {
        "$id": "/unstructure/image",
        "title": "ImageField",
        "description": "Image field in dsdl.",
        "type": "string",
    }

    geometry_class = "Image"


class LabelMap(UnstructuredObjectFieldWithDomain):
    data_schema = {
        "$id": "/unstructure/labelmap",
        "title": "LabelMapField",
        "description": "LabelMap field in dsdl.",
        "type": "string",
    }

    geometry_class = "SegmentationMap"

    def additional_validate(self, value):
        if isinstance(self.actural_dom, list):
            assert len(self.actural_dom) == 1, "You can only assign one class dom in LabelMapField."
        return value


class InstanceMap(UnstructuredObjectField):
    data_schema = {
        "$id": "/unstructure/instancemap",
        "title": "InstanceMapField",
        "description": "InstanceMap field in dsdl.",
        "type": "string",
    }

    geometry_class = "InstanceMap"


class PointCloud(UnstructuredObjectField):
    default_args = {
        "load_dim": 3
    }

    args_schema = {
        "type": "object",
        "properties": {
            "load_dim": {"type": "integer"}
        },
        "minProperties": 1,
        "maxProperties": 1,
        "required": ["load_dim"]
    }

    data_schema = {
        "$id": "/unstructure/pointcloud",
        "title": "PointCloudField",
        "description": "PointCloud Field in dsdl.",
        "type": "string"
    }

    geometry_class = "PointCloud"


class Video(UnstructuredObjectField):
    data_schema = {
        "$id": "/unstructure/video",
        "title": "VideoField",
        "description": "Video field in dsdl.",
        "type": "string",
    }

    geometry_class = "Video"
