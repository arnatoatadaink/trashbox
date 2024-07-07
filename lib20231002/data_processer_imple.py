

from data_processer_base import base_process
from typing import List,Dict,Union,Callable

class test_process(base_process):
    def __init__(self,**keyargs):
        pass
    def __call__(self,print_str:str="",**keyargs) -> Dict[str,any]:
        keyargs["printed"] = print("test process",print_str)
        return keyargs
    