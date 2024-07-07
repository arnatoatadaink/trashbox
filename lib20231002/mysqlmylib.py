import re,uuid
import pandas as pd
from datetime import timedelta,datetime
from urllib.parse import urlparse
import mysql.connector

# "3.2#/.61234567890"
def make_url_requests(url='mysql://root:@localhost:3306/mysql',secretsalt = ""):
    if type(url) == str:
        url = urlparse(url)
    return {
        "action_request"       : make_sql_request(cur_action    ,url),
        "selectpd_request"     : make_sql_request(cur_select_pd ,url),
        "selectdc_request"     : make_sql_request(cur_select_dic,url),
        "select_request"       : make_sql_request(cur_select    ,url),
        "insert_request"       : make_sql_request(cur_insert    ,url),
        "delete_request"       : make_sql_request(cur_delete    ,url),
        "update_request"       : make_sql_request(cur_update    ,url),
        "commitsql_request"    : make_commitsql_request(         url),
        "show_table"           : make_showtable(                 url),
        "get_columnstype"      : make_getcolumnstype(            url),
        "check_tableexist"     : make_check_tableexist(          url),
        "get_user"             : make_getuser(                   url),
        "create_user_data"     : make_create_user_data(          url,secretsalt),
        "update_user_data"     : make_update_user_data(          url,secretsalt),
        "make_get_logined_data": make_get_logined_data(          url),
        "create_login_data"    : make_create_login_data(         url),
        "update_login_data"    : make_update_login_data(         url),
    }
    
def cur_select(cur,con,sql,*args):
    try:
        if not re.search("^(SHOW|SELECT|select|show|Select|Show)",sql):
            return "type failed"
        if re.search("%s",sql):
            for arg in args:
                cur.execute(sql,arg)
                break
        else:
            cur.execute(sql)
        return cur.fetchall()
    except Exception as e:
        return "select request error : {}".format(e)

def cur_select_pd(cur,con,sql,*args):
    try:
        if not re.search("^(SHOW|SELECT|select|show|Select|Show)",sql):
            return "type failed"
        if re.search("%s",sql):
            for arg in args:
                cur.execute(sql,arg)
                break
        else:
            cur.execute(sql)
        data    = cur.fetchall()
        index   = None
        columns = cur.column_names
        return pd.DataFrame(data,index,columns)
    except Exception as e:
        return "select request error : {} : error sql : {}".format(e,sql)

def cur_select_dic(cur,con,sql,*args):
    try:
        if not re.search("^(SHOW|SELECT|select|show|Select|Show)",sql):
            return "type failed"
        if re.search("%s",sql):
            for arg in args:
                cur.execute(sql,arg)
                break
        else:
            cur.execute(sql)
        datas   = cur.fetchall()
        index   = None
        columns = cur.column_names
        ret     = []
        for data in datas:
            dic = {}
            for i in range(len(columns)):
                dic[columns[i]] = data[i]
            ret.append(dic)
        return ret
    except Exception as e:
        return "select request error : {} : error sql : {}".format(e,sql)
    
# commit actionにおいて連続insertを一つのcommitにまとめたい
# valueを*argsにまとめてそちらで展開する？
# echoの除去を実施すれば適用できる
def make_commit_action(sql_type):
    sql_type_u = sql_type.upper()
    sql_type_l = sql_type.lower()
    sql_type_h = sql_type_u[:1] + sql_type_l[1:]
    
    sql_pt = "^({}|{}|{}|{})".format(sql_type,sql_type_u,sql_type_l,sql_type_h)
                            
    def commit_action_imple(cur,con,sql,*args):
        # start transaction?
        cnt = None
        try:
            if not re.search(sql_pt,sql):
                return "type failed"
            if re.search("%s",sql):
                sqls  = [x for x in sql.split(";") if x != ""]
                vcnts = [len(re.findall("%s",sql)) for sql in sqls]
                cnt   = 1
                for arg in args:
                    vprev = 0
                    for i in range(len(sqls)):
                        cur.execute(sqls[i],arg[vprev:vprev+vcnts[i]])
                        vprev += vcnts[i]
                        cnt = cnt + 1
            else:
                sqls  = [x for x in sql.split(";") if x != ""]
                for i in range(len(sqls)):
                    cur.execute(sqls[i])
            con.commit()
            return True
        except Exception as e:
            # need rollback
            con.rollback()
            if cnt is None:
                error_print = sql_type + " request error : {} : error sql : {}".format(e,sql)
            else:
                error_print = sql_type + " request error : {} : error sql : {} : error item : {} : error val : {}".format(e,sql,cnt,arg)
            return error_print
    return commit_action_imple
