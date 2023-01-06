from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from dsdlsdk.exception.exception import DatasetPathNotExists


class DataRepo(ABC):
    """remote 多repo 抽象

    """
    def __repo_new(self, config, args):
        pass
    
    def __repo_delete(self, config, args):
        pass
    
    def __repo_auth(self, config, args):
        pass
    
    def __repo_content_list(sefl, config, args):
        pass
    
class DSDL(DataRepo):
    pass
    
    
class ODL(DataRepo):
    pass
    
class AIDE(DataRepo):
    pass