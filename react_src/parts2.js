import './view_function.css';
import './view_design.css';

// import React from 'react';

import {
    InputNumber,
    InputText,
    InputPassword,
    InputButton,
    CheckBox,
    RadioButton,
    RadioButtonNone,
} from './parts.js'

import {choice_items,event_keys} from './util.js';

const adddata_components = {
    "number":InputNumber,
    "text":InputText,
    "bool":CheckBox,
}

export function AddDatas(props){
    const outputs        = [];
    
    const class_name     = props["is_main"]?"class_key":"";
    const funcs          = choice_items(props,event_keys);
    
    const adddata        = props["data"]["adddata"];
    const adddata_format = props["format"]["adddata_format"];
    
    for( let i = -1; ++i < adddata_format.length; ){
        const data     = adddata_format[i];
        const UsePart  = adddata_components[data["type"]];
        const typebool = data["type"] === "bool";
        const size     = typebool?"":data["size"];
        const style    = typebool?{}:{width:(data["size"]/2+1.5).toString()+"em"};
        const val      = data["key"] in adddata?adddata[data["key"]]:data["data"];
        const part_props = {
            ...funcs,
            key       : i,
            name      : data["name"],
            dbkey     : data["dbkey"],
            maxLength : size,
            value     : val,
            style     : style,
            className : class_name,
        }
        outputs.push(<UsePart {...part_props}/>);
    }
    return (<div name="adddata">{outputs}</div>);
}

export function RadioButtons(props){
    const funcs        = choice_items(props,event_keys);
    const common_props = {
        "group"    :"class_id"+("count" in props?"_"+props["count"]:""),
        "rawgroup" :"class_id",
        "className":"class_key",
    }
    
    const class_id  = props["data"]["class_id"]*1;
    const class_set = props["format"]["class_set"];
    
    const outputs   = [];
    
    if( props["None"] !== false ){
        const none_id   = 0;
        const none_key  = '0';
        const none_props = {
            ...funcs,
            ...common_props,
            "key"   : "none",
            "dbkey" : none_key,
            "name"  : "none",
            "value" : class_id===none_id
        }
        outputs.push(<RadioButtonNone {...none_props}/>);
    }
    const keys = Object.keys(class_set);
    for( let i = -1;++i < keys.length; ){
        const format = class_set[keys[i]];
        const rb_props = {
            ...funcs,
            ...common_props,
            "key"   : format["key"],
            "dbkey" : format["id"],
            "name"  : format["name"],
            "value" : class_id===format["id"],
        }
        outputs.push(<RadioButton {...rb_props} />);
    }
    
    // React.useEffect(()=>{
    //     const n = common_props["group"]
    //     const k = "[name='"+n+"'][value='"+class_id+"']";
    //     const t = document.querySelector(k);
    //     t.checked = true;
    // },[class_id])
    
    return (<>{outputs}</>);
}

export function Datas(props){
    const funcs    = choice_items(props,event_keys);
    const ad_props = {
        ...funcs,
        "is_main" : true,
        "data"    : props["data"],
        "format"  : props["format"]
    }
    return (<div><AddDatas{...ad_props}/></div>);
}

export function RadioButtonAndDatas(props){
    const funcs    = choice_items(props,event_keys);
    const rb_props = {
        ...funcs,
        "count"  : props["count"],
        "data"   : props["data"],
        "format" : props["format"]
    }
    const ad_props = {
        ...funcs,
        "is_main" : false,
        "data"    : props["data"],
        "format"  : props["format"]
    }
    return (<>
        <RadioButtons {...rb_props} />
        <div><AddDatas {...ad_props} /></div>
    </>);
}

export function AddDelSlotButton({count,view_type,children}){
    if( children.length >= 2 &&
          ( view_type === "multi radio" ||
            view_type === "multi radio and datas" ) ){
        if( count === 0 ){
            return (<>{children[0]}</>)
        }else{
            return (<>{children[1]}</>)
        }
    }
    return (<></>);
}