cur_insert = make_commit_action("insert")
cur_delete = make_commit_action("delete")
cur_update = make_commit_action("update")

def cur_commit(cur,con,sqls_dict,show):
    # start transaction?
    try:
        last_sql = ""
        for sql_key in sqls_dict:
            cnt = None
            if re.search("%s",sql_key):
                if show:
                    print("sql : ",sql_key)
                    print("data :",sqls_dict[sql_key])
                sqls  = [x for x in sql_key.split(";") if x != ""]
                vcnts = [len(re.findall("%s",sql)) for sql in sqls]
                cnt   = 1
                for arg in sqls_dict[sql_key]:
                    vprev = 0
                    for i in range(len(sqls)):
                        last_sql = sqls[i]
                        val = arg[vprev:vprev+vcnts[i]]
                        cur.execute(last_sql,val)
                        vprev += vcnts[i]
                        cnt = cnt + 1
            else:
                if show:
                    print("sql : ",sql_key)
                sqls  = [x for x in sql_key.split(";") if x != ""]
                for i in range(len(sqls)):
                    last_sql = sqls[i]
                    cur.execute(last_sql)
        con.commit()
        return True
    except Exception as e:
        # need rollback
        con.rollback()
        if cnt is None:
            error_print = "request error : {} : error sql : {}".format(e,last_sql)
        else:
            error_print = "request error : {} : error sql : {} : error item : {} : error val : {}".format(e,last_sql,cnt,arg)
        return error_print

def cur_action(cur,conn,sql,*args):
    try:
        cur.execute(sql)
    except Exception as e:
        return "sql request error  : {} : error sql : {}".format(e,sql)
    return "successed"

def make_sql_request(cur_func,url):
    def sql_request_imple(sql,*args):
        # settingsは一旦make関数に埋め込む
        # サーバー上ではどこで管理するか？
        # トークンをキーにDictに預ける？
        conn = mysql.connector.connect(
            host     = url["db_host"],
            port     = url["db_port"],
            user     = url["db_user"],
            password = url["db_password"],
            database = url["db_database"],
        )
        if conn.is_connected():
            conn.ping(reconnect=True)
            cur = conn.cursor()
        else:
            return

        ret = cur_func(cur,conn,sql,*args)

        conn.ping(reconnect=False)
        conn.disconnect()
        return ret
    return sql_request_imple

def make_commitsql_request(url):
    def commitsql_request_imple(sqls_dict,show=False):
        # settingsは一旦make関数に埋め込む
        # サーバー上ではどこで管理するか？
        # トークンをキーにDictに預ける？
        conn = mysql.connector.connect(
            host     = url["host"],
            port     = url["port"],
            user     = url["user"],
            password = url["password"],
            database = url["database"],
        )
        if conn.is_connected():
            conn.ping(reconnect=True)
            cur = conn.cursor()
        else:
            return

        ret = cur_commit(cur,conn,sqls_dict,show)

        conn.ping(reconnect=False)
        conn.disconnect()
        return ret
    return commitsql_request_imple

def make_showtable(url):
    show_request = make_sql_request(cur_select_pd,url)
    columns = [
        "TABLE_NAME",
        "COLUMN_NAME",
        "IS_NULLABLE",
        "DATA_TYPE",
        "CHARACTER_MAXIMUM_LENGTH",
        "COLUMN_DEFAULT",
        "EXTRA",
        "COLUMN_KEY",
    ]
    columns = ",".join(columns)

    from_table = "INFORMATION_SCHEMA.COLUMNS"

    where_dict = {
        "TABLE_NAME":'%s',
        "TABLE_SCHEMA":'%s',
    }
    where = []
    for key in where_dict:
        val = where_dict[key]
        if "%s" == val:
            con = " LIKE "
        elif re.search("%",val):
            con = " LIKE "
            val = "'{}'".format(val)
        else:
            con = " = "
            val = "'{}'".format(val)
        where.append("{}{}{}".format(key,con,val))
    where = " AND ".join(where)

    order_columns = [
        "TABLE_NAME",
        "ORDINAL_POSITION"
    ]
    order_columns = ",".join(order_columns)
    sql = "select {} from {} WHERE {} ORDER BY {};".format(columns,from_table,where,order_columns)
    def show_table_imple(table_name):
        val = (table_name,url.path[1:])
        return show_request(sql,val)
    return show_table_imple

