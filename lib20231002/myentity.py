import typing
from myutil import makecheck
is_list = makecheck([])
is_dict = makecheck({})

class entity:
    type = ""

class container_entity(entity):
    def __init__(obj):
        self.type =""
        self.obj  = obj
    def get(self,obj,**keyargs):
        return obj
    def get_typefree(selfobj,obj,name=None):
        if is_list(obj):
            obj.append(selfobj)
            return obj
        elif is_dict(obj) and name is not None:
            obj[name] = selfobj
            return obj
        else:
            return selfobj
    
class data_entity(container_entity):
    def __init__(obj):
        self.type = "data"
        self.obj  = obj
    def get(self,obj,name=None):
        return container_entity.get_typefree(self.obj,obj,name)
    
class arg_entity(container_entity):
    def __init__(obj:typing.List):
        self.type = "arg"
        self.obj  = obj
    def get(self,obj:typing.List,**keyargs):
        # concat array
        if is_list(obj):
            obj.extented(self.obj)
        else:
            obj = container_entity.get_typefree(self.obj,obj,**keyargs)
        return obj
    
class keyarg_entity(container_entity):
    def __init__(obj:typing.Dict):
        self.type = "keyarg"
        self.obj  = obj
    def get(self,obj:typing.Dict,**keyargs):
        # update dict
        if is_dict(obj):
            obj.update(self.obj)
        else:
            obj = container_entity.get_typefree(self.obj,obj,**keyargs)
        return obj