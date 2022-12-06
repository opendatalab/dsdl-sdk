from importlib.metadata import version, PackageNotFoundError
import git
from setuptools_scm import get_version

try:
    __version__ = version("odl-cli") # return '0.1.1'
except PackageNotFoundError:
    # package is not installed
    pass

__version__ = get_version() # return '0.1.dev519+g37fcc3b.d20221206'

__version_tuple__ = tuple(__version__.split("."))
dev_version = ''
for ele in __version_tuple__:    
    if ele.startswith('dev'):
        dev_version = ele
    break    
__version__ = __version__ + dev_version
    
repo = git.Repo(search_parent_directories=True)
sha = repo.head.object.hexsha

#just keep the first 4 characters
abbrev = sha.split()[0][:4]

__version__ = 'v' + __version__  + abbrev