def make_getcolumnstype(url):
    show_request = make_sql_request(cur_select,url)
    columns = [
        "COLUMN_NAME",
        "DATA_TYPE",
        "CHARACTER_MAXIMUM_LENGTH",
        "EXTRA",
        "COLUMN_KEY",
    ]
    columns = ",".join(columns)

    from_table = "INFORMATION_SCHEMA.COLUMNS"

    where_dict = {
        "TABLE_NAME":'%s',
        "TABLE_SCHEMA":'%s',
    }
    where = []
    for key in where_dict:
        val = where_dict[key]
        if "%s" == val:
            con = " LIKE "
        elif re.search("%",val):
            con = " LIKE "
            val = "'{}'".format(val)
        else:
            con = " = "
            val = "'{}'".format(val)
        where.append("{}{}{}".format(key,con,val))
    where = " AND ".join(where)

    order_columns = [
        "TABLE_NAME",
        "ORDINAL_POSITION"
    ]
    order_columns = ",".join(order_columns)
    sql = "select {} from {} WHERE {} ORDER BY {};".format(columns,from_table,where,order_columns)
    def get_columnstype_imple(tablename):
        ret = {}
        val = (tablename,url["database"])
        column_datas = show_request(sql,val)
        for column in column_datas:
            ret[column[0]] = {
                "data_type"  :column[1].decode("utf-8"),
                "max_length" :column[2],
                "extra"      :column[3],
                "key"        :column[4],
            }
        return ret
    return get_columnstype_imple

def make_check_tableexist(url):
    select_request = make_sql_request(cur_select,url)
    sql = "select TABLE_NAME from INFORMATION_SCHEMA.COLUMNS WHERE ORDINAL_POSITION = 1 and TABLE_NAME = %s;"
    def check_tableexist_imple(table_name):
        return len(select_request(sql,(table_name,))) != 0
    return check_tableexist_imple

################### make commands ###################
mysql_types = {
    "CHAR":             ["size"],            # 固定長文字列(文字、数字、特殊文字)、size=0～255 文字、defsize=1
    "VARCHAR":          ["size"],            # 可変長文字列(文字、数字、特殊文字)、size=0～65535 文字
    "BINARY":           ["size"],            # Equal to CHAR(),size to specified byte
    "VARBINARY":        ["size"],            # Equal to VARCHAR(),size to specified byte
    "TINYTEXT":         "",                  # 最大 255 文字
    "TINYBLOB":         "",                  # 最大 255 bytes
    "TEXT":             ["size"],            # 最大 65,535 文字
    "BLOB":             ["size"],            # 最大 65,535 bytes
    "MEDIUMTEXT":       "",                  # 最大 16,777,215 文字
    "MEDIUMBLOB":       "",                  # 最大 16,777,215 bytes
    "LONGTEXT":         "",                  # 最大 4,294,967,295 文字
    "LONGBLOB":         "",                  # 最大 4,294,967,295 bytes
    "ENUM":             ["args"],            # 指定された値から一つの値をセット出来るリスト、指定可能な値は65535まで、リストに無い値が指定されたら空白が入る
    "SET":              ["args"],            # 指定された値から複数の値をセット出来るリスト、指定可能な値は64まで
    "BIT":              ["size"],            # range 1～64 defsize=1
    "BOOL":             "",                  # 0 or 1
    "BOOLEAN":          "",                  # Equal to BOOL
    "TINYINT":          ["size"],            #  8 bit int ,size parameter specifies the maximum display width (which is 255) 
    "SMALLINT":         ["size"],            # 16 bit int ,size parameter specifies the maximum display width (which is 255)
    "MEDIUMINT":        ["size"],            # 24 bit int ,size parameter specifies the maximum display width (which is 255)
    "INT":              ["size"],            # 32 bit int ,size parameter specifies the maximum display width (which is 255)
    "BIGINT":           ["size"],            # 64 bit int ,size parameter specifies the maximum display width (which is 255)
    "INTEGER":          ["size"],            # Equal to INT(size)
    "FLOAT":            ["size"],            # p=0～24 to FLOAT(),p=25～53 to DOUBLE()
    "DOUBLE":           ["size","decimal"],
    "DOUBLE PRECISION": ["size","decimal"],
    "DECIMAL":          ["size","decimal"],  # maxsize=65,maxd=30 defsize=10,defd=0
    "DEC":              ["size","decimal"],  # Equal to DECIMAL(size,d)
    "DATE":             "",                  # format YYYY-MM-DD range '1000-01-01' to '9999-12-31'
    "DATETIME":         ["fsp"],             # format YYYY-MM-DD hh:mm:ss range '1000-01-01 00:00:00' to '9999-12-31 23:59:59'
    "TIMESTAMP":        ["fsp"],             # format YYYY-MM-DD hh:mm:ss range '1970-01-01 00:00:01' UTC to '2038-01-09 03:14:07'
    "TIME":             ["fsp"],             # format hh:mm:ss range '-838:59:59' to '838:59:59',fsp=小数点以下精度
    "YEAR":             "",                  # format YYYY range 1901 to 2155, and 0000
}

