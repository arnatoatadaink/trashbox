import React,{TransitionEvent,createContext,useContext,useState,useReducer,useEffect} from 'react';
import ReactDOM from 'react-dom/client';
import './view_function.css';
import './view_design.css';
import './loader.css';

import {
    InputNumber,
    InputText,
    InputPassword,
    InputButton,
    CheckBox,
    RadioButton,
    RadioButtonNone,
    Pin,
} from './parts.js'
import {
    AddDatas,
    RadioButtons,
    Datas,
    RadioButtonAndDatas,
    AddDelSlotButton,
} from './parts2.js'
import {
    PatternRoot,
    ExpandSelectOptions,
    Appender,
    Selector,
    SimpleSelector,
} from './part_util.js';

import {prepost_process} from './prepost_process.js';

import {load_info,save_info} from './storage_forpage.js';
import {choice_items,event_keys,compare_dict,copy_dict,
    check_limit,remove_cookie,array_make,datatypes,
    array2dict,get_dictvalue} from './util.js';
import {get_page_values,set_page_values,
    control_accordions} from './page_util.js';
    
import {GetRequest,PostRequestByForm,LoadHundler} from './connect.js';

import sender from './view_action.js';
 
const LoadCover = React.forwardRef((props,ref)=>{
    
    const load_ref = React.useRef();
    const toggle_cover = React.useCallback((key)=>{
        const target = load_ref.current;
        const has = target.classList.contains("hide");
        const ret = has === key;
        if( ret ){
            target.classList.toggle("hide");
            target.classList.remove("transitionend");
        }
        return ret;
    },[load_ref]);
    useEffect(()=>{toggle_cover(false)},[toggle_cover]);
    
    ref.current = React.useMemo(()=>{return {
        load    : toggle_cover.bind(null,true),
        loaded  : toggle_cover.bind(null,false)
    }},[toggle_cover]);
    
    return (<div ref={load_ref} className="cover">
        <div className="loader">Loading...</div>
    </div>);
});

function MakeInheritComponent(LAYER_CONTEXT){
    const useInherit = () => {
        return useContext(LAYER_CONTEXT);
    };
    const Inherit = ({ children ,...props}) => {
        return (<LAYER_CONTEXT.Provider value={props}>
                    {children}
                </LAYER_CONTEXT.Provider>);
    };
    return [Inherit,useInherit];
}
const [MenuContext,useMenuContext]   = MakeInheritComponent(createContext());
const [LoginContext,useLoginContext] = MakeInheritComponent(createContext());

function useSender(url){
    
    const [regkey,setRegkey] = useState(null);
    const token = useLoginContext().token;
    
    const sendinstance = React.useCallback((query,datas)=>{
        setRegkey(sender.set(
            url,
            query,
            datas,
            token,
            regkey));
    },[url,regkey,token]);
    
    return sendinstance
}

function Flags(props){
    const outputs = [];
    
    const funcs   = choice_items(props,event_keys);
    const formats = props["formats"];
    const data    = props["data"];

    const keys    = Object.keys(formats);
    for( let i = -1; ++i < keys.length; ){
        const format = formats[keys[i]];
        const cb_props = {
            "key"    : format["key"],
            "is_main": false,
            "dbkey"  : format["key"],
            "name"   : format["name"],
            "value"  : data[format["key"]]
        }
        outputs.push(<CheckBox {...cb_props}{...funcs}/>);
    }
    return (<>{outputs}</>);
}

function DataView(props){
    const data_settings_id = props.data.data_settings_id;
    const data_id          = props.data.data_id;
    const source           = "http://localhost:8000/"+props.data.data; // TODO image server
    return (<>
        <img 
            data-settings={data_settings_id}
            data-id={data_id}
            src={source}
            alt={"ref error "+JSON.stringify(props)}>
        </img>
    </>);
}

