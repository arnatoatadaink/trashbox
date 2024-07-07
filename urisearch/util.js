//////////////// struct util ////////////////
// select list values
const datatypes = [
    "None",
    "char","signed char","unsigned char",
    "_Bool",
    "short","unsigned short",
    "int","unsigned int",
    "long","unsigned long",
    "long long","unsigned long long",
    "ssize_t","size_t",
    "half float","float","double",
    "string","string number",
    "void*"
]

function conv_types_detail(format_str,names_str){
    const ret = [];
    const names = names_str.split(",");
    const [types,sizes] = conv_types(format_str);
    if( names.length  !== types.length 
            || names.length !== sizes.length ){
        return ret;
    }
    for( let i = -1; ++i < names.length; ){
        const detail = typedetail(types[i],sizes[i]);
        detail["name"] = names[i];
        ret.push(detail);
    }
    return ret;
}

function conv_types(format_str){
    let   count = "";
    const types = []
    const sizes = []
    const keys  = Object.keys(format_str);
    for( let i = -1; ++i < format_str.length; ){
        const key = keys[i];
        const t   = format_str[key];
        if( !isNaN(t) ){
            count = count + t
        }else if( count !== "" ){
            const count_int = parseInt(count);
            if( t !== "s" ){
                for( let i = -1; ++i < count_int; ){
                    types.push(t)
                    sizes.push(0)
                }
            }else{
                types.push(t)
                sizes.push(count_int)
            }
            count = "" 
        }else{
            types.push(t)
            sizes.push(0)
        }
    }
    if( types.length > 0 ){
        if( "xcbB?hHiIlLqQnNefdspP".search(types[0]) === -1 ){
            types.shift()
        }
    }
    return [types,sizes]
}

