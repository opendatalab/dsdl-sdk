from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Union


@dataclass
class DownloadConfig:
    """config for downloadmanager

    Attributes:
        download_dir:
        Specify a cache directory to save the file to (overwrite the
            default cache dir).
    _extended_summary_
    """
    downlaod_dir : Union[str, Path]
    force_download : bool = False
    num_proc : Optional[int] = None
    max_retries : int = 1
    auth_dict : Optional[Dict] = None
    download_desc : Optional[str] = None