import json,inspect
from mysqlalchemy import get_scalar,model2dict
from myutil import get_methodtype
from models import parameters
from typing import List
from myentity import data_entity,arg_entity,keyarg_entity

loaded_parameters = {}
def load_param(type_name,index,localdict={}):
    key = type_name+":"+str(index)
    if key not in loaded_parameters:
        keyargs   = {"type":type_name,"id"  :index,}
        parameter = get_scalar(parameters,**keyargs)+[{}]
        parameter = parameter[0]
        parameter = model2dict(parameter)
        parameter["data"] = json.loads(parameter["data"])
        loaded_parameters[key] = parameter
        name            = parameter["name"]
        localdict[name] = parameter["data"]
    else:
        parameter = loaded_parameters[key]
    return parameter

# TODO
#   args,keyargs delivery
#     引数から返す？
#   depth2以降からargs/keyargsが返ってきた場合
#   どのように配布すればいいのかもう分からない
#     両方ある場合はエラー
def recurrent_expand(obj,localdict = {},loop_checker={}):
    lc = loop_checker
    ld = localdict
    if type(obj) == list:
        # TODO
        #   expand container entities
        #   多段展開が必要であればfor loopになる
        # return [recurrent_expand(v,ld,lc) for v in obj]
        ret = []
        for v in obj:
            v2  = recurrent_expand(v,ld,lc)
            ret = v2.get(ret)
        return ret
    elif type(obj) == dict:
        # TODO
        #   expand container entities
        #   多段展開が必要であればfor loopになる
        # return {k:recurrent_expand(obj[v],ld,lc) for v in obj}
        ret = {}
        for v in obj:
            v2  = recurrent_expand(obj[v],ld,lc)
            ret = v2.get(ret,name=v)
        return ret
    elif type(obj) == str:
        lc = {**lc}
        return expand_parameters(obj,ld,lc)
    else:
        return obj
    
def split_last(param,sep="."):
    splited = param.split(sep)
    head    = sep.join(splited[:-1])
    last    = splited[-1]
    if head == "":
        return [last]
    else:
        return [head,last]
    
imported_parameters = {}
def import_item(import_str,localdict={}):
    if import_str in localdict:
        imported = localdict[import_str]
    elif import_str in globals():
        imported = globals()[import_str]
    elif import_str in imported_parameters:
        imported = imported_parameters[import_str]
    else:
        import_keys = split_last(import_str,".")
        if len(import_keys) == 2:
            im = __import__(import_keys[0],fromlist=import_keys[1])
            imported = im.__dict__[import_keys[1]]
        else:
            imported = import_module(*import_keys)
        imported_parameters[import_str] = imported
    return imported

def make_prefix_action(prefix:str):
    len_prefix = len(prefix)
    def check_prefix_imple(key:str):
        if key[:len_prefix] != prefix:
            return False
        elif len(key[len_prefix:].split(":")) != 2:
            return False
        return True
    def load_prefix_imple(obj:str,loop_checker:Dict):
        loop_checker[obj] = loop_checker.get(obj,0)+1
        assert loop_checker[obj] < 3, "loop reference error {}".format(obj)
        obj = load_param(*obj[len_prefix:].split(":"),localdict)
        return obj
    return check_prefix_imple,load_prefix_imple

is_temp     ,load_temp      = make_prefix_action("temp:")
is_parameter,load_parameter = make_prefix_action("param:")
is_args     ,load_args      = make_prefix_action("args:")
is_keyargs  ,load_keyargs   = make_prefix_action("keyargs:")
    
def expand_parameters(obj = "",localdict = {},loop_checker={}):
    print(obj)
    if not type(obj) == str:
        return data_entity(obj)
    elif "locals:" == obj[:7]:
        obj = localdict[obj[7:]]
        return data_entity(obj)
    elif "globals:" == obj[:8]:
        obj = globals()[obj[8:]]
        return data_entity(obj)
    elif is_parameter(obj): # elif "param:" == obj[:6]:
        obj = load_parameter(obj)
    elif is_temp(obj):
        obj = load_temp(obj)
    elif is_args(obj):
        obj = load_args(obj)
        return arg_entity(obj)
    elif is_keyargs(obj):
        obj = load_keyargs(obj)
        return keyarg_entity(obj)
    else:
        return data_entity(obj)

    generated  = obj.get("generated") or False
    name       = obj.get("name") or ""
    parameters = obj.get("data") or {}
    import_str = parameters.get("import")  or ""
    args       = parameters.get("args")    or []
    keyargs    = parameters.get("keyargs") or {}
    # TODO expand container entities
    args       = recurrent_expand(args,localdict,loop_checker)
    keyargs    = recurrent_expand(keyargs,localdict,loop_checker)
    
    if import_str == "":
        assert len(args) * len(keyargs) == 0, \
            "response representation error"
        assert len(args) + len(keyargs) != 0, \
            "response error"
        if len(args) > 0:
            localdict[name] = args
        else:
            localdict[name] = keyargs
        return data_entity(localdict[name])
    
    imported    = import_item(import_str,localdict)
    if not generated:
        call_object = imported(*args,**keyargs)
    else:
        call_object = imported
    if not hasattr(imported,"__class__"):
        localdict[name] = call_object
        return data_entity(localdict[name])
    
    call_object = imported(*args,**keyargs)
    
    methods = parameters.get("methods")  or []
    for method_obj in methods:
        method = method_obj.get("method")  or "__call__"

        if not hasattr(call_object.__class__,method):
            continue

        self_arg = [] # to class
        method_type = get_methodtype(call_object,method)
        if method_type == "function":
            self_arg.append(call_object)
        elif method_type == "classmethod":
            self_arg.append(call_object.__class__)
        
        method_args    = method_obj.get("method_args") or []
        method_keyargs = method_obj.get("method_keyargs") or {}
        method_args    = recurrent_expand(method_args,localdict,loop_checker)
        method_keyargs = recurrent_expand(method_keyargs,localdict,loop_checker)

        method_ret = call_object.__dict__[method](*self_arg,*method_args,**method_keyargs)
        method_result =  method_obj.get("use_methodresult") or False
        if method_result:
            call_object = method_ret
    
    localdict[name] = call_object
    return data_entity(call_object)

def execute_parameters(parameters:List[str]):
    localdict    = {}
    converted    = []
    for parameter in parameters:
        if is_temp(parameter):
            # to local
            expand_parameters(parameter,localdict)
        elif is_parameter(parameter):
            ret = expand_parameters(parameter,localdict)
            converted = ret.get(converted)
            # converted.append(ret)
    ret = []
    for action in converted:
        ret = [action(*ret)]
    return ret[0]