def add_typeinfo(col_type = "",column = {}):
    add_colinfo = mysql_types.get(col_type,False)
    if not add_colinfo:
        return col_type
    values = []
    for key in add_colinfo:
        value = column.get(key)
        if not value:
            return col_type
        elif key == "args":
            if type(value) == type(""):
                values.append(str(value))
            else:
                for v in value:
                    values.append(str(v))
        else:
            values.append(str(value))
    return "{}({})".format(col_type,",".join(values))
    
def make_createtable_sql(table = {},columns = []):
    sql_c = ""
    keys  = []
    for col_name in columns:
        column = columns[col_name]
        if sql_c:
            sql_c = sql_c+", "
        col_type = column.get("type")
        col_type = add_typeinfo(col_type,column)
        sql_c = sql_c       + col_name
        sql_c = sql_c + " " + col_type
        # NOT NULL - Ensures that a column cannot have a NULL value
        if column.get("not_null",False):
            sql_c = sql_c + " NOT NULL"
        # UNIQUE - Ensures that all values in a column are different
        if column.get("unique",False):
            sql_c = sql_c + " UNIQUE"
        # PRIMARY KEY - A combination of a NOT NULL and UNIQUE. Uniquely identifies each row in a table
        if column.get("primary_key",False):
            keys.append(col_name)
        # AUTO_INCREMENT
        if column.get("auto_increment",False):
            sql_c = sql_c + " AUTO_INCREMENT"
        # FOREIGN KEY - Prevents actions that would destroy links between tables
        if column.get("foreign key",False):
            # FOREIGN KEY [index_name] (col_name, ...) REFERENCES tbl_name (col_name, ...)
            pass
#         # CHECK - Ensures that the values in a column satisfies a specific condition
#         if column.get("CHECK",False):
#             pass
        # DEFAULT - Sets a default value for a column if no value is specified
        if column.get("DEFAULT",False):
            pass
        # CREATE INDEX - Used to create and retrieve data from the database very quickly
        if column.get("INDEX",column.get("CREATE INDEX",False)):
            index = column.get("INDEX",column.get("CREATE INDEX",False))
            pass
    if len(keys) > 0:
        sql_c += ", PRIMARY KEY( {} )".format(",".join(keys))
    return "CREATE TABLE {} ( {} )".format(table["name"],sql_c)
# make_createtable_sql(
#     {
#         "name":"label_settings"
#         # constraint name : { type:constraint,... }
#     },{
#         "label":{
#             "type":"VARCHAR",
#             "size":32,
#             "not_null":True,"primary_key":True,
#         },
#         "val1":{
#             "type":"VARCHAR",
#             "size":32,
#         },
#         "val2":{
#             "type":"VARCHAR",
#             "size":32,
#         }
#     },
# )

def make_insert_sqls(table_name:str,get_columnstype,datadict_list:[]):
    ret = []
    columns_type = get_columnstype(table_name)
    for datadict in datadict_list:
        columns = []
        values  = []
        for key in datadict:
            if columns_type.get(key) is None:
                print("columns key error table : {} hasn't column : {} ".format(table_name,key))
                return []
            column_type = columns_type[key]
            value       = datadict[key]
            if value is None:
                continue
            elif value == "%s":
                pass
            # # TODO：VALUES (SELECT ～ FROM ～ WHERE ～)
            # elif type(value) == dict:
            #     inner_table  = value.pop("table_name")
            #     inner_insert = make_insert_sqls(inner_table,get_columnstype,[value])[0]
            #     value = "( {} )".format(inner_insert)
            elif column_type["max_length"] is not None \
                    or column_type["data_type"] in ["date","datetime","timestamp","time"]:
                value = "'{}'".format(value)
            elif type(value) != str:
                value = str(value)
            columns.append(key)
            values.append(value)
        if len(columns) > 0:
            columns = ",".join(columns)
            values  = ",".join(values)
            insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(table_name,columns,values)
            ret.append(insert_sql)
    return ret
    