function ClassView ({
        data:{view_type,format,flags,datas},
        ...props}){
    const sender = useSender("http://localhost:8000/classes");
        
    const conv = (datas,flags)=>{
        return {
            "datas":datas, 
            "flags":{
                "dis":flags["dis"]["data"],
                "unk":flags["unk"]["data"],
                "uns":flags["uns"]["data"]
            }
        }
    }
    
    const [state,setState] = useState(conv(datas,flags));
    
    React.useEffect(()=>{
        setState(conv(datas,flags))
    },[datas,flags])
    
    const token = useLoginContext().token;
    const pickup   = React.useCallback((new_state=false)=>{
        if( !new_state ){
            new_state = get_page_values("#class_view > [id]");
        }else{
            set_page_values("#class_view > [id]",new_state);
        }
        const is_change = !compare_dict(new_state,state);
        if( is_change ){
            const query = props.getstate();
            sender(query,new_state);
            setState(new_state);
        }else{
            console.log("state no changes");
        }
    },[state,setState,token]);

    const UsePart = React.useMemo(()=>{
        if( view_type === "radio" || 
                view_type === "multi radio" ){
            return RadioButtons;
        }else if( view_type === "data" ){
            return Datas;
        }else if( view_type === "radio and data" ||
                   view_type === "multi radio and datas" ){
            return RadioButtonAndDatas;
        }
        return null;
    },[view_type]);
    
    const addbutton_prop = React.useMemo(()=>{return {
        "className":"option_button",
        "name":"+",
        "view_type":view_type,
        "onClick":(e)=>{
            const new_datas = copy_dict(state);
            const new_slot = {}
            new_datas["datas"].push(new_slot);
            if( format["class_set"].length > 0 ){
                new_slot["class_id"] = '0';
            }
            if( format["adddata_format"].length > 0 ){
                const adddata_format = format["adddata_format"];
                new_slot["adddata"] = {}
                for( let i = -1; ++i < adddata_format.length; ){
                    const key = adddata_format[i]["key"];
                    const def = adddata_format[i]["data"];
                    new_slot["adddata"][key] = def;
                }
            }
            pickup(new_datas,true);
        }
    }},[view_type,pickup,format]);
    const delbutton_prop = React.useMemo(()=>{return {
        "className":"option_button",
        "name":"×",
        "view_type":view_type,
        "onClick":(e)=>{
            const target = e.target.parentElement;
            const cnt = target.getAttribute("data-count");
            const new_datas = copy_dict(state);
            new_datas.datas.splice(cnt,1);
            pickup(new_datas,true);
        }
    }},[view_type,pickup]);

    
    const outputs  = [];
    const callback = ()=>pickup();
        
        // expand rows
        const keys = Object.keys(state.datas);
        for( let i = -1; ++i < keys.length; ){
            const data = state.datas[keys[i]];
            outputs.push(<div key={"divpart_"+i} data-count={i}>
                <UsePart count={i} format={format} data={data} onClick={callback}/>
                <AddDelSlotButton count={i} view_type={view_type}>
                    <InputButton {...addbutton_prop}/>
                    <InputButton {...delbutton_prop}/>
                </AddDelSlotButton>
            </div>
            )
        }
    return (<>
        <div
            className="classes imitate_list"
            id={"datas"}>
            {outputs}
        </div>
        <div className="flags" id="flags">
            <Flags
                formats={flags}
                data={state.flags}
                onClick={callback}/>
        </div>
    </>);
}

function NavView(props){
    const outputs = [];
    const keys    = ["prev","next","next_unset","next_unknown"];
    for( let i = -1; ++i < keys.length; ){
        const key = keys[i];
        if( !props.data[key] ){ continue }
        const clicked = ()=>{
            props.updater(props.state_name,props.data[key]);
            props.reload();
        }
        const set_props = {
            "key":key,"id":key,"value":key,
            "type":"button","onClick":clicked,
        }
        outputs.push(<input {...set_props}/>);
    }
    return (<>{outputs}</>);
}

function InfoView(props){
    const info_data = props.data;
    
    return (<>
        <div>
        <span>索引 </span>
        <span>{ info_data['data_id'       ] }</span>
        <span> / </span>
        <span>{ info_data['data_count'    ] }</span>
        <span> ( 未設定 : { info_data['unset_total'   ] } 件 / </span>
        <span>   不明   : { info_data['unknown_total' ] } 件 / </span>
        <span>   無効   : { info_data['dissable_total'] } 件 ) </span>
        </div>
    </>);
}

//////////////// list pattern ////////////////
// TODO
//   パネルの開閉制御
//
// deliv part3.js
export function DummyPanel({name:name,children:children}){
    return (<div>
        <div style={{"width":"auto"}}>{name}</div>
        <div className="dummy_panel">
            <div>{children}</div>
        </div>
    </div>);
}

export function DummySpanPanel({name:name,children:children}){
    return (<span>
        <span style={{"width":"auto"}}>{name}</span>
        <div className="dummy_panel">
            <div>{children}</div>
        </div>
    </span>);
}

// TODO
//   state更新による画面初期化の対策
//     maxHeight 100% から開始することで都度の再展開防止が出来た
//     選択状態は記録していないためon/offの保持制御は効かない
//   画面上の選択状態をstateとして配置し再配布する
//   ActivePanel上のidを設定し
//   IDに紐づく情報を管理する
//     state更新毎にidも更新される
export function ActivePanel({default_open=false,name,children}){
    const ref = React.useRef();
    React.useLayoutEffect(()=>{
        control_accordions(ref.current,true);
    },[ref.current])
    const accordion_props = {
        className : "accordion",
        ref       : ref,
        style     : {"width":"auto"},
    }
    const panel_props = {
        className : "panel",
        style     : {},
    }
    if( default_open ){
        accordion_props.className += " active";
        panel_props.className += " active";
        panel_props.style = {"maxHeight":"100%"}
    }
    return (<div>
        <div {...accordion_props}>{name}</div>
        <div {...panel_props}>
            <div>{children}</div>
        </div>
    </div>);
}

export function ActiveSpanPanel({default_open=false,name,children}){
    const ref = React.useRef();
    React.useLayoutEffect(()=>{
        control_accordions(ref.current,true);
    },[ref.current])
    const accordion_props = {
        className : "accordion",
        ref       : ref,
        style     : {"width":"auto"},
    }
    const panel_props = {
        className : "panel",
        style     : {},
    }
    if( default_open ){
        accordion_props.className += " active";
        panel_props.className += " active";
        panel_props.style = {"maxHeight":"100%"}
    }
    return (<span>
        <span {...accordion_props}>{name}</span>
        <div {...panel_props}>
            <div>{children}</div>
        </div>
    </span>);
}
// // ListItem細分化のComponent
// function ChildFuncExpand({
// }){
//     // children[i](data) の形式で下位objectを生成するか検討しているもの
// }
function ExpandDict({
        data:data,
        keys:keys,
        labels:labels=undefined,
        setdiv:setdiv=true}){
    const outputs = [];
    const View = setdiv?"div":"span";
    labels = labels?labels:keys;
    console.assert(
        keys.length<=labels.length,
        "ExpandDict : label array out of bounds");
    for( let i = -1; ++i < keys.length; ){
        const key   = keys[i];
        const label = labels[i];
        console.assert(
            key in data,
            "ExpandDict : invalid key");
        outputs.push(<View key={i}> {label} : {data[key]} </View>);
    }
    return (<>{outputs}</>)
}
function ExpandDictList({
        datas:datas,
        keys:keys,
        labels:labels=undefined,
        setdiv:setdiv=true}){
    const props = {
        keys:keys,
        labels:labels?labels:keys,
        setdiv:setdiv
    }
    const outputs = [];
    for( let i = -1; ++i < datas.length; ){
        const data  = datas[i];
        outputs.push(<div key={i}>
            <ExpandDict data={data} {...props}/></div>);
    }
    return (<>{outputs}</>)
}
function DictView({
        name:name,
        data:data,
        keys:keys,
        labels:labels=undefined}){
    const props = {
        keys:keys,
        labels:labels,
        data:data,
        setdiv:true
    }
    return (
        <DummyPanel name={name}>
            <ExpandDict {...props}/>
        </DummyPanel>);
}
function DictListView({
        name:name,
        datas:datas,
        keys:keys,
        labels:labels=undefined}){
    const props = {
        keys:keys,
        labels:labels,
        datas:datas,
        setdiv:false
    }
    return (
        <DummyPanel name={name}>
            <ExpandDictList {...props}/>
        </DummyPanel>);
}

function RowLabel({
            data:datas,
            state_name,
            label_keys:keys = []
        }){
    const ret  = [];
    const id   = state_name+"_"+datas[state_name];
    for( let i = -1; ++i < keys.length; ){
        const key  = keys[i];
        const data = datas[key];
        const label_props = {
            htmlFor:id,
            className:"list_item_data",
            key:key
        }
        ret.push(<label {...label_props}>{key} : {data}</label>)
    }
    return ret;
}

function RowDetail(props){
    const ret  = [];
    const dict = props.data;
    const keys = Object.keys(dict);
    for( let i = -1; ++i < keys.length; ){
        const key  = keys[i];
        const data = dict[key];
        ret.push(<div key={key}>{key} : {data}</div>)
    }
    return ret;
}

function ListRow({
        label_view  = RowLabel,
        detail_view = RowDetail,
        state_name,
        checked,
        ...props}){
    const id      = state_name+"_"+props["data"]["id"];
    const ref = React.useRef();
    const click_rb = (e)=>ref.current.click()
    const rb_props = {
        className : "accordion",
        rawgroup  : id,
        group     : state_name,
        val       : checked
    }
    const panel_props = {
        id        : id+"_panel",
        className : "panel close_other",
            style     : {},
    }
    
    if( checked ){
        rb_props.className += " active";
        panel_props.className += " active";
        panel_props.style = {"maxHeight":"100%"}
    }
    
    const LabelView  = label_view;
    const DetailView = detail_view;
    const label      = <LabelView  {...props}/>;
    const detail     = <DetailView {...props}/>;

    React.useLayoutEffect(()=>{
        control_accordions(ref.current,true);
    },[ref.current]);

    return (<div onClick={click_rb} className="list_item">
        <RadioButton ref={ref} {...rb_props}/>
        <span onClick={click_rb}>{label}</span>
        <div  onClick={click_rb} {...panel_props}>{detail}</div>
    </div>);
}

function makeRowLabel(label_keys){
    function RowLabelImple(props){
        const base_props = {...props}
        base_props["label_keys"] = label_keys;
        return (<RowLabel{...base_props}/>);
    }
    return RowLabelImple;
}

// TODO 追加、削除用にuseContextを仕込む？
// いきなり削除したらエラーが発生するため無効化のみ
// 引き当て時に無効なIDが混じっていたら後続処理でエラー
export function SelectListView({
        detail_view  = undefined,
        label_view   = undefined,
        state_name,
        pre_process = (d)=>d,
        forSender   = undefined,
        forCopy     = undefined,
        ...props}){
    
    const select_row = props.updater.bind(null,state_name);
    const datas      = pre_process(props.data)
    const keys       = Object.keys(datas);
    const selected   = props.getstate()[state_name]
    const outputs    = [];
    
    for( let i = -1; ++i < keys.length; ){
        const key     = keys[i];
        const data    = datas[key];
        const id      = data.id;
        const checked = ""+selected === ""+id;
        const func    = select_row.bind(null,id);
        
        const base_props = {...props}
        base_props["checked"]     = checked;
        base_props["data"]        = data;
        base_props["datas"]       = data;
        base_props["state_name"]  = state_name;
        base_props["label_view"]  = label_view;
        base_props["detail_view"] = detail_view;
        base_props["save_state"]  = (value)=>{
            if( !forSender ){return}
            datas[key] = value;
            forSender(key,value,datas);
        };
        base_props["copy_state"] = (value)=>{
            if( !forCopy ){ return }
            forCopy(value);
        }
        
        outputs.push(<div key={key} onClick={func}>
            <ListRow {...base_props}/>
        </div>);
    }
    return (<div>{outputs}</div>);
}

export function AppedableClassListView(props){
    
    const format_options = array2dict(datatypes);
    const base_props = {...props};
    // state
    const pp = prepost_process["classlist"];
    base_props["pre_process"]  = pp["pre_process"];
    base_props["post_process"] = pp["post_process"];
    base_props["checkbox_right"] = true;
    base_props["label_names"]    = ["id","class_name","detail"];
    base_props["save_keys"]      = ["id"];
    base_props["save_path"]      = "http://localhost:8000/class_settings";
    base_props["default_edit"]   = false;
    base_props["new_row"]        = false;
    // view
    base_props["root_name"] = "settings";
    base_props["formats"] = {
        "default":{
            "options":{
                "appendable":false,
                "deletable" :false,
                "changeable":true,
                "editbutton":false,
            }
        },
        "settings":{
            "append_default":{
                "id":"new key",
                "name":"",
                "detail":"",
                "class_type":"single_class",
                "class_set":[],
                "adddata_format":[],
            },
            "options":{
                "appendable":false,
                "deletable" :false,
                "changeable":true,
                "editbutton":true,
            }
        },
        "settings>id":{
            "options":{
                "appendable":false,
                "deletable" :false,
                "changeable":false,
                "editbutton":false,
            }
        },
        "class_type":{
            "view":Selector,
            "append_props":{
                "use_none":false,
                "group_clip":false,
                "base_types":{
                    "no_class"     : "no_class"    ,
                    "single_class" : "single_class",
                    "multi_class"  : "multi_class" ,
                },
            },
        },
        "class_set":{
            "options":{
                "appendable_newrow":true,
                "deletable_newrow" :true,
                "changeable_newrow":true,
                "editbutton":false,
            },
            "append_default":{
                "class_settings_id":-1,
                "class_id"  :-1,
                "class_key" :"",
                "class_name":"",
            }
        },

        "class_set.row":{
            "append_props":{
                "is_row":true
            }
        },
        "class_settings_id":{
            "append_props":{
                "hidden":true
            }
        },
        "class_id":{
            "append_props":{
                "hidden":true
            }
        },
        "class_key":{
            "append_props":{
                "label":"key"
            }
        },
        "class_name":{
            "append_props":{
                "label":"name"
            }
        },
        "adddata_format":{
            "append_default":{
                "adddata_name":"",
                "adddata_type":"None",
            },
            "options":{
                "appendable_newrow":true,
                "deletable_newrow" :true,
                "changeable_newrow":true,
            }
        },
        "adddata_format.row":{
            "append_props":{
                "is_row":true
            }
        },
        "adddata_name":{
            "append_props":{
                "label":"name",
            }
        },
        "adddata_type":{
            "view":Selector,
            "append_props":{
                "label":"type",
                "group_clip":false,
                "base_types":format_options,
            },
            "options":{
                "changeable_newrow":true,
            }
        },
        "adddata_length":{
            "append_props":{
                "label":"length",
                "size":8,
                "use_lengthstyle":true,
            },
            "options":{
                "changeable_newrow":true,
            }
        },
    }
    
    return (<AppendableList2 {...base_props}/>);
}

function ProcessSelector(props){
    const props2 = {...props}
    props2["base_types"] = Object.keys(prepost_process);
    props2["use_none"]   = false;
    return <SimpleSelector {...props2}/>
}

export function AppendablePagingListView(props){
    const base_props = {...props};
    
    const pp = prepost_process["parameter"];
    base_props["pre_process"]  = pp["pre_process"];
    base_props["post_process"] = pp["post_process"];
    base_props["checkbox_right"] = true;
    // base_props["active_panel"]   = true;
    base_props["root_name"]    = "page";
    base_props["label_names"]  = ["id"];
    base_props["save_keys"]    = ["id"];
    base_props["save_path"]    = "http://localhost:8000/page_parameters";
    base_props["default_edit"] = false;
    base_props["new_row"]      = false;
    base_props["formats"] = {
        "page":{
            "append_default":{
                id         : "new id",
                enabled    : false,
                data       : {
                    menu : {
                        title      : "", // ページのタイトル
                        state_name : "", // これは追加キーとしてpageで使用する
                        clip_name  : "", // clipの親名、同じ名前を持つページを括る
                        clip_id    : -1, // clip上のorder、同値の場合、idの昇順
                        detail     : "", // pageの説明
                        ref_path   : "", // 読み込むbackendのpath
                        ref_type   : "", // 読み込み方法
                    },
                    view : {
                        preandpost_process:"default",
                        save_path  :"",
                        save_keys  :[],
                        label_names:[],
                        root_name  : "",
                        formats    : {
                            "default":{
                                "append_default":undefined,
                                "view"   : undefined,
                                "options": undefined,
                            },
                        },
                    },
                }
            },
            "options":{
                appendable : false,
                deletable  : false,
                changeable : true,
                editbutton : true,
            }
        },
        "preandpost_process":{
            "view":ProcessSelector,
            "append_default":"default",
            "options":{
                changeable : true,
            }
        },
        "page>data.value":{
            "append_props":{
                "active_panel":true,
            }
        },
        "save_keys":{
            "append_default":"",
            "options":{
                appendable:true,
                deletable :true,
                changeable:true,
            }
        },
        "label_names":{
            "append_default":"",
            "options":{
                appendable:true,
                deletable :true,
                changeable:true,
            }
        },
        "ref_type":{
            "view":Selector,
            "append_props":{
                "group_clip":false,
                "base_types":{
                    "load"   : "load",   // url
                    "local"  : "local",  // local strage
                    "render" : "render", // static for test
                },
            },
            "options":{
                changeable:true,
            }
        },
        "formats":{
            "append_props":{
                "base_types":{
                    "normal":{
                        "view":"",
                        "options":null,
                        "append_default":null,
                        "append_props":{},
                    },
                    "select":{
                        "view":"Selector",
                        "options":null,
                        "append_props":{
                            "base_types":{},
                            "group_clip":false,
                        },
                    },
                },
                "group_clip":false,
            },
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "formats.value":{
            "append_props":{
                "active_panel":true,
            }
        },
        "append_default":{
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "append_default.row":{
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "append_default.value":{
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "append_props":{
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "base_types":{
            "options":{
                appendable : true,
                deletable  : true,
                changeable : true,
                editbutton : false,
            },
        },
        "options":{
            "append_default":{
                appendable : false,
                deletable  : false,
                changeable : true,
                editbutton : false,
            },
        },
        "page>id":{
            "options":{
                appendable : false,
                deletable  : false,
                changeable : false,
                editbutton : false,
            }
        },
        "default":{
            "options":{
                appendable : false,
                deletable  : false,
                changeable : true,
                editbutton : false,
            }
        },
    }
    
    
    return (<AppendableList2 {...base_props}/>)
}

// TODO appendable top list
// set keys / set targets( url / read connection / save connection )
export const AppendableList = (({
            title,
            state_name,
            info_keys   = [],
            target_url  = "",
            // output_func = undefined, // unneccessary
            data = {},
            forSender = undefined,
            ...props
        })=>{
    
    const copy_data = copy_dict(data)
    const [appendable,setAppendable] = React.useState(false);
    const appendbutton_props = {
        "className" : "option_button",
        "name"      : "Append Row",
        "onClick"   : ()=>setAppendable(true),
    }
    const [appendvalue,setAppendvalue] = React.useState(undefined);
    // TODO
    //   set_appendable(true)の他に
    //   copy buttonを配置して
    //   既存パラメーターをコピーして増やしたい
    const forCopy = (d)=>{
        d.id = "copied : "+d.id;
        setAppendvalue(d);
        setAppendable(true);
    }
    const append_props = {...props}
    const save_state = (d)=>{
        let id = 0;
        if( copy_data.length > 0 ){
            id = copy_data[copy_data.length-1].id;
        }
        d.id = id+1;
        forSender(d.id,d,copy_data.concat([d]));
        setAppendable(false);
        setAppendvalue(undefined);
    }
    const discard_state = (d)=>{
        setAppendable(false);
        setAppendvalue(undefined);
    }
    append_props["save_state"]    = save_state;
    append_props["discard_state"] = discard_state;
    append_props["datas"]         = appendvalue;
    append_props["default_edit"]  = true;
    append_props["new_row"]       = true;
    
    // TODO
    //   select list view においてliftStateする方法
    //   下位view側に暫定実装を用意した
    //     PatternRoot以降はLiftState
    //     それ以上はsavestateでコントロール
    //       名称の整備
    // TODO
    //   暫定実装
    //     規格整備を未実施
    //     使いまわす予定なので
    //     PatternRootなどを含め名称の整備が必要
    //       整備に際してRow関連もpart_utilに配備する
    return (<div>
            <SelectListView {...{
                state_name  : state_name,
                data        : copy_data,
                forSender   : forSender,
                forCopy     : forCopy,
                ...props
            }}/>
            {!appendable // append button
                && <InputButton {...appendbutton_props}/>}
            {appendable // edit append value
                && <PatternRoot {...append_props}/> }
        </div>);
});

// TODO
//   auto fit by pager params
export const AppendableList2 = (({
            pre_process  = (d)=>d,
            post_process = (id,d,d_all)=>d, // for sending data
            ...props})=>{
    const base_props = {...props};
    
    const data = pre_process(base_props["data"]);
    const [state,setState] = React.useState(data);
    base_props["data"]  = state;
    base_props["datas"] = state;
    base_props["checkbox_right"] = true;
    // base_props["active_panel"]   = true;
    base_props["name"]  = base_props["root_name"];
    base_props["default_edit"] = false;
    base_props["new_row"]      = false;

    // senderはsingletonとして本体を配置し
    // singleton上で送受信のコントロールを行う
    // useSenderでは未送信状態のデータ変更追跡を行う
    const sender = useSender(base_props["save_path"]);
    
    base_props["forSender"] = React.useCallback((id,d,d_all)=>{
        if( state.length != d.length ){
            // pass
        }else if( !compare_dict(state[id],d) ){
            // pass
        }else{
            return;
        }
        // TODO
        //   add post process
        // post_process
        const new_data = post_process(id,copy_dict(d),d_all);
        const query = {};
        const save_keys = base_props["save_keys"];
        for( let i = -1; ++i < save_keys.length; ){
            const key = save_keys[i];
            query[key] = new_data[key];
        }
        console.log("query : ",query.toString())
        console.log("body : ",new_data.toString())
        // 特定したデータを送信する
        sender(query,new_data);
        // 更新したデータをstateに反映する
        setState(d_all);
    },[state,sender]);
    return (<AppendableList
        {...base_props}
        label_view  = {makeRowLabel(base_props["label_names"])}
        detail_view = {PatternRoot}
    />)
});

function Menu(props){
    
    // console.log(props.append_menus);
    
    const set_logout = useLoginContext().do_logout;
    // horizontal
    // vertical
    
    // vertical hide toggle button
    // horizontal auto hide toggle button
    // let class_name = "menu vertical";
    let class_name = "menu horizontal";
    const clip_pattern = (menu,i) => {
        const View = "inner"in menu?MenuClip:MenuItem;
        const view_props = {
            key  : "menu_"+i,
            menu :  menu,
        }
        return (<View {...view_props}/>);
    }
    let menus = array_make(props.menus,clip_pattern)
    // TODO
    //   menu bar to add transform action for enhans

    function parent_toggleclass(e){
        const pin = e.target.closest(".pin");
        pin.parentElement.classList.toggle("hide");
    }

    return (
        <div className={class_name}>
            <div className="pin togglebutton row"
                 onClick={parent_toggleclass}>
                <div className="head"></div>
                <div className="needle"></div>
            </div>
            {menus}
            <div className="menu_item logout row"
                 onClick={set_logout}>
                <div>log out</div>
            </div>
        </div>
    );
}

function MenuClip(props){
    // TODO dropdown list
    const menu_prop = {
        className:"row",
    }
    const clip_pattern = (menu,i)=>(
        <MenuItem key={"menu_"+i}menu={menu}{...menu_prop}/>);
    const menu_clip = array_make(
        props.menus,clip_pattern);
    return (<div className="menu_clip row">{menu_clip}</div>);
}

function MenuItem({
        menu:{
            title,
            state_name,
            use_subtitle  = false,
            load_action   = undefined,
            render_action = undefined,
        },...props}){
    const {
        getstate : getstate,
        setview  : setview,
        selected : selected,
    } = useMenuContext();
    
    // check subtitle func
    // state_name内の値で参照したいが、それが出来ないため
    // この場合、stateの参照が切れる、Pythonとの違い
    // const {state_name:state_value} = getstate();
    const state_value = getstate()[state_name];
    const subtitle = state_name + " : " + state_value;
    // render func
    const data = {
        state_name : state_name,
        ...useMenuContext()
    };
    const render_view = React.useCallback(()=>{
        if( selected(state_name) ){ return }
        if( load_action ){
            const view_props = {
                load_action:load_action(data),
                type:"load",
                name:state_name,
            }
            setview(view_props);
        }else if( render_action ){
            const view_props = {
                view:render_action(data),
                type:"paste",
            }
            setview(view_props);
        }else{
            console.assert(false,"menu item props error",state_name);
        }
    },[load_action,data]);
    
    return (<div className="menu_item row" onClick={render_view}>
        <div>{title}</div>
        <div>{use_subtitle && state_value && subtitle}</div>
    </div>);
}

// TODO MenuClip drop down list
function DropDownList(props){
    
}

// function MenuLabel(props){
//     const inheritprops = props.inheritprops;
//     const get_menu = get_dictvalue.bind(null,props.menu);
//     
//     // check title
//     const title        = get_menu("title");
//     const state_name   = get_menu("state_name");
//     // check subtitle func
//     const use_subtitle = get_menu("use_subtitle");
//     const state_value  = inheritprops.getstate()[state_name];
//     const subtitle     = state_name+" : "+state_value;
//     // render func
//     const data = {
//         state_name:state_name,
//         ...inheritprops
//     };
//     const view = get_menu("load_action")(data);
//     const view_prop = {
//         view:view,
//         type:"load"
//     };
//     const render_view = ()=>inheritprops.setview(view_prop);
//     
//     const item_props = {
//         className:"menu_item row",
//         onClick:render_view
//     }
//     
//     return (<div {item_props}>
//         <div>{title}</div>
//         <div>{use_subtitle && state_value && subtitle}</div>
//     </div>);
//     return (<>{props.children}</>);
// }

// ReactのRenderから分離
class LoadDatas extends LoadHundler{
    constructor({response,...props}){
        super(props);
        this.response = response;
    }
    loaded(datas){
        this.response(datas)
    }
    send_request(){
        const View = this.view;
        const suc_func = (res,data) => {
            this.loaded(data);
        }
        const err_func = (err)=>{
            if( !(err instanceof Error) ){
            }else if( check_limit(err.status,400,499) ){
            }else if( check_limit(err.status,500,599) ){
            }
            this.loaded({});
        }
        const fin_func = ()=>{}
        const request_item  = new GetRequest(
            this.props.url,
            null,null,null,
            suc_func,err_func,fin_func);
        request_item.request();
    }
}

// ReactのRenderから分離
class LoadAction extends LoadHundler{
    constructor({view:view,...props}){
        super(props);
        this.view = view;
    }
    loaded(view){
        const action = {
            view:view,
            type:"loaded",
        }
        this.props.inheritprops.setview(action)
    }
    send_request(){
        const View = this.view;
        const suc_func = (res,data) => {
            this.loaded(<View
                data={data}
                {...this.props}
                {...this.props.inheritprops}/>);
        }
        const err_func = (err)=>{
            if( !(err instanceof Error) ){
            }else if( check_limit(err.status,400,499) ){
            }else if( check_limit(err.status,500,599) ){
            }
            this.loaded(<div>{err.toString()}</div>);
        }
        const fin_func = ()=>{}
        const request_item  = new GetRequest(
            this.props.url,
            null,null,null,
            suc_func,err_func,fin_func);
        request_item.request();
    }
}

// Loading
class ClassifierLoadAction extends LoadAction{
    constructor(props){
        super(props);
        this.count = 0;
        this.views = [];
    }
    reload(){
        this.count = 0;
        this.views = [];
        // this.send_request();
        const action = {
            load_action:this,
            type:"load"
        };
        this.props.inheritprops.setview(action);
    }
    loaded(view,i){
        this.count++;
        this.views[i] = view;
        if( this.count < 4 ){
            return;
        }
        const action = {
            view:(<div>{this.views}</div>),
            type:"loaded"
        };
        this.props.inheritprops.setview(action);
    }
    send_request(){
        const loaded         = this.props.inheritprops.getstate();
        loaded["data_id"] = loaded["data_id"]?loaded["data_id"]:1;
        const dataclass_dict = choice_items(
            loaded,["data_settings_id","class_settings_id","data_id"]);
        const data_dict      = choice_items(
            loaded,["data_settings_id","data_id"]);
        const request_array = [
            {id:"data_view" ,view:DataView ,url:this.props.data_url ,query:data_dict},
            {id:"class_view",view:ClassView,url:this.props.class_url,query:dataclass_dict},
            {id:"nav_view"  ,view:NavView  ,url:this.props.nav_url  ,query:dataclass_dict},
            {id:"info_view" ,view:InfoView ,url:this.props.info_url ,query:dataclass_dict},
        ];
        const inheritprops = {
            ...this.props.inheritprops,
            reload:()=>this.reload()
        };
        for( let i= -1; ++i < request_array.length; ){
            this.views.push("");
            const request_data  = request_array[i];
            const content_id    = request_data.id;
            const content_url   = request_data.url;
            const content_query = request_data.query;
            const View          = request_data.view;
            const suc_func = (res,data) => {
                this.loaded((<div id={content_id} key={i}>
                        <View data={data} {...inheritprops}/>
                    </div>),i);
            }
            const err_func = (err)=>{
                if( !(err instanceof Error) ){
                }else if( check_limit(err.status,400,499) ){
                }else if( check_limit(err.status,500,599) ){
                }
                this.loaded(<div>{err.toString()}</div>,i);
            }
            const fin_func = ()=>{}
            const request_item  = new GetRequest(
                content_url,null,null,content_query,
                suc_func,err_func,fin_func);
            request_item.request();
        }
    }
}

// LoadCoverを切り出す
// ViewStateContext/Request/Menu関連は依存関係で結ぶ
export function LoginView(props){
    const load_ref = React.useRef();
    const [state,setState] = useState({message:"",token:""});
    useEffect(()=>{check_logined();},[])
    
    const loginform_data = ()=>{
        const login_username = document.querySelector("#login_form .login_username").value;
        const login_password = document.querySelector("#login_form .login_password").value;
        return {
            "grant_type":"",
            "username":login_username,
            "password":login_password,
            "scope":"",
            "client_id":"",
            "client_secret":""
        }
    }
    // set cover
    const load = ()=>load_ref.current.load();
    const loaded = ()=>load_ref.current.loaded();
    
    // control token
    const set_logout = ()=>{
        remove_cookie("token");
        setState({"message":"log off","token":""});
    }
    const set_logon = (token)=>{
        setState({"message":"","token":token});
    }
    const set_login_error = (message)=>{
        setState({"message":message,"token":""});
    }

    // response
    const suc_func = (res,data)=>{
        if( data.access_token.length > 0 ){
            set_logon(data.access_token);
        }else{
            set_login_error("login error");
        }
    }
    const err_func = (err)=>{
        set_login_error("login error");
    }
    const expire_func = (err)=>{
        set_login_error("need login");
    }
    
    // sender
    const check_logined = React.useCallback(()=>{
        // did mount
        // do check a logined token
        // コンポーネントがマウントされた（ツリーに挿入された）直後に呼び出されます
        const request_item  = new GetRequest(
            "http://localhost:8000/check_token",
            null,null,null,
            suc_func,
            expire_func,
            loaded);
        load();
        request_item.request();
    },[]);
    const do_login = React.useCallback(()=>{
        // url,token,headers,body,funcs...
        const body = loginform_data();
        const request_item  = new PostRequestByForm(
            "http://localhost:8000/token",
            null,null,{},body,
            suc_func,
            err_func,
            loaded);
        load();
        request_item.request();
    },[]);

    // view
    const login_view = (message)=>{
        // login form
        const make_attr = (name)=>{return{
            name:name+"：",className:"login_"+name,
            dbkey:"",value:"",maxLength:20}}
        const username_attr = make_attr("username");
        const password_attr = make_attr("password");
        const send_attr = {
            name:"send",className:"send_login",
            onClick:do_login}
        return (
        <div className="login_form">
        <div className="login_form" id="login_form">
            <div><InputText {...username_attr}/></div>
            <div><InputPassword {...password_attr}/></div>
            <div><InputButton {...send_attr}/></div>
            <div>{state.message}</div>
        </div>
        </div>);
    }
    const logined_view = (token)=>{
        const View = props.view;
        return (
            <LoginContext token={token} do_logout={set_logout} >
                <View/>
            </LoginContext>);
    }
    
    let content = null;
    if( state.token.length > 0 ){
        content = logined_view(state.token)
    }else{
        content = login_view(state.message);
    }    
    return (<>
        <LoadCover ref={load_ref}/>
        {content}
    </>);
}

var menus = [
    {
        title         : "class_settings",
        state_name    : "class_settings_id",
        use_subtitle  : true,
        default_state : "",
        load_action   : (data)=>{
            return new LoadAction({
                    view:AppedableClassListView,
                    url:"http://localhost:8000/class_settings_list",
                    inheritprops:data
                })
        }
    },{
        title         : "classifier",
        state_name    : "data_id",
        use_subtitle  : true,
        default_state : 1,
        load_action   : (data)=>{
            return new ClassifierLoadAction({
                    data_url  :"http://localhost:8000/data",
                    class_url :"http://localhost:8000/classes",
                    nav_url   :"http://localhost:8000/nav",
                    info_url  :"http://localhost:8000/info",
                    inheritprops:data
                })
        }
    },
];
var admin_menu = [
    {
        title         : "pagine view",
        state_name    : "page",
        use_subtitle  : true,
        default_state : "",
        load_action   : (data)=>{
            return new LoadAction({
                    view:AppendablePagingListView,
                    url:"http://localhost:8000/page_parameters",
                    inheritprops:data
                })
        },
    }
];

// TODO
// 相互作用するSeparateComponentに分離して扱いたい
// デザインを呼び出し側から設定して下位で相互に依存する入力を持ったViewを生成する
export function PageController(props){
    
    // pager menu state
    const [append_menus,setAppendMenus ] = useState([]);
    React.useEffect(()=>{
        const loader = new LoadDatas({
            url:"http://localhost:8000/page_parameters",
            response:(datas)=>{
                const ret = [];
                for(let i = -1; ++i < datas.length;){
                    const data = datas[i];
                    if( !data["enable"] ){ continue }
                    const page_param = JSON.parse(data["data"]);
                    const menu_param = page_param["menu"];
                    const view_param = page_param["view"];
                    const pp_key     = view_param["preandpost_process"];
                    const pp_process = prepost_process[pp_key];
                    view_param["preandpost_process"] = undefined;
                    const set_param = {...menu_param};
                    if( menu_param["ref_type"] === "load" ){
                        set_param["load_action"] = (data)=>{
                            return new LoadAction({
                                // force update to AppendableList2
                                view:(p)=><AppendableList2 {...p}/>,
                                // view:AppendableList2,
                                url:menu_param["ref_path"],
                                inheritprops:data,
                                ...pp_process,
                                ...view_param});
                        }
                    }else if( menu_param["ref_type"] === "local" ){
                        // set_param["render_action"] = 
                        // load_info(menu_param["ref_path"])
                    }else{
                        // pass
                    }
                    ret.push(set_param);
                }
                setAppendMenus(ret);
            }
        });
        loader.send_request();
    },[]);
    
    // menu state
    const [ menu_state,setMenustate ] = useState(load_info("selected"))
    function updatestate(key,val){
        menu_state[key] = val;
        setMenustate({...menu_state})
        save_info("selected",menu_state)
    }
    // stop consecutive clicks
    const [ selected_state,setSelectedState ] = useState("first_page");
    const selected = (state_name)=>{
        const ret = selected_state === state_name;
        setSelectedState(state_name);
        return ret;
    }
    // view
    // reducerのstateでcontextのrenderが発生しなかった
    const [view,setView] = React.useState(<div>first page</div>)
    const load_ref = React.useRef();
    const updateView = React.useCallback((action)=>{
        if( action.type === "load" ){
            if( !load_ref.current.load() ){ return }
            action.load_action.send_request();
        }else if( action.type === "loaded" ){
            if( !load_ref.current.loaded() ){ return }
            // TODO
            //   AppendableList2 update error
            //     layer → data_settings_list
            //       left to view of the layer
            setView(action.view);
        }else if( action.type === "paste" ){
            load_ref.current.loaded();
            setView(action.view);
        }
    },[]);
    
    const setview  = updateView;
    const getstate = ()=>menu_state;
    const updater  = updatestate;
    
    // TODO
    //   adding db pager
    return (
    <MenuContext
            setview={setview}
            getstate={getstate}
            updater={updater}
            selected={selected}>
        <Menu menus={[...menus,...append_menus,...admin_menu]}/>
        <div className="main" id="main_view">
            <LoadCover ref={load_ref} loaded={true}/>
            {view}
        </div>
    </MenuContext>);
}
