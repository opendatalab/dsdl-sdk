import pytest
from pathlib import Path

from cli.commands import const


@pytest.fixture
def dsdl_program_name():
    return const.PROG_NAME


@pytest.fixture
def dsdl_path(tmp_path: Path) -> Path:
    return tmp_path / "dsdl-test" / ".dsdl"


@pytest.fixture
def dsdl_config_path(dsdl_path: Path) -> Path:
    return dsdl_path / const.__DEFAULT_CLI_CONFIG_FILE_NAME


@pytest.fixture
def dsdl_datasets_path(dsdl_path: Path) -> Path:
    return dsdl_path / "datasets"


@pytest.fixture
def dsdl_media_path(dsdl_path: Path) -> Path:
    return dsdl_datasets_path / const.DSDL_CLI_DATASET_NAME / "media"


@pytest.fixture
def dsdl_annotations_path(dsdl_path: Path) -> Path:
    return dsdl_datasets_path / const.DSDL_CLI_DATASET_NAME / "yml"


@pytest.fixture
def dsdl_parquet_path(dsdl_path: Path) -> Path:
    return dsdl_datasets_path / const.DSDL_CLI_DATASET_NAME / "parquet"


@pytest.fixture
def dsdl_sqlite_path(dsdl_path: Path) -> Path:
    return dsdl_path / const.__SQLITE_DB_NAME
