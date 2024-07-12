import {
    conv_types_detail,
    compand_types_detail,
    is_string,
} from './util.js';

const data_pre_process = (d_all) =>{
    for( let i = -1; ++i < d_all.length; ){
        const d = d_all[i];
        if( "data" in d && is_string(d["data"]) ){
            d["data"] = JSON.parse(d["data"]);
        }
    }
    return d_all;
}

const data_post_process = (id,d,d_all) =>{
    d["data"] = JSON.stringify(d["data"]);
    return d;
}

const expand_adddataformat = ({
            adddata_columns = null,
            adddata_format  = null,
        })=>{
    if( !is_string(adddata_format) ){ return []; }
    const ret = [];
    const types_detail = conv_types_detail(
        adddata_format,adddata_columns);
    for( let i = -1; ++i < types_detail.length; ){
        const type_detail = types_detail[i];
        ret.push({
            "adddata_name"  :type_detail["name"],
            "adddata_type"  :type_detail["datatype"],
            "adddata_length":type_detail["max_print"],
        })
    }
    return ret;
}
const expand_classtype = ({
            no_class       = false,
            single_class   = false,
            multi_class    = false,
            multi_data     = false,
            adddata_format = null,
        })=>{
    if( !!no_class ){
        return "no_class";
    }else if( !!single_class ){
        return "single_class";
    }else if( !!multi_class ){
        return "multi_class";
    }else{
        return "error";
    }
}
const classlist_pre_process = (datas)=>{
    if( !datas ){
        datas = [[],[]];
    }
    const ret = [];
    const ref = {};
    for( let i = -1; ++i < datas[0].length; ){
        const base_data = datas[0][i];
        const data      = {
            "id"         : base_data["id"],
            "class_name" : base_data["class_name"],
            "detail"     : base_data["detail"],
        };
        ret.push(data)
        ref[base_data["id"]]   = data;
        data["class_type"]     = expand_classtype(base_data);
        data["class_set"]      = [];
        data["adddata_format"] = expand_adddataformat(base_data);
    }
    for( let i = -1; ++i < datas[1].length; ){
        const data = datas[1][i];
        ref[data["class_settings_id"]]["class_set"].push(data);
    }
    return ret;
}

const compand_adddataformat = (formats)=>{
    // lengthは削除する
    // 4h256sなどの書式の中に項目長を含めるため
    // 入力側のsなどに対応したlengthが必要
    
    const adddata_columns = [];
    const type_array      = [];
    const length_array    = [];
    for( let i = -1; ++i < formats.length; ){
        const format = formats[i];
        adddata_columns.push(format["adddata_name"]);
        type_array.push(format["adddata_type"]);
        length_array.push(format["adddata_length"] || 1);
    }
    const [adddata_format,adddata_length] = compand_types_detail(
        type_array,length_array);
    return {
        "adddata_columns":adddata_columns.join(","),
        "adddata_format" :adddata_format,
        "adddata_length" :adddata_length,
    }
}
const compand_classtype = (classtype)=>{
    return {
        "no_class"    : classtype === "no_class"    ,
        "single_class": classtype === "single_class",
        "multi_class" : classtype === "multi_class" ,
    }
}
const compand_classset = (d)=>{
    const id = d["id"];
    const class_set = d["class_set"];
    for( let i = -1; ++i < class_set.length;){
        const c = class_set[i];
        c["class_settings_id"] = id;
        c["class_id"] = i+1;
    }
    return class_set;
}
const classlist_post_process = (id,d,d_all)=>{
    console.log(id,d,d_all);
    return {
        "class_settings":{
            "class_name" : d["class_name"],
            "detail" :  d["detail"],
            "id": d["id"],
            ...compand_adddataformat(d["adddata_format"]),
            ...compand_classtype(d["class_type"])
        },
        "class_set":compand_classset(d)
    }
}
    
// pre and post process colector
export const prepost_process = {
    "default":{
        "pre_process" :(d)=>d,
        "post_process":(id,d,d_all)=>d,
    },
    "parameter":{
        "pre_process" :data_pre_process,
        "post_process":data_post_process,
    },
    "classlist":{
        "pre_process" :classlist_pre_process,
        "post_process":classlist_post_process,
    },
}