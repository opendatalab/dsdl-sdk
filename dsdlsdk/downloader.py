"""download API"""

from typing import Any, Iterable, Iterator, Optional, Tuple, Union

from dsdlsdk.exception.exception import DownLoadException


def get_downloader(*args: Any, **kwargs: Any) -> '_Downloader':
    return _Downloader(*args, **kwargs)


class DownloadError(DownLoadException):
    pass


class _Downloader(object):
    """Class download API """

    def __init__(self):
        """ Init _Downloader instance.

        """
        pass

    def tqdm(self) -> Iterator:
        """ Add a progression bar for the current download.
        
        """
        pass

    def download(
      self,
      url: str,
      destination_path: str,
      verify: bool = True):
        """Download url to given path.
        Args:
        url: 
        destination_path: `str`,
        verify:

        Returns:
        flag: check capacity
        """
        pass

    def _check_size(self, path:str):
        """check download file size compared to original datasets

        """
        pass
    
    