def make_update_sqls(table_name:str,get_columnstype,datadict_list:[]):
    ret = []
    columns_type = get_columnstype(table_name)
    for datadict in datadict_list:
        values = []
        wheres = []
        for key in datadict:
            if columns_type.get(key) is None:
                print("columns key error table : {} hasn't column : {} ".format(table_name,key))
                return []
            column_type = columns_type[key]
            value       = datadict[key]
            if value is None:
                continue
            elif value == "%s":
                pass
            elif column_type["max_length"] is not None:
                value = "'{}'".format(value)
            elif type(value) != str:
                value = str(value)
                
            target = values if column_type["key"] == "" else wheres
            target.append(" = ".join([key,value]))
            
        if len(values) > 0:
            values     = ",".join(values)
            wheres     = " AND ".join(wheres)
            update_sql = "UPDATE {} SET {}" if len(wheres) == 0 else "UPDATE {} SET {} WHERE {}"
            update_sql = update_sql.format(table_name,values,wheres)
                
            ret.append(update_sql)
    return ret

def make_adddatatable_sql(length):
    # TINYBLOB   最大 255 bytes
    if length <= 2**8:
        data_type = "TINYBLOB"
    # BLOB       最大 65,535 bytes
    elif length <= 2**16:
        data_type = "BLOB"
    # MEDIUMBLOB 最大 16,777,215 bytes
    elif length <= 2**24:
        data_type = "MEDIUMBLOB"
    # LONGBLOB   最大 4,294,967,295 bytes
    elif length <= 2**32:
        data_type = "LONGBLOB"
    else:
        assert False , "add data size error"
    
    
    
    table_dict = {
        "name":"add_data{}".format(length)
    }
    columns_dict = {
        # class_settings_id:ID
        "data_id":{
            "type":"INT",
            "not_null":True,"primary_key":True,
            "auto_increment":True
        },
        # adddata_out_func:追加データ出力時の変換関数
        "data":{
            "type":data_type,
            "size":length,
        }
    }
    return make_createtable_sql(table_dict,columns_dict)

################ login control ################
def make_getuser(url):
    usertable               = 'Oay'
    usertable_name          = 'wHa' # '$2b$12$3P7vwNuQTDguxGFr8ap5VeMj53OIugSAzahPn1YozzKt2lwHkNwHa'
    usertable_fullname      = 'Iog'
    usertable_id            = 'RBq' # '$2b$12$V.LLzUhc8g93EpsN9eKMKelvz9fuWr8RxP1Ue4AbotTXvbIEYtRBq'
    usertable_hasedpassword = 'axg'
    usertable_salt          = 'K96' # '$2b$12$oeFjCWTQaZQhgX/pJl55MeT2yXCLAOayYUsJziGuqMAVjWOBbhK96'
    usertable_address       = 'j9W' # '$2b$12$OoGbheuBhzsKkz/hKRurRuakJDSLCHcUtevncWWdjU4HnJcwxCj9W'
    usertable_createdate    = 'PlC' # '$2b$12$LRYIAQyxJXm4J1sFCBXen.opoBgi4wwauTetR2Yc0FRYdO0TehPlC'
    usertable_updatedate    = 'XYi' # '$2b$12$tt9XziYhGcIdUWulJwuFwusPbzXnN2qRAJfsh0J91mde298AaFXYi'
    usertable_expired       = 'Ru2' # '$2b$12$YAR9tmaA3j8zXDBV8lmjUO25ZdQ8bQ8fY.OqTGc4m9nw4O0C1ARu2'
    usertable_flags         = 'GE2' # '$2b$12$hyJW13/Q.YLYJYS9V4R9ROUD9jVENFuaYmtifFTlpfxbwKXp8mGE2'
    select_request = make_sql_request(cur_select_dic,url)
    def get_user(username:str):
        sql = f"SELECT {usertable_name}          as username"+\
              f" ,     {usertable_fullname}      as full_name"+\
              f" ,     {usertable_id}            as id"+\
              f" ,     {usertable_salt}          as salt"+\
              f" ,     {usertable_hasedpassword} as hashed_password"+\
              f" ,     {usertable_address}       as email"+\
              f" ,     {usertable_createdate}    as create_date"+\
              f" ,     {usertable_updatedate}    as update_date"+\
              f" ,     {usertable_expired}       as expired"+\
              f" ,     {usertable_flags}         as disabled"+\
              f" FROM  {usertable} "+\
              f"WHERE {usertable_name} = %s"
        val = (username,)
        ret = select_request(sql,val)
        if type(ret) == list and len(ret) > 0:
            return ret[0]
        return ret
    return get_user
    