function byte2printlength(byte){
    return Math.floor(Math.log(2**(byte*8),10))+1
}
const True = true
const False = false
const None  = undefined
const typedetail_dict = {
//   フォーマット  C の型               Python の型        標準のサイズ        注釈        
//    x            パディングバイト     値なし             
    "x":{"default":None ,"datatype":"None","casttype":"None" ,"type":None,"length":None,"inneronly":True},
//    c            char                 長さ 1 のバイト列  1        
    "c":{"default":""   ,"datatype":"char","casttype":"None" ,"type":"text","length":1,"inneronly":False},
//    b            signed char          整数               1                   (1), (2)
    "b":{"default":0    ,"datatype":"signed char","casttype":"int"  ,"type":"number","length":byte2printlength(1)+1,"inneronly":False},
//    B            unsigned char        整数               1                   (2)
    "B":{"default":0    ,"datatype":"unsigned char","casttype":"int"  ,"type":"number","length":byte2printlength(1),"inneronly":False},
//    ?            _Bool                真偽値型(bool)     1                   (1)
    "?":{"default":False,"datatype":"_Bool","casttype":"bool","type":"bool","length":1,"inneronly":False},
//    h            short                整数               2                   (2)
    "h":{"default":0    ,"datatype":"short","casttype":"int"  ,"type":"number","length":byte2printlength(2)+1,"inneronly":False},
//    H            unsigned short       整数               2                   (2)
    "H":{"default":0    ,"datatype":"unsigned short","casttype":"int"  ,"type":"number","length":byte2printlength(2),"inneronly":False},
//    i            int                  整数               4                   (2)
    "i":{"default":0    ,"datatype":"int","casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
//    I            unsigned int         整数               4                   (2)
    "I":{"default":0    ,"datatype":"unsigned int","casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
//    l            long                 整数               4                   (2)
    "l":{"default":0    ,"datatype":"long","casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
//    L            unsigned long        整数               4                   (2)
    "L":{"default":0    ,"datatype":"unsigned long","casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
//    q            long long            整数               8                   (2)
    "q":{"default":0    ,"datatype":"long long","casttype":"int"  ,"type":"number","length":byte2printlength(8)+1,"inneronly":False},
//    Q            unsigned long long   整数               8                   (2)
    "Q":{"default":0    ,"datatype":"unsigned long long","casttype":"int"  ,"type":"number","length":byte2printlength(8),"inneronly":False},
//    n            ssize_t              整数                                   (3)
    "n":{"default":0    ,"datatype":"ssize_t","casttype":"int"  ,"type":"number","length":byte2printlength(4)+1,"inneronly":False},
//    N            size_t               整数                                   (3)
    "N":{"default":0    ,"datatype":"size_t","casttype":"int"  ,"type":"number","length":byte2printlength(4),"inneronly":False},
//    e            (6)                  浮動小数点数       2                   (4)
    "e":{"default":0    ,"datatype":"half float","casttype":"float","type":"number","length":5,"inneronly":False},
//    f            float                浮動小数点数       4                   (4)
    "f":{"default":0    ,"datatype":"float","casttype":"float","type":"number","length":9,"inneronly":False},
//    d            double               浮動小数点数       8                   (4)
    "d":{"default":0    ,"datatype":"double","casttype":"float","type":"number","length":18,"inneronly":False},
//    s            char[]               bytes                                  
    "s":{"default":""   ,"datatype":"string","casttype":"None" ,"type":"text","length":None,"inneronly":False},
//    p            char[]               bytes                                  
    "p":{"default":0    ,"datatype":"string number","casttype":"None" ,"type":"number","length":None,"inneronly":False},
//    P            void*                整数                                   (5)
    "P":{"default":0    ,"datatype":"void*","casttype":"None" ,"type":"number","length":None,"inneronly":True},
}

function typedetail(t,s){
    return {
        "default"  :typedetail_dict[t]["default"]    ,
        "type"     :typedetail_dict[t]["type"]       ,
        "datatype" :typedetail_dict[t]["datatype"]   ,
        "cast"     :typedetail_dict[t]["casttype"]   ,
        "max_print":typedetail_dict[t]["length"] || s,
    }
}
    
const castfuncs = {
    "int":parseInt,
    "float":parseFloat,
    "None":()=>undefined,
    "bool":(x)=>{return x==="true"},
}
function cast_func(val,cast_key){
    return castfuncs[cast_key](val)
}

// TODO how to use pack/unpack of javascript
// // textの処置はencode+pack/decode+unpackで実施する
// // 入力項目中、桁溢れが発生した場合、桁が落ちる
// function encode_format(format_str,...args){
//     const ret   = []
//     const [types,sizes] = conv_types(format_str)
//     // 入力数が異なるのは明らかなエラー
//     if( types.length != args.length ){
//         // console.log("format error need : {} , input : {}".format(format_str,args))
//     }
//     for( let i = -1; ++i < types.length; ){
//         let val = args[i]
//         if( types[i] == "s" ){
//             val = val.encode("utf-8")
//             
//             // 桁溢れはassertで出力すべき想定外のエラーか？
//             // デコード時に末尾不明のエラーが発生しうるため
//             // 警告ではなく、エラーにしたい
//             if( val.length > sizes[i] ){
//                 // console.log("data size {} over {} → {} ".format(sizes[i],args[i],val))
//             }
//         }
//         ret.push(val)
//     }
//     // ret = pack(format_str,*ret)
//     return ret
// }
// 
// function decode_format(format_str,packed){
//     const ret           = []
//     const [types,sizes] = conv_types(format_str)
//     // unpacked    = unpack(format_str,packed)
//     for( let i =-1; ++i < types.length; ){
//         let val = unpacked[i]
//         if( types[i] == "s" ){
//             val = val.decode("utf-8").split("\x00")[0]
//         }
//         ret.append(val)
//     }
//     return ret
// }

//////////////// uuid ////////////////
function generate_uuidv4() {
    // https://github.com/GoogleChrome/chrome-platform-analytics/blob/master/src/internal/identifier.js
    // const FORMAT: string = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx";
    let chars = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".split("");
    for (let i = 0, len = chars.length; i < len; i++) {
        switch (chars[i]) {
            case "x":
                chars[i] = Math.floor(Math.random() * 16).toString(16);
                break;
            case "y":
                chars[i] = (Math.floor(Math.random() * 4) + 8).toString(16);
                break;
            default:
                // pass
        }
    }
    return chars.join("");
}

//////////////// events util ////////////////
// export const event_keys = ["click","input","change","blur","focus"];
const event_keys = ["onClick","onInput","onChange","onBlur","onFocus","onFocusOut"];
const get_funcs = (props)=>choice_items(props,event_keys)

//////////////// type util ////////////////
function equal_type(obj1,obj2){ return typeof(obj1) === typeof(obj2); }
function is_string(obj){ return (typeof (obj) === "string" || obj instanceof String); }
// export function is_array(obj) { return Object.prototype.toString.call(obj) === '[object Array]'; }
function is_array(obj) { return Array.isArray(obj); }
function is_object(obj) { return typeof obj === 'object' && obj !== null && !is_array(obj); }
function is_boolean(obj) { return typeof obj === 'boolean'; }
function check_type(value){
    if( is_array(value) ){
        return "array";
    }else if( is_object(value) ){
        return "object";
    }else if( is_boolean(value) ){
        return "bool";
    }else if( !isNaN(value) && value !== "" ){
        return "numeric";
    }else if( is_string(value) ){
        if( value.match("\r|\n") ){
            return "strings";
        }else{
            return "string";
        }
    }else if( !value ){
        return "error";
    }
    return "other";
}

//////////////// array util ////////////////
function array_convert(arr,func){ for(let i=-1;++i<arr.length;){arr[i] = func(arr[i],i)} }
function array_make(arr,func){ const ret=[]; for(let i=-1;++i<arr.length;){ret.push(func(arr[i],i))}return ret; }
function array_action(arr,func){ for(let i=-1;++i<arr.length;){func(arr[i],i)}}
function array_sum(arr,func){ let ret=0;for(let i=-1;++i<arr.length;){ret+=func(arr[i],i)}return ret;}
function array_sum_bool(arr,func){ let ret=0;for(let i=-1;++i<arr.length;){ret+=!!func(arr[i],i)}return ret;}
//////////////// num util ////////////////
function max(a,b){ return a>b?a:b; }
function min(a,b){ return a<b?a:b; }
function add(a,b){ return a*1+b*1; }
function range2par(val,min,max){ return (val-min)/(max-min); }
function limit(a,b,c){ return max(c,min(b,a)) }
function check_limit(a,b,c){ return a>=b?a<=c:false; }

//////////////// day util ////////////////
function get_utcday(){   return new Date().toUTCString().substr(0,16); }
function get_localday(){ return new Date().toString(   ).substr(0,16); }

//////////////// str util ////////////////
function num2par(val,round){
    if( !round ){ round = 2; }
    return ( Math.round(val*10**round)/10**(round-2) ) + " %";
}
function px2int(strval){ return strval.slice(0,-2)*1; }
function get_inside(strval,start,end){
    const index_s = strval.indexOf(start);
    const index_e = strval.lastIndexOf(end);
    return strval.slice(index_s+1,index_e-strval.length);
}
function numstr2space(numstr){
    const digits     = Math.ceil(Math.log10(numstr*1+1e-10));
    const addsuf     = Math.floor(digits/2);
    const half_space = digits%2;
    let suffix     = "";
    for( let i = -1; ++i < addsuf; ){
        suffix += "　";
    }
    if( half_space ){
        suffix += " ";
    }
    suffix += "　";
    return suffix;
}

function search_and_eject(array,matches){
    for( let i = array.length; --i >= 0; ){
        for( let j = -1; ++j < matches.length; ){
            if( array[i].match(matches[j]) ){
                array.splice(i, 1);
                break;
            }
        }
    }
    return array;
}

function array_trim(array){
    for( let i = -1; ++i < array.length; ){
        array[i] = array[i].trim();
    }
    return array;
}

function get_splitarray(detail,sep,quot){
    // 純粋な数値か区切り文字を含む文字列を考慮して分割
    // const setkey= quot+sep+quot
    //             +"|(?=[0-9])"+sep+quot
    //             +"|"+quot+sep+"(?=[0-9])"
    //             +"|(?=[0-9])"+sep+"(?=[0-9])";
    const setkey = "([0-9.]+|"+quot+"[^"+quot+"]+"+quot+")"+sep;
    let   array = detail.split(RegExp(setkey));
    array = search_and_eject(array,["^$"]);
    return array;
}

//////////////// cookie util ////////////////
// function cookie2dict(cookie){
//     const cookie_array = cookie.split("; ");
//     const ret = {}
//     for( let i = -1; ++i < cookie_array.length; ){
//         const cookie_pair = cookie_array[i].split("=");
//         ret[cookie_pair[0]] = cookie_pair[1];
//     }
//     return ret;
// }
// function dict2cookie(object){
//     const ret    = "";
//     const keys   = Object.keys(object);
//     let   prefix = "";
//     for( let i = -1; ++i < keys.length; ){
//         const key = keys[i];
//         ret   += prefix+key+"="+object[key];
//         prefix = "; ";
//     }
//     return ret;
// }
// 
// export function cookie_keys(){
//     return Object.keys(cookie2dict(document.cookie));
// }
// 
// export function has_cookie(key){
//     return cookie2dict(document.cookie).hasOwnProperty(key);
// }
// 
// export function get_cookie(key){
//     return cookie2dict(document.cookie)[key];
// }
// 
// export function set_cookie(key,value){
//     const cookie_object = cookie2dict(document.cookie);
//     cookie_object[key] = value;
//     const cookie_string = dict2cookie(cookie_object);
//     document.cookie = cookie_string;
// }

function remove_cookie(key){
    // const cookie_object = cookie2dict(document.cookie);
    // delete cookie_object[key];
    // const cookie_string = dict2cookie(cookie_object);
    // document.cookie = cookie_string;
    document.cookie = key+"=; max-age=0;";
}

/////////////////////////////////////////////////
function request_closure(request,func){
    return function(){ func(request);}
}

//////////////// element util ////////////////
function bubbling_class(target,classkeys){
    if( is_string(classkeys) ){
        classkeys = [classkeys];
    }
    while( target.parentElement ){
        for( let i = -1; ++i < classkeys.length; ){
            if( target.classList.contains(classkeys[i]) ){
                return target;
            }
        }
        target = target.parentElement;
    }
    return undefined;
}

//////////////// get css font size ////////////////
// ref:https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript
function getTextWidth(text, font) {
  // re-use canvas object for better performance
  const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
  const context = canvas.getContext("2d");
  context.font = font;
  const metrics = context.measureText(text);
  return metrics.width;
}

function getCssStyle(element, prop) {
    return window.getComputedStyle(element, null).getPropertyValue(prop);
}

function getCanvasFontSize(el = document.body) {
  const fontWeight = getCssStyle(el, 'font-weight') || 'normal';
  const fontSize = getCssStyle(el, 'font-size') || '16px';
  const fontFamily = getCssStyle(el, 'font-family') || 'Times New Roman';
  
  // return `${fontWeight} ${fontSize} ${fontFamily}`;
  return [fontWeight,fontSize,fontFamily].join(" ");
}

//////////////// random util ////////////////
// ref:https://qiita.com/psn/items/d7ac5bdb5b5633bae165
function generateUuid() {
    // https://github.com/GoogleChrome/chrome-platform-analytics/blob/master/src/internal/identifier.js
    // const FORMAT: string = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx";
    let chars = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".split("");
    for (let i = 0, len = chars.length; i < len; i++) {
        switch (chars[i]) {
            case "x":
                chars[i] = Math.floor(Math.random() * 16).toString(16);
                break;
            case "y":
                chars[i] = (Math.floor(Math.random() * 4) + 8).toString(16);
                break;
            default:
                // pass
        }
    }
    return chars.join("");
}

//////////////// dict util ////////////////
function dict_make(dict,func){
    const ret  = {};
    const keys = Object.keys(dict);
    for( let i = -1; ++i < keys.length; ){
        const key = keys[i];
        const [new_key,data] = func(key,dict[key]);
        ret[new_key] = data
    }
    return ret;
}

function set_default(dict,key,def){
    dict[key] = key in dict?dict[key]:def;
    return dict[key];
}
function safe_get(dict,key){
    if( !dict ){
        return undefined;
    }else{
        const keys = is_array(key)?key:[key];
        for( let i = -1; ++i < keys.length; ){
            const key = keys[i];
            if( !(key in dict) ){ continue }
            return dict[key];
        }
    }
}
function choice_items(dict,keys){
    const ret = {};
    for( let i = -1; ++i < keys.length; ){
        if( !dict[keys[i]] ){
            continue;
        }
        ret[keys[i]] = dict[keys[i]];
    }
    return ret;
}
function choice_relabel(dict,label_dict){
    const keys = Object.keys(label_dict);
    const ret  = {};
    for( let i = -1; ++i < keys.length; ){
        const label = keys[i];
        const value = safe_get(dict,label_dict[label])
        if( !value ){ continue; }
        ret[label] = value;
    }
    return ret;
}

// keyのsyntax sugar
// keysのうち先頭から取得に挑戦して
// 取れたものを返す
function get_dictvalue(dict,keys,def){
    if( !is_array(keys) ){
        keys = [keys];
    }
    for( let i = -1;++i < keys.length; ){
        if( keys[i] in dict ){
            return dict[keys[i]];
        }
    }
    return def;
}

function remove_dictkeys(dict){
    const keys = Object.keys(dict);
    for( let i = -1;++i<keys.length; ){
        const key = keys[i];
        if( is_string(dict[key]) ){
            if( dict[key].length === 0 ){
                delete dict[key];
            }
        }else if( is_array(dict[key]) ){
            if( dict[key].length === 0 ){
                delete dict[key];
            }
        }else if( is_object(dict[key]) ){
            remove_dictkeys(dict[key]);
            if( Object.keys(dict[key]).length === 0 ){
                delete dict[key];
            }
        }
    }
}

function copy_dict(dict_base){
    let ret = null;
    if( dict_base instanceof Array ){
        ret = [];
    }else if( dict_base instanceof Object ){
        ret = {}
    }
    const keys = Object.keys(dict_base);
    for( let i = -1;++i<keys.length; ){
        const key = keys[i];
        if( !isNaN(dict_base[key]) && dict_base[key] !== "" ){
            ret[key] = dict_base[key];
        }else if( is_string(dict_base[key]) ){
            ret[key] = dict_base[key];
        }else if( is_object(dict_base[key])
               || is_array(dict_base[key]) ){
            ret[key] = copy_dict(dict_base[key]);
        }else{
            // その他のコレクションクラス、Freeze系？
            ret[key] = dict_base[key];
        }
    }
    return ret;    
}

function correct_dict(dict_base,dict_add){
    // 無いキーは追加
    // 有るキーは数値の場合加算
    // 有るキーは辞書の場合合成（correct_dict）
    // 有るキーは文字の場合代入
    const addkeys = Object.keys(dict_add);
    for( let i = -1;++i<addkeys.length; ){
        const addkey = addkeys[i];
        if( !(addkey in dict_base) ){
            dict_base[addkey] = dict_add[addkey];
        }else if( !equal_type(dict_base[addkey],dict_add[addkey]) ){
            dict_base[addkey] = dict_add[addkey];
        }else{
            if( is_boolean(dict_base[addkey]) ){
                dict_base[addkey] = dict_add[addkey];
            }else if( !isNaN(dict_base[addkey]) && dict_base[addkey] !== "" ){
                dict_base[addkey] = dict_base[addkey]*1+dict_add[addkey]*1;
            }else if( is_string(dict_base[addkey]) ){
                dict_base[addkey] = dict_add[addkey];
            }else if( is_array(dict_base[addkey]) ){
                dict_base[addkey].concat(dict_add[addkey]);
            }else if( is_object(dict_base[addkey]) ){
                dict_base[addkey] = correct_dict(dict_base[addkey],dict_add[addkey]);
            }else{
                // その他のコレクションクラス、Freeze系？
                dict_base[addkey] = dict_add[addkey];
            }
        }
    }
    return dict_base;
}

function compare_dict(dict1,dict2){
    // return JSON.stringify(dict1) == JSON.stringify(dict2);
    const keys1 = Object.keys(dict1);
    const keys2 = Object.keys(dict2);
    if( keys1.length !== keys2.length ){
        return false;
    }
    for( let i = -1; ++i < keys1.length; ){
        const key = keys1[i];
        if( !(key in dict2) ){
            return false;
        }
        const type1 = typeof dict1[key];
        const type2 = typeof dict2[key];
        if( type1 !== type2 ){
            return false;
        }
        if( type1 === "function" ){
            continue;
        }else if( type1 === "object" ){
            if( !compare_dict(dict1[key],dict2[key]) ){
                return false;
            }
        }else if( dict1[key] !== dict2[key] ){
            return false;
        }
    }
        
    return true;
}

function dict_keycorrect(dict_base,dict_add){
    // 無いキーは追加
    // 有るキーは数値の場合加算
    // 有るキーは辞書の場合合成（correct_dict）
    // 有るキーは文字の場合代入
    var addkeys = Object.keys(dict_add);
    for( var i = -1;++i<addkeys.length; ){
        const addkey = addkeys[i];
        if( !dict_base.hasOwnProperty(addkey) ){
            dict_base[addkey] = dict_add[addkey];
        }else if( !equal_type(dict_base[addkey],dict_add[addkey]) ){
            dict_base[addkey] = dict_add[addkey];
        }else{
            if( is_boolean(dict_base[addkey]) ){
                dict_base[addkey] = dict_add[addkey];
            }else if( !isNaN(dict_base[addkey]) && dict_base[addkey] !== "" ){
                dict_base[addkey] = dict_add[addkey]*1;
            }else if( is_string(dict_base[addkey])
                    || is_array(dict_base[addkey]) ){
                dict_base[addkey] = dict_add[addkey];
            }else if( is_object(dict_base[addkey]) ){
                dict_base[addkey] = dict_keycorrect(dict_base[addkey],dict_add[addkey]);
            }else{
                // その他のコレクションクラス、Freeze系？
                dict_base[addkey] = dict_add[addkey];
            }
        }
    }
    return dict_base;
}
