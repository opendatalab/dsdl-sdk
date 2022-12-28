from .local_studio_view import LocalStudioView
from .remote_studio_view import RemoteStudioView


def StudioView(dataset_name, task_type, n=None, shuffle=False, remote=False):
    if remote:
        return RemoteStudioView(dataset_name, task_type, n=n, shuffle=shuffle)
    else:
        return LocalStudioView(dataset_name, task_type, n=n, shuffle=shuffle)


__all__ = [
    "StudioView",
]
