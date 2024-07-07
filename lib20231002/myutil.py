from typing import Union,Dict,Callable
import datetime

def makecheck(base):
    check = type(base)
    return lambda obj:type(obj) == check

def zipdict(col,val):
    return {key:val for key,val in zip(col,val)}

def recursive_deep_copy(input_value):
    
    if not hasattr(input_value, '__iter__'):
        return input_value
    if type(input_value) == str:
        return input_value
    if type(input_value) == bytes:
        return input_value
    
    ret = type(input_value)()
    for obj in input_value:
        if hasattr(ret,"append"):
            ret.append(recursive_deep_copy(obj))
        else:
            ret[obj] = recursive_deep_copy(input_value[obj])
    return ret

def recursive_print_iter(indent,key,input_value):
    
    if not hasattr(input_value, '__iter__'):
        print(indent,key,input_value,type(input_value))
    elif type(input_value) == str:
        print(indent,key,input_value,type(input_value))
    elif type(input_value) == bytes:
        print(indent,key,input_value,type(input_value))
    else:
        print(indent,key,type(input_value))
        if hasattr(input_value,"__dict__"):
            for obj in input_value.__dict__:
                recursive_print_iter(indent+"    ",obj+":",input_value.__dict__[obj])
        else:
            for obj in input_value:
                if hasattr(input_value,"index"):
                    recursive_print_iter(indent+"    ","",obj)
                else:
                    recursive_print_iter(indent+"    ",obj+":",input_value[obj])

def recursive_print(input_value,name = ""):
    return recursive_print_iter("",name,input_value)
    
def recursive_str_iter(indent,key,input_value):
    
    ret = ""
    if not hasattr(input_value, '__iter__'):
        ret = ""+indent+key+input_value+type.__repr__(type(input_value)) + "\r\n"
    elif type(input_value) == str:
        ret = ""+indent+key+input_value+type.__repr__(type(input_value)) + "\r\n"
    elif type(input_value) == bytes:
        ret = ""+indent+key+input_value+type.__repr__(type(input_value)) + "\r\n"
    else:
        ret = ""+indent+key+type.__repr__(type(input_value)) + "\r\n"
    
        for obj in input_value:
            if hasattr(ret,"index"):
                ret += recursive_str_iter(indent+"    ","",obj)
            else:
                ret += recursive_str_iter(indent+"    ",obj+":",input_value[obj])
    return ret
    
def recursive_str(input_value,name = ""):
    return recursive_str_iter("",name,input_value)

import os,stat
def get_directries_info(path):
    ret = []
    for item in os.listdir(path):
        stat_value = os.stat("{}/{}".format(path,item))
        mode = stat_value.st_mode
        if stat.S_ISDIR(mode):
            ret.append({
                "name":item,
                "type":"directory"
            })
        elif stat.S_ISREG(mode):
            ret.append({
                "name":item,
                "type":"normal",
                "size":stat_value.st_size,
                "mtime":stat_value.st_mtime,
                "ctime":stat_value.st_ctime
            })
    return ret
    
from inspect import signature
from inspect import isfunction
from inspect import isclass
from inspect import ismethod
import re

def get_callabletype(_input):
    if isclass(_input):
        return "class" # has __init__ ?
    elif isclass(type(_input)):
        return "instance" # has __call__ ?
    elif ismethod(_input):
        return "method" # has __self__
    elif isfunction(_input):
        return "function"
    else:
        return ""

def get_methodtype(_class,_method:Union[str,Callable]):
    input_type  = type(_method).__name__ == "str"
    method_name = _method if input_type else _method.__name__
    method      = _class.__dict__.get(method_name,None)
    method_type = type(method).__name__
    return {
        "function"    :"function",
        "classmethod" :"classmethod",
        "staticmethod":"staticmethod",
    }.get(method_type,None)

def get_argments(_input):
    input_val = _input
    ret       = []
    params    = []
    isslice   = False
    ct = get_callabletype(input_val)
    if ct == "class":
        input_val = input_val.__init__
        isslice   = True
    elif ct == "instance":
        # un callable
        assert hasattr(input_val,"__call__"), \
            "instance object hasn't __call__"
        input_val = input_val.__call__
    elif ct == "method":
        pass
    elif ct == "function":
        pass

    if isroutine(input_val):
        params = signature(input_val).parameters
        
        for param in params:
            param_val  = params[param]
            match_obj = re.match("^\*+",str(param_val))
            if match_obj is not None:
                pos = match_obj.end()
            else:
                pos = 0
            ret.append("{}{}".format("*"*pos,param))
        if ismethod(input_val) or isslice:
            ret = ret[1:]
        
    return ret

def get_commonparameters(
        _input_val,
        _parameters:Dict[str,any],
        _prefix="",_suffix=""):
    ret      = {}
    argments = get_argments(_input_value)
    for key in _parameters.keys():
        if _prefix+key+_suffix in argments:
            ret.update({key:_parameters[_prefix+key+_suffix]})
        elif key in argments:
            ret.update({key:_parameters[key]})
    return ret
    
# TIME
def get_timedict(bt):
    return {
        n:t for n,t in zip(
            ["year","month","day","hour","minus","second"],
            [int(s) for s in re.split("[/ :]",bt)]
        )
    }
def get_nowtimestamp():
    return datetime.datetime.now().timestamp()
def get_timearray(bt):
    return [int(s) for s in re.split("[/ :]",bt)]

def get_timestamp(bt):
    ta = get_timearray(bt)
    ts = datetime.datetime(*ta).timestamp()
    return ts
