

# import pydantic_models
import models
from sqlalchemy import select,insert,update,delete,bindparam
from sqlalchemy import and_, or_,union,func

from mysqlalchemy import session_begin
from mysqlalchemy import session_execute
from mysqlalchemy import connection_begin
from mysqlalchemy import connection_execute
from mysqlalchemy import select_session
from mysqlalchemy import select_connection
from mysqlalchemy import conv_rows

import operator
import inspect
import re

from typing import List,Dict,Union,Callable
import data_processer_imple as imple

from abc import ABC, ABCMeta, abstractmethod

from myutil import get_callabletype
from myutil import get_methodtype
from myutil import get_argments
from myutil import get_commonparameters

from importlib import import_module

# 入出力を**keyargsで加工する
# プロセスリストを用意し
# それぞれのプロセスに**keyargsを入力
# 関数内において、無効な名前の引数はすべて出力に回す
# 有効な名前の引数は加工してkeyargsに出力
# return keyargs
# processer(**keyargs):
#     for f in process_list:
#         keyargs = f(**keyargs)
#     return keyargs
# 各 process の引数(*,named...,**keyargs):
class base_process(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self,**keyargs):
        pass
    @abstractmethod
    def __call__(self,**keyargs) -> Dict[str,any]:
        return keyargs
        
def call_process(
        process_list:List[Union[base_process,Callable]],
        **keyargs) -> Dict[str,any]:
    for process in process_list:
        keyargs.update(process(**keyargs))
    return keyargs

def load_process_list(
        process_list_id:int = 0,**keyargs
        ) -> List[Union[base_process,Callable]]:
    assert process_list_id > 0,"load process : input id error"
    
    process_list:List[Union[base_process,Callable]] = []
    
    data1     = models.process_list
    data2     = models.process
    state     = select(data1).where(data1.id == process_list_id)
    results   = select_scalars(state)
    list_name = ret.get(0,None)
    state     = select(data2).join(data1.process_id==data2.id).where(data1.id == process_list_id)
    results   = select_scalars(state)
    for ret in results:
        process_list.append(load_process(ret,**keyargs))
    return process_list
    
def load_process(
        process_info:models.process,**keyargs
        ) -> Union[base_process,Callable]:
    # return # need factory
    # id          : Mapped[int] = mapped_column(mstype.INTEGER,primary_key=True)
    # name        : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    # prefix      : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    # module_name : Mapped[str] = mapped_column(mstype.VARCHAR(length=256))
    # class_name  : Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    # func_name   : Mapped[str] = mapped_column(mstype.VARCHAR(length=256),nullable=True)
    
    is_class       = False
    is_wrapp       = False
    process_name   = process_info.name
    module_name    = process_info.module_name
    class_name     = process_info.class_name
    func_name      = process_info.func_name
    imple_name     = ""
    process_prefix = process_info.prefix
    
    if module_name == "":
        module_name = "imple"
        is_wrapp    = True
    if class_name is not None:
        is_wrapp &= True
    elif func_name is None:
        assert False,"process data error"
        
    # get module
    module_dict = globals()
    
    # モジュールを追加で読み込む
    top_module = module_name.split(".")[0]
    if top_module not in module_dict:
        module_dict[top_module] = import_module(top_module)
        module = module_dict[top_module]
        assert inspect.ismodule(module),"module import error"
    
    for key in module_name.split("."):
        if key in module_dict:
            module = module_dict[key]
            assert inspect.ismodule(module), "module path error"
            module_dict = module.__dict__
        else:
            assert False,"module path error"
    
    if is_wrapp:
        call_class = module_dict.get(class_name,None)
        assert call_class is not None,"class name error"
        call_class = call_class(**keyargs)
        return call_class
    elif func_name is None:
        func_name = "__call__"
    
    self_arg = []
    if class_name is not None:
        assert class_name in module_dict,"class name error"
        call_class  = module_dict[class_name]
        method_type = get_methodtype(call_class,func_name)
        assert method_type != "","class method name error"
        module_dict = call_class.__dict__
        if method_type == "function":
            args = get_commonparameters(
                call_class,
                keyargs,
                process_prefix)
            instance = call_class(**args)
            self_arg.append(instance)
        elif method_type == "classmethod":
            self_arg.append(call_class)
    else:
        assert func_name in module_dict,\
            "func name error"
        
    call_func =  module_dict[func_name]
    
    if re.match("make_",func_name): # enclodure
        args = get_commonparameters(
            call_func,
            keyargs,
            process_prefix)
        call_func2 = call_func(*self_arg,**args)
        assert inspect.isfunction(call_func2), \
            "enclodure return error"
        self_arg  = []
        call_func = call_func2
        
    def process_imple(**keyargs):
        args = get_commonparameters(
            call_func,
            keyargs,
            process_prefix)
        ret = call_func(*self_arg,**args)
        if type({}) != type(ret):
            ret = {
                key:val
                for key,val in zip([process_name],[ret])
            }
        return ret
    return process_imple
