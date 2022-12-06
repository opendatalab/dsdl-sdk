from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("odl-cli")
except PackageNotFoundError:
    # package is not installed
    pass

from git import Repo

import git
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

#just keep the first 4 characters
abbrev = sha.split()[0][:4]

__version__ = 'v' + __version__ + '-' + abbrev