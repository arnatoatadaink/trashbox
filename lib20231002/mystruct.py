from struct import pack,unpack
import math,re

def conv_types(format_str):
    types = []
    sizes = []
    count = ""
    for t in format_str:
        if t in "0123456789":
            count = count + t
        else:
            if count != "":
                if t != "s":
                    for i in range(int(count)):
                        types.append(t)
                        sizes.append(0)
                else:
                    types.append(t)
                    sizes.append(int(count))
                count = "" 
            else:
                types.append(t)
                sizes.append(0)
    if len(types) > 0:
        if re.match("[xcbB?hHiIlLqQnNefdspP]",types[0]) is None:
            types = types[1:]
    return (types,sizes)

def byte2printlength(byte):
    return math.floor(math.log(2**(byte*8),10))+1
typedetail_dict = {
#    フォーマット  C の型               Python の型        標準のサイズ        注釈        
#     x            パディングバイト     値なし             
    "x":{"default":None ,"casttype":"None" ,"type":None,"length":None,"inneronly":True},
#     c            char                 長さ 1 のバイト列  1        
    "c":{"default":""   ,"casttype":"None" ,"type":"text","length":1,"inneronly":False},
#     b            signed char          整数               1                   (1), (2)
    "b":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(1)+1,"inneronly":False},
#     B            unsigned char        整数               1                   (2)
    "B":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(1),"inneronly":False},
#     ?            _Bool                真偽値型(bool)     1                   (1)
    "?":{"default":False,"casttype":"bool","type":"bool","length":1,"inneronly":False},
#     h            short                整数               2                   (2)
    "h":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(2)+1,"inneronly":False},
#     H            unsigned short       整数               2                   (2)
    "H":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(2),"inneronly":False},
#     i            int                  整数               4                   (2)
    "i":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
#     I            unsigned int         整数               4                   (2)
    "I":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
#     l            long                 整数               4                   (2)
    "l":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
#     L            unsigned long        整数               4                   (2)
    "L":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
#     q            long long            整数               8                   (2)
    "q":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(8)+1,"inneronly":False},
#     Q            unsigned long long   整数               8                   (2)
    "Q":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(8),"inneronly":False},
#     n            ssize_t              整数                                   (3)
    "n":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
#     N            size_t               整数                                   (3)
    "N":{"default":0    ,"casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
#     e            (6)                  浮動小数点数       2                   (4)
    "e":{"default":0    ,"casttype":"float","type":"number","length":5,"inneronly":False},
#     f            float                浮動小数点数       4                   (4)
    "f":{"default":0    ,"casttype":"float","type":"number","length":9,"inneronly":False},
#     d            double               浮動小数点数       8                   (4)
    "d":{"default":0    ,"casttype":"float","type":"number","length":18,"inneronly":False},
#     s            char[]               bytes                                  
    "s":{"default":""   ,"casttype":"None" ,"type":"text","length":None,"inneronly":False},
#     p            char[]               bytes                                  
    "p":{"default":0    ,"casttype":"None" ,"type":"number","length":None,"inneronly":False},
#     P            void*                整数                                   (5)
    "P":{"default":0    ,"casttype":"None" ,"type":"number","length":None,"inneronly":True},
}

def typedetail(t,s):
    typeinfo = {
        "default"  :typedetail_dict[t]["default"],
        "type"     :typedetail_dict[t]["type"],
        "cast"     :typedetail_dict[t]["casttype"],
        "max_print":typedetail_dict[t]["length"] or s,
    }
    return typeinfo
    
castfuncs = {
    "int":int,
    "float":float,
    "None":None,
    "bool":(lambda x:x=="true"),
}
def cast_func(val,cast_key):
    return castfuncs[cast_key](val)

# textの処置はencode+pack/decode+unpackで実施する
# 入力項目中、桁溢れが発生した場合、桁が落ちる
def encode_format(format_str,*args):
    ret   = []
    types,sizes = conv_types(format_str)
    # 入力数が異なるのは明らかなエラー
    assert len(types) == len(args), \
        "format error need : {} , input : {}".format(format_str,args)
    for i in range(len(types)):
        val = args[i]
        if types[i] == "s":
            val = val.encode("utf-8")
            # 桁溢れはassertで出力すべき想定外のエラーか？
            # デコード時に末尾不明のエラーが発生しうるため
            # 警告ではなく、エラーにしたい
            assert len(val) <= sizes[i], \
                "data size {} over {} → {} ".format(sizes[i],args[i],val)
        ret.append(val)
    ret = pack(format_str,*ret)
    return ret

def decode_format(format_str,packed):
    ret         = []
    types,sizes = conv_types(format_str)
    unpacked    = unpack(format_str,packed)
    for i in range(len(types)):
        val = unpacked[i]
        if types[i] == "s":
            val = val.decode("utf-8").split("\x00")[0]
        ret.append(val)
    return ret

if __name__ == '__main__':
    # text
    test       = ["teあst",1,"teいst"]
    format_str = "20sh20s"

    temp = encode_format(format_str,*test)
    ret  = decode_format(format_str,temp)

    if test != ret or test == temp:
        print("error")
        print("input:{}".format(test))
        print("into db:{}".format(temp))
        print("output:{}".format(ret))