def make_create_user_data(url,secretsalt):
    usertable               = 'Oay'
    usertable_name          = 'wHa' # '$2b$12$3P7vwNuQTDguxGFr8ap5VeMj53OIugSAzahPn1YozzKt2lwHkNwHa'
    usertable_fullname      = 'Iog'
    usertable_id            = 'RBq' # '$2b$12$V.LLzUhc8g93EpsN9eKMKelvz9fuWr8RxP1Ue4AbotTXvbIEYtRBq'
    usertable_hasedpassword = 'axg'
    usertable_salt          = 'K96' # '$2b$12$oeFjCWTQaZQhgX/pJl55MeT2yXCLAOayYUsJziGuqMAVjWOBbhK96'
    usertable_address       = 'j9W' # '$2b$12$OoGbheuBhzsKkz/hKRurRuakJDSLCHcUtevncWWdjU4HnJcwxCj9W'
    usertable_createdate    = 'PlC' # '$2b$12$LRYIAQyxJXm4J1sFCBXen.opoBgi4wwauTetR2Yc0FRYdO0TehPlC'
    usertable_updatedate    = 'XYi' # '$2b$12$tt9XziYhGcIdUWulJwuFwusPbzXnN2qRAJfsh0J91mde298AaFXYi'
    usertable_expired       = 'Ru2' # '$2b$12$YAR9tmaA3j8zXDBV8lmjUO25ZdQ8bQ8fY.OqTGc4m9nw4O0C1ARu2'
    usertable_flags         = 'GE2' # '$2b$12$hyJW13/Q.YLYJYS9V4R9ROUD9jVENFuaYmtifFTlpfxbwKXp8mGE2'#     import uuid
    insert_request  = make_sql_request(cur_insert,url)
    get_columnstype = make_getcolumnstype(        url)
    def create_user_data(username,fullname,userpassword,address):
        utcnow = datetime.utcnow()
        salt = str(uuid.uuid4())
        table_name = f"{usertable}"
        user_datas = [
            {
                usertable_name          : username,
                usertable_fullname      : fullname,
                usertable_hasedpassword : get_password_hash(userpassword+salt+secretsalt),
                usertable_salt          : salt,
                usertable_address       : address,
                usertable_createdate    : str(utcnow)[:-7],
                usertable_updatedate    : str(utcnow)[:-7],
                usertable_expired       : str(utcnow+datetime.timedelta(days=7))[:-7],
                usertable_flags         : True,
            }
        ]
        insert_sqls = make_insert_sqls(table_name,get_columnstype,user_datas)
        for insert_sql in insert_sqls:
            insert_request(insert_sql)
        pass
    return create_user_data

