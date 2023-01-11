import platform

import pyarrow
from packaging import version

if version.parse(platform.python_version()) < version.parse('3.7'):
    raise ImportWarning(
        'Python version no supported! Please using Python >= 3.7'
    )
    
if version.parse(pyarrow.__version__).major < 5:
    raise ImportWarning(
        'xxxxxxxxxxx'
    )
    
# still need other utils like logging xxx