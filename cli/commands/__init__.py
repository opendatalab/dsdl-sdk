from importlib.metadata import version, PackageNotFoundError
# import git
from setuptools_scm import get_version

try:
    __short_version__ = version("odl-cli") # return '0.1.1'
except PackageNotFoundError:
    # package is not installed
    pass

# __full_version__ = get_version() # return '0.1.dev519+g37fcc3b.d20221206'

# __version_tuple__ = tuple(__full_version__.split("."))


# __version_dev_part__ = ''
# for ele in __version_tuple__:    
#     if ele.startswith('dev'):
#         _tmp_tuple = tuple(ele.split("+"))
#         for ele2 in _tmp_tuple:
#             if ele2.startswith('dev'):
#                 __version_dev_part__ = ele2 # return 'devxxx'
#                 break
    
# repo = git.Repo(search_parent_directories=True)
# sha = repo.head.object.hexsha
# #just keep the first 4 characters
# __version_commitID_part__ = sha.split()[0][:4]

# __version__ = 'v' + __short_version__  + '.' + __version_dev_part__ + __version_commitID_part__
# __version__ = 'v' + __short_version__  + '.' + __version_dev_part__
__version__ = 'v' + __short_version__