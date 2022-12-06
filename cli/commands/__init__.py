from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("odl-cli")
except PackageNotFoundError:
    # package is not installed
    pass