def make_update_user_data(url,secretsalt):
    usertable               = 'Oay'
    usertable_name          = 'wHa' # '$2b$12$3P7vwNuQTDguxGFr8ap5VeMj53OIugSAzahPn1YozzKt2lwHkNwHa'
    usertable_fullname      = 'Iog'
    usertable_id            = 'RBq' # '$2b$12$V.LLzUhc8g93EpsN9eKMKelvz9fuWr8RxP1Ue4AbotTXvbIEYtRBq'
    usertable_hasedpassword = 'axg'
    usertable_salt          = 'K96' # '$2b$12$oeFjCWTQaZQhgX/pJl55MeT2yXCLAOayYUsJziGuqMAVjWOBbhK96'
    usertable_address       = 'j9W' # '$2b$12$OoGbheuBhzsKkz/hKRurRuakJDSLCHcUtevncWWdjU4HnJcwxCj9W'
    usertable_createdate    = 'PlC' # '$2b$12$LRYIAQyxJXm4J1sFCBXen.opoBgi4wwauTetR2Yc0FRYdO0TehPlC'
    usertable_updatedate    = 'XYi' # '$2b$12$tt9XziYhGcIdUWulJwuFwusPbzXnN2qRAJfsh0J91mde298AaFXYi'
    usertable_expired       = 'Ru2' # '$2b$12$YAR9tmaA3j8zXDBV8lmjUO25ZdQ8bQ8fY.OqTGc4m9nw4O0C1ARu2'
    usertable_flags         = 'GE2' # '$2b$12$hyJW13/Q.YLYJYS9V4R9ROUD9jVENFuaYmtifFTlpfxbwKXp8mGE2'#     import uuid
    update_request  = make_sql_request(cur_update,url)
    get_columnstype = make_getcolumnstype(        url)
    def update_user_data(userid,username=None,fullname=None,userpassword=None,address=None):
        utcnow = datetime.utcnow()
        table_name = f"{usertable}"
        changedatas = {}
        if username is not None:
            changedatas[usertable_name] = username
        if fullname is not None:
            changedatas[usertable_fullname] = fullname
        if userpassword is not None:
            salt = str(uuid.uuid4())
            changedatas[usertable_hasedpassword] = get_password_hash(userpassword+salt+secretsalt)
            changedatas[usertable_salt         ] = salt
        if address is not None:
            changedatas[usertable_address] = address
        
        user_datas = [
            {
                usertable_id            : userid,
                **changedatas,
                usertable_updatedate    : str(utcnow)[:-7],
                usertable_expired       : str(utcnow+datetime.timedelta(days=7))[:-7],
                usertable_flags         : True,
            }
        ]
        update_sqls = make_update_sqls(table_name,get_columnstype,user_datas)
        for update_sql in update_sqls:
            update_request(update_sql)
        pass
    return update_user_data

def make_get_logined_data(url):
    loginedtable            = 'IdU'
    loginedtable_id         = 'LLz'
    loginedtable_ip         = 'bhe'
    loginedtable_iptype     = 'Jfs'
    loginedtable_date       = 'aA3'
    select_request = make_sql_request(cur_select_dic,url)
    def get_logined_data(name:str):
        sql = f"SELECT {loginedtable_id}      as id"+\
              f" ,     {loginedtable_ip}      as ip"+\
              f" ,     {loginedtable_iptype}  as iptype"+\
              f" ,     {loginedtable_date}    as date"+\
              f" FROM  {loginedtable} "+\
              f"WHERE {loginedtable_id} = %s"
        val = (name,)
        ret = select_request(sql,val)
        if type(ret) == list and len(ret) > 0:
            return ret[0]
        return ret
    return get_logined_data

def make_create_login_data(url):
    loginedtable            = 'IdU'
    loginedtable_id         = 'LLz'
    loginedtable_ip         = 'bhe'
    loginedtable_iptype     = 'Jfs'
    loginedtable_date       = 'aA3'
    insert_request  = make_sql_request(cur_insert,url)
    get_columnstype = make_getcolumnstype(        url)
    def create_login_data(userid,ip,iptype):
        utcnow = datetime.utcnow()
        table_name = f"{loginedtable}"
        login_datas = [
            {
                loginedtable_id      : userid,
                loginedtable_ip      : ip,
                loginedtable_iptype  : iptype,
                loginedtable_date    : str(utcnow)[:-7],
            }
        ]
        insert_sqls = make_insert_sqls(table_name,get_columnstype,login_datas)
        for insert_sql in insert_sqls:
            insert_request(insert_sql)
        pass
    return create_login_data

def make_update_login_data(url):
    loginedtable            = 'IdU'
    loginedtable_id         = 'LLz'
    loginedtable_ip         = 'bhe'
    loginedtable_iptype     = 'Jfs'
    loginedtable_date       = 'aA3'
    update_request  = make_sql_request(cur_update,url)
    get_columnstype = make_getcolumnstype(        url)
    def update_login_data(userid,ip,iptype):
        utcnow = datetime.utcnow()
        table_name = f"{loginedtable}"
        login_datas = [
            {
                loginedtable_id      : userid,
                loginedtable_ip      : ip,
                # loginedtable_iptype  : iptype,
                loginedtable_date    : str(utcnow)[:-7],
            }
        ]
        update_sqls = make_update_sqls(table_name,get_columnstype,login_datas)
        for update_sql in update_sqls:
            update_request(update_sql)
    return update_login_data
    