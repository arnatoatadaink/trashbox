from typing import Union,Dict,List
from sqlalchemy.orm import Session
from sqlalchemy.orm import InstrumentedAttribute as IA
from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import BinaryExpression as BE,BindParameter as BP
from sqlalchemy import bindparam
from models import Engine,Base

from sqlalchemy import select,update,delete
from sqlalchemy.dialects.mysql import insert

def session_begin(func):
    with Session(Engine) as session:
        with session.begin():
            return func(session)
    return False
def session_execute(func):
    with Session(Engine) as session:
        return func(session)
    return False
def connection_begin(func):
    with Engine.begin() as connect:
        return func(connect)
    return False
def connection_execute(func):
    with Engine.connect() as connect:
        return func(connect)
    return False
    
def select_scalars(state,*arg):
    with Session(Engine) as session:
        ret = []
        result = session.scalars(state,*arg)
        for row in result:
            ret.append(row)
        return ret
    return False
        
def select_session(state,*arg):
    with Session(Engine) as session:
        ret = []
        result = session.execute(state,*arg)
        for row in result:
            ret.append(row)
        return ret
    return False
        
def select_connection(state,*arg):
    with Engine.connect() as connect:
        ret = []
        result = connect.execute(state,*arg)
        for row in result:
            ret.append(row)
        return ret

def conv_rows(orm_array,receive_model):
    for i in range(len(orm_array)):
        orm_array[i] = receive_model.from_orm(orm_array[i])
    return orm_array

def model2dict(obj):
    if not hasattr(obj,"__annotations__"):
        return {}
    else:
        return {k:obj.__dict__[k] for k in obj.__annotations__}
        
my_bindkey = lambda k: "b_"+k
my_bindparam = lambda k:bindparam(my_bindkey(k))

def conv_wheres(arr:Union[List[Union[str,IA]],Dict[str,BP]]):
    if type(arr) != list:
        return arr
    for i in range(len(arr)):
        v = arr[i]
        if type(v) == IA:
            key = v._annotations["proxy_key"]
            arr[i] = v==my_bindparam(key)
    return arr

def conv_values(arr:List[Union[str,IA]]):
    ret = {}
    for v in arr:
        t = type(v)
        if t == IA or t == Column:
            key = v._annotations["proxy_key"]
            ret[key] = my_bindparam(key)
        else:
            ret[v] = my_bindparam(v)
    return ret
    
# avoid reserve word
def conv_bindkey(params:List[Dict[str,any]]):
    return [
        { my_bindkey(k):d[k] for k in d }
        for d in params
    ]

def get_bulk_upsert(
        model,
        keys:List[IA],
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]]):
    values = conv_values(values)
    params = conv_bindkey(params)
    state  = insert(model) \
            .values(values)
    state  = state.on_duplicate_key_update(
            status='U',
            **state.inserted,
        ).returning(*keys)
                
    return state,params

def get_bulk_insert(
        model,
        keys:List[IA],
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]]):
    values = conv_values(values)
    params = conv_bindkey(params)
    state  = insert(model) \
                .values(values) \
                .returning(*keys)
    return state,params

def get_bulk_update(
        model,
        wheres:List[Union[BE,IA]], # model.column==bindparam("column_name")
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]]):
    wheres = conv_wheres(wheres)
    values = conv_values(values)
    params = conv_bindkey(params)
    state  = update(model) \
                .where(*wheres) \
                .values(values)
    return state,params

def get_bulk_delete(
        model,
        wheres:List[Union[BE,IA]], # model.column==bindparam("column_name")
        params:List[Dict[str,any]]):
    wheres = conv_wheres(wheres)
    params = conv_bindkey(params)
    state  = delete(model) \
                .where(*wheres)
    return state,params

def make_bulk_upsert(
        model,
        keys:List[IA],
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]],
        debug_call:bool=False):
    state,params = get_bulk_upsert(model,keys,values,params)
    if debug_call:
        print("state  : ",state)
        print("params : ",params)
    def bulk_upsert_imple(session):
        return session.execute(state,params)
    return bulk_upsert_imple

def make_bulk_insert(
        model,
        keys:List[IA],
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]],
        debug_call:bool=False):
    state,params = get_bulk_insert(model,keys,values,params)
    if debug_call:
        print("state  : ",state)
        print("params : ",params)
    def bulk_insert_imple(session):
        return session.execute(state,params)
    return bulk_insert_imple

def make_bulk_update(
        model,
        wheres:List[Union[BE,IA]], # model.column==bindparam("column_name")
        values:Union[List[Union[str,IA]],Dict[str,BP]], # {"column_name":bindparam("column_name") }
        params:List[Dict[str,any]],
        debug_call:bool=False):
    state,params = get_bulk_update(model,wheres,values,params)
    if debug_call:
        print("state  : ",state)
        print("params : ",params)
    def bulk_update_imple(session):
        return session.execute(state,params)
    return bulk_update_imple

def make_bulk_delete(
        model,
        wheres:List[Union[BE,IA]], # model.column==bindparam("column_name")
        params:List[Dict[str,any]],
        debug_call:bool=False):
    state,params = get_bulk_delete(model,wheres,params)
    if debug_call:
        print("state  : ",state)
        print("params : ",params)
    def bulk_delete_imple(session):
        return session.execute(state,params)
    return bulk_delete_imple

def pickup_data(ttype:Base,params:Dict)->Union[Dict,bool]:
    keys   = {}
    values = {}

    for anno_key in ttype.__annotations__.keys():
        col = ttype.__dict__[anno_key]
        
        if not hasattr(col,"__dict__"):
            # relationship has'nt __dict__
            continue
        elif anno_key not in params:
            f = "func set_data input args error : need keys {}"
            print(f.format(anno_key))
            return False
        elif col.primary_key:
            keys[anno_key]   = params[anno_key];
        else:
            values[anno_key] = params[anno_key]
    
    datas = {}
    datas.update(keys)
    datas.update(values)
    return datas
    
def pickup_columns(ttype:Base,exculude:List[str]=[])->List[IA]:
    columns = ttype.__annotations__.keys()
    columns = [ttype.__dict__[c] for c in columns if c not in exculude]
    columns = [c for c in columns if hasattr(c,"__dict__")]
    return columns

def get_scalar(ttype,**keyargs):
    wheres = []
    for col in ttype.__table__.primary_key.c:
        if col.name not in keyargs:
            continue
        wheres.append(col == keyargs[col.name])
    
    state = select(ttype).where(*wheres)
    return select_scalars(state)

def get_data(ttype,rtype,**keyargs):
    wheres = []
    for col in ttype.__table__.primary_key.c:
        if col.name not in keyargs:
            continue
        wheres.append(col == keyargs[col.name])
    
    state = select(ttype).where(*wheres)
    return conv_rows(select_scalars(state),rtype)
    
def get_data2(ttype,rtype,exclude=[],**keyargs):
    wheres = []
    for col in ttype.__table__.primary_key.c:
        if col.name not in keyargs:
            continue
        wheres.append(col == keyargs[col.name])

    columns = pickup_columns(ttype,exclude)
    state   = select(*columns).where(*wheres)
    return conv_rows(select_session(state),rtype)    

def set_data(ttype,**keyargs):

    datas = pickup_data(ttype,keyargs)
    if not datas:
        return False
    
    upsert_datas = [datas]
    columns      = pickup_columns(ttype)
    no_return = []
    
    action = make_bulk_upsert(ttype,
        no_return,columns,upsert_datas,True)
        
    def call_funcarray(session):
        ret = []
        ret.append(action(session))
        return ret
    ret = connection_begin(call_funcarray)
    debug_print("sql posted")
    return ret

# TODO 引数の明示
def set_datas(type_clips:List[Dict[str,any]] = []):
    actions = []
    for type_clip in type_clips:
        ttype       = type_clip["ttype"]
        value_array = type_clip["value_array"]
        
        upsert_datas = []
        for check_targets in value_array:
            datas = pickup_data(ttype,check_targets)
            if not datas:
                return False
            upsert_datas.append(datas)
            
        no_return = []
        columns   = pickup_columns(ttype)
        
        action = make_bulk_upsert(ttype,
            no_return,columns,upsert_datas,True)
            
        actions.append(action)
        
    def call_funcarray(session):
        ret = []
        for action in actions:
            ret.append(action(session))
        return ret
    ret = connection_begin(call_funcarray)
    debug_print("sql posted")
    return ret

def get_columnkeys(ttype):
    ret = []
    for r in ttype.__annotations__:
        c = ttype.__dict__[r]
        k = ""
        if hasattr(c,"__dict__"):
            k = c.key
        ret.append([r,k])
    return ret
def rename_annotation(ttype,dic):
    ret   = {}
    ckeys = get_columnkeys(ttype)
    for anno,col in ckeys:
        ret[anno] = dic[col]
    return ret
def get_columnsdict(ttype,annotation_base=False):
    ret = {}
    for r in ttype.__table__.columns:
        ret[r.name] = r
    if annotation_base:
        ret = rename_annotation(ttype,ret)
    return ret
def get_IAdict(ttype,annotation_base=False):
    ret = {}
    for r in ttype.__annotations__:
        c = ttype.__dict__[r]
        k = ""
        if hasattr(c,"__dict__"):
            ret[c.key] = c
    if annotation_base:
        ret = rename_annotation(ttype,ret)
    return ret
