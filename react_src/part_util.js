import React,{
    TransitionEvent,
    createContext,useContext,
    useState,useReducer,useEffect} from 'react';
import {choice_items,event_keys,compare_dict,generate_uuidv4,
    check_limit,remove_cookie,copy_dict,dict_keycorrect,
    array_make,dict_make,conv_types_detail,data_types,get_dictvalue,
    check_type,is_string,is_function,is_object,is_array,new_address,
    array2dict,getCssStyle,getTextWidth} from './util.js';
    
import {
    set_page_values,
} from './page_util.js'
import {
    InputNumber,
    InputText,
    InputTextArea,
    InputPassword,
    InputButton,
    CheckBox,
    RadioButton,
    RadioButtonNone,
    Pin,
    LabelDiv,
    Option,
    OptionGroup,
    Select,
} from './parts.js'

import {
    DummySpanPanel as DummyPanel,
    ActiveSpanPanel as ActivePanel,
} from './view_parts.js'

var _global = window;

export const Appender = ({
        name    : name,
        label   : label,
        datas   : datas,
        draft   : draft,
        options : {
            appendable = false, // 追加可能な
            deletable  = false, // 削除可能な
            changeable = false, // 変更可能な(編集開始可能な)
            sortable   = false, // 並替可能な
        },
        editable = false,
        hidden  = false,
        liftState,
        ...other_props})=>{
    // 値選択済みの場合
    const selected = datas !== undefined && datas !== null;
    // 選択はdraftで返す
    const setState    = liftState;
    const deleteState = ()=>liftState(null)
    
    // 追加するelm
    const appendview = (<AppendValue
        add_func={setState}
        {...other_props}
        {...{options : {
            appendable,
            deletable ,
            changeable,
            sortable  ,
        }}}
    />);
    // 再選択可能にするelm
    const deleteview = (d)=>(<DeleteButton {...other_props}{...d}/>);
    const props = {
        name:name,
        // label:"",
        format_key:name+".row",
        datas:datas,
        draft:draft,
        liftState:setState,
        editable:editable,
        ...other_props
    }
    const del_props = {
        onClick:deleteState
    }
    
    let Panel = DummyPanel;
    if( other_props["active_panel"] ){
        Panel = (p)=><ActivePanel default_open={true}{...p}/>;
        // Panel = (p)=><ActivePanel default_open={false}{...p}/>;
    }
    
    const className = hidden?"hidden":"";
    
    // need top labels
    return (<span className={className}>
        { selected && editable && deletable && deleteview(del_props)}
        { selected && <ExpandPattern {...props}/>}
        {!selected && <Panel name={label}>
            {editable && appendable && appendview}
            {!editable && <>undefined</>}
        </Panel>}
    </span>);    
}

const clip_switch = {
    true:{
        key :"groups",
        type:{
            value:{
                numeric: 0,
                string : "",
                bool   : false,
            },
            container:{
                array  : [],
                object : {},
            },
        }
    },
    false:{
        key :"group",
        type:{
            numeric: 0,
            string : "",
            bool   : false,
            array  : [],
            object : {},
        },
    }
}

export const Selector = ({
        name    : name,
        label   : label = undefined,
        liftState,
        base_types=undefined,
        group_clip=true,
        hidden = false,
        ...props})=>{
    
    const clip_view = {
        true  : ExpandSelectGroupOptions,
        false : ExpandSelectOptions,
    }
    const clip = clip_switch[!!group_clip];
    const View = clip_view[!!group_clip];
    const key  = clip["key"];
    const select_props = {...props}
    select_props["liftState"] = liftState;
    select_props[key]         = base_types;
    
    const className = hidden?"hidden":"";
    
    return (<>
        <label className={className}>
            {label || name}
        </label>
        <View {...select_props}/>
    </>);
}

export const SimpleSelector = ({
        base_types=[],
        group_clip=undefined,
        ...props})=>{
    const base_types2 = array2dict(base_types);
    return <Selector
        base_types={base_types2}
        group_clip={false}
        {...props}/>
}

const TypeSelector = ({
        liftState,
        base_types=undefined,
        template_types={},
        group_clip=true,
        ...props})=>{
    
    const clip_view = {
        true  : ExpandSelectGroupOptions,
        false : ExpandSelectOptions,
    }
    const clip = clip_switch[!!group_clip];
    const View = clip_view[!!group_clip];
    const key  = clip["key"];
    base_types = base_types?base_types:copy_dict(clip["type"]);
    if( Object.keys(template_types).length > 0 ){
        if( group_clip ){
            template_types = {"template":template_types}
        }
        base_types = Object.assign(
            copy_dict(template_types),
            base_types);
    }
    const select_props = {...props}
    select_props["liftState"] = liftState;
    select_props[key]         = base_types;
    
    return (<>
        <label>{"type value"}</label>
        <View {...select_props}/>
    </>);
}

// TODO set append default
function AppendKeyValue({
            add_func,
            key_list=undefined,
            append_default=undefined,
            liftState=undefined,
            ...props
        }){

    const refKey   = React.useRef();
    const refType  = React.useRef(append_default);
    const liftKey  = (value)=>{ refKey.current  = value; }
    const liftType = (value)=>{ refType.current = value; }
    
    const changeable = {
        editable:true,
        options:{changeable:true}
    }
    
    // keyの入力、valueの選択
    // 既存のkey checkなどは上で実施したい
    // 入力式、外部からリストを与える場合は選択式にする
    // key list
    const key_val = <TextContent liftState={liftKey}
        {...changeable} name="new key"/>
    // 選択式、外部からリストを与える場合も考慮する
    // TODO
    //   type over write
    //     adding none key and empty parent value
    //     over write primitive value
    //   append default
    //     append to default value only
    //   template list
    //     append type selector lists
    //   formatsの仕様整備
    //     現状append_defaultの扱いが矛盾があり仕様が煩雑である
    //     pagerとして運用するなら挙動を統一して単純化が必要
    //     append_defaultの型指定に困っている
    //       null、undefinedの無指定型を作る
    let   type_val = <TypeSelector
        liftState={liftType}{...changeable}{...props}/>
    if( append_default !== undefined
            && append_default !== null ){
        type_val = "";
    }
    // 確定のAddButton
    const add_func2 = ()=>{
        const key   = refKey.current;
        const value = refType.current;
        if( key   === undefined || key   === null ){ return }
        if( key   === "" ){ return }
        if( value === undefined || value === null ){ return }
        add_func(key,copy_dict(value));
    }
    const add_props = {
        onClick   : add_func2,
        name      : "add",
        className : "add_button",
        disabled  : false,
    }
    const addbutton = <InputButton {...add_props}/>
    return (<>{addbutton}{key_val}{type_val}</>);
}

// TODO set append default
function AppendValue({add_func,append_default=undefined,...props}){
    
    const refType  = React.useRef(append_default);
    const liftType = (value)=>{ refType.current = value; }
    
    // 選択式、外部からリストを与える場合も考慮する
    const changeable = {
        editable:true,
        options:{changeable:true}
    }
    // TODO
    //   append default
    //     append to default value only
    //   template list
    //     append type selector lists
    
    let type_val = <TypeSelector
        liftState={liftType}{...changeable}{...props}/>
    if( append_default !== undefined
            && append_default !== null ){
        type_val = "";
    }
    
    // 確定のAddButton
    const add_func2 = React.useCallback(()=>{
        const value = refType.current;
        if( value === undefined || value === null ){ return }
        add_func(value);
    },[add_func]);
    const add_props = {
        onClick   : add_func2,
        name      : "add",
        className : "add_button",
        disabled  : false,
    }
    const addbutton = <InputButton {...add_props}/>
    return (<>{addbutton}{type_val}</>);
}

function DeleteButton(props){
    const delete_props = {
        onClick   : props.onClick,
        name      : "×",
        className : "delete_button",
        disabled  : false,
    }
    return (<InputButton {...delete_props}/>);
}
function ChangeButton(props){
    const copy_props = {
        onClick   : props.onClickCopy,
        name      : "Copy",
        className : "copy_button",
        disabled  : false,
    }
    const edit_props = {
        onClick   : props.onClickEdit,
        name      : "Edit",
        className : "edit_button",
        disabled  : false,
    }
    const save_props = {
        onClick   : props.onClickSave,
        name      : "Save",
        className : "save_button",
        disabled  : false,
    }
    const discard_props = {
        onClick   : props.onClickDiscard,
        name      : "Discard",
        className : "discard_button",
        disabled  : false,
    }
    
    let group1_style = {
        marginLeft   : "10px",
        marginRight  : "10px",
        marginTop    : "0px",
        marginButtom : "0px",
    }
    let group2_style = {
        display       : "flex",
        flexDirection : "column",
    }
    if( props.editable ){
        group1_style = {display:"none"}
    }else{
        group2_style = {display:"none"}
    }
    
    return (<span className="change_buttons">
        <div name="group1" style={group1_style}>
            <InputButton {...edit_props}/>
            <InputButton {...copy_props}/>
        </div>
        <div name="group2" style={group2_style}>
            <InputButton {...save_props}/>
            <InputButton {...discard_props}/>
        </div>
    </span>);
    // return (<span className="change_buttons">
    //     <span name="group1" style={group1_style}>
    //         <InputButton {...edit_props}/>
    //     </span>
    //     <div name="group2" style={group2_style}>
    //         <InputButton {...save_props}/>
    //         <InputButton {...discard_props}/>
    //     </div>
    // </span>);
}

// TODO
//   入力propについてまとめる
//   再入力するpropとそのまま渡すprop
//   それぞれのpropをどこで使うか
//     formatsとoptionsをnameで再配布する為にデザインの修正が必要
const ArrayContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        draft   : draft,
        options : {
            appendable = false, // 追加可能な
            deletable  = false, // 削除可能な
            changeable = false, // 変更可能な(編集開始可能な)
            sortable   = false, // 並替可能な
        },
        editable = false,
        hidden  = false,
        liftState,
        ...other_props})=>{
    
    // 自作のexpanderからReactComponentの再起処理に変更する
    const setStateNewValue = (value)=>{
        liftState(draft.concat([value]));
    }
    
    const setStateByID = (id,value)=>{
        draft[id] = value
        liftState(draft);
    }
    
    // TODO deleted array id , re distribution
    const deleteStateByID = (id)=>{
        draft.splice(id,1)
        liftState(draft);
    }
        
    const appendview = (<AppendValue
        add_func={setStateNewValue}
        {...other_props}
        {...{options : {
            appendable,
            deletable ,
            changeable,
            sortable  ,
        }}}
    />);
    const deleteview = (d)=>(<DeleteButton {...other_props}{...d}/>);
    
    const outputs = [];
    for( let i = -1; ++i < datas.length; ){
        const props = {
            name:i,
            label:"",
            format_key:name+".row",
            datas:datas[i],
            draft:draft && draft[i],
            liftState:setStateByID.bind(null,i),
            editable:editable,
            ...other_props
        }
        const del_props = {
            onClick:deleteStateByID.bind(null,i)
        }
        
        outputs.push(<div key={i}>
            {editable && deletable && deleteview(del_props)}
            <ExpandPattern {...props}/>
        </div>);
    }
    
    const empty_outputs = outputs.length === 0;
    
    let Panel = DummyPanel;
    if( other_props["active_panel"] ){
        Panel = (p)=><ActivePanel default_open={true}{...p}/>;
        // Panel = (p)=><ActivePanel default_open={false}{...p}/>;
    }
    
    const className = "arrayhead"+(hidden?" hidden":"");
    
    // need top labels
    return (<span className={className}>
        <Panel name={label}>
            {editable && appendable && appendview}
            {outputs}
            {empty_outputs && <>empty array</>}
        </Panel>
    </span>);
}
const DictContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        draft   : draft,
        options : {
            appendable = false, // 追加可能な
            deletable  = false, // 削除可能な
            changeable = false, // 変更可能な(編集開始可能な)
            sortable   = false, // 並替可能な
            ...dict_option
        },
        editable   = false,
        hidden    = false,
        is_row     = false,
        liftState,
        ...other_props})=>{
    
    const setStateNewValue = (key,value)=>{
        if( key in draft ){ return }
        draft[key] = value;
        liftState(draft);
    }
    const setStateBindKey = (key,value)=>{
        draft[key] = value;
        liftState(draft);
    }
    const deleteStateByKey = (key)=>{
        delete draft[key];
        liftState(draft);
    }
    
    const appendview = (<AppendKeyValue
        add_func={setStateNewValue}
        {...other_props}
        {...{options : {
            appendable,
            deletable ,
            changeable,
            sortable  ,
            ...dict_option
        }}}
    />);
    const deleteview = (d)=>(<DeleteButton {...dict_option}{...other_props}{...d}/>);
    
    let   key_width = 0.0;
    const font    = getCssStyle(document.body,"font");
    const keys    = Object.keys(datas);
    const outputs = [];
    for( let i = -1; ++i < keys.length; ){
        const key    = keys[i];
        key_width = Math.max(key_width,getTextWidth(key,font));
        const props  = {
            name :key,
            datas:datas[key],
            draft:draft && draft[key],
            liftState:setStateBindKey.bind(null,key),
            editable:editable,
            format_key:name+".value",
            ...other_props
        }
        const del_props = {
            onClick:deleteStateByKey.bind(null,key)
        }
        
        // need column labels
        outputs.push(<div key={i}>
            {editable && deletable && deleteview(del_props)}
            <ExpandPattern {...props}/>
        </div>);
    }
    
    const empty_outputs = Object.keys(outputs).length === 0;
    
    let Panel = DummyPanel;
    if( other_props["active_panel"] ){
        Panel = (p)=><ActivePanel default_open={true}{...p}/>;
        // Panel = (p)=><ActivePanel default_open={false}{...p}/>;
    }
    if( is_row && label==="" ){
        Panel = ({children})=><>{children}</>;
    }
    
    // react.useid default format :r[0-9]+:
    // above format css not work
    // because ":" is css syntax key
    const className    = "dicthead"+(hidden?" hidden":"");
    const rowClassName = is_row?"row":"";
    const id = React.useId().slice(1,-1); 
    const style_text = ""
        +"#"+id+":not(.row) > div > label:not(:empty),"
        +"#"+id+":not(.row) > div > span > label:not(:empty)"
        +"{"
        +"    min-width    : "+key_width+"px;"
        +"}"
        +"#"+id+" > div > label:not(:empty,.hidden),"
        +"#"+id+" > div > span > label:not(:empty,.hidden)"
        +"{"
        +"    display      : inline-block;"
        +"    margin-left  : 2px;"
        +"    margin-right : 2px;"
        +"}"
        +"#"+id+".row,"
        +"#"+id+".row > div"
        +"{"
        +"    display : inline;"
        +"}"
    const keyalign = <style>{style_text}</style>
    return (<span className={className}>
        <Panel name={label}>
            {keyalign}
            {editable && appendable && appendview}
            <div id={id}className={rowClassName}>{outputs}</div>
            {empty_outputs && <>empty object</>}
        </Panel>
    </span>);
}
const NumericContent = ({
        name,
        label,
        datas,
        editable=false,
        hidden =false,
        options:{changeable=false,...options},
        liftState,
        size = undefined,
        maxLength = undefined,
        style = undefined,
        use_lengthstyle = false,
        ...other_props})=>{
    
    const props = {
        disabled  : !(editable&&changeable),
        hidden   : hidden,
        value     : datas,
        size      : size || maxLength,
        style     : style,
        name      : name,
        label     : label,
        onBlur    : (e)=>{
            liftState(e.target.value*1)
        },
        use_lengthstyle : use_lengthstyle,
    }
    return (<InputNumber {...props}/>);
}
const ErrorContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        editable=false,
        hidden =false,
        options:{changeable=false,...options},
        liftState,
        ...other_props})=>{
            
    return (<LabelDiv hidden={hidden}value={datas}/>);
}
const TextAreaContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        editable=false,
        hidden =false,
        options:{changeable=false,...options},
        liftState,
        ...other_props})=>{
    
    const props = {
        disabled  : !(editable&&changeable),
        hidden   : hidden,
        value     : datas,
        name      : name,
        label     : label,
        onBlur    : (e)=>{
            liftState(e.target.value)
        }
    }
    return (<InputTextArea {...props}/>)
}
const TextContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        editable=false,
        hidden =false,
        options:{changeable=false,...options},
        liftState,
        style = undefined,
        size = undefined,
        maxLength = undefined,
        use_lengthstyle = false,
        ...other_props})=>{
    
    
    const props = {
        disabled  : !(editable&&changeable),
        hidden   : hidden,
        value     : datas,
        size      : size || maxLength,
        name      : name,
        stiye     : style,
        label     : label,
        onBlur    : (e)=>{
            liftState(e.target.value)
        },
        use_lengthstyle : use_lengthstyle,
    }
    
    return (<InputText {...props}/>)
}
const BoolContent = ({
        name    : name,
        label   : label,
        datas   : datas,
        editable=false,
        hidden =false,
        options:{changeable=false,...options},
        liftState,
        checkbox_right=false,
        ...other_props})=>{
    
    const props = {
        disabled  : !(editable&&changeable),
        hidden   : hidden,
        value     : !!datas,
        name      : name,
        label     : label,
        onClick   : (e)=>{
            liftState(e.target.checked)
        },
        checkbox_right:checkbox_right
    }
    return (<CheckBox {...props}/>)
}
const DefaultContent = TextContent;
const NullContent    = ErrorContent;

const expand_funcs = {
    "array"  : ArrayContent,
    "object" : DictContent,
    "numeric": NumericContent,
    "error"  : ErrorContent,
    "null"   : Appender,
    "strings": TextAreaContent,
    "string" : TextContent,
    "bool"   : BoolContent,
    "other"  : DefaultContent,
};

const head_key = "/"

const get_formatkeys = (
        format_key,
        name,
        name_chaine = "",
        formatkey_chaine = "")=>{
    const format_keys = [];
    //////////////// use chaines ////////////////
    // format keyがある部分はそれを優先する
    // 接頭辞に関して、chaineのheadにhead_keyを付与する
    const hierarchy1     = [];
    const hierarchy2     = [];
    const name_hierarchy = name_chaine.split(">");
    const formatkey_hierarchy = formatkey_chaine.split(">");
    name_hierarchy.push(name);
    formatkey_hierarchy.push(format_key);
    const len = Math.min(name_hierarchy.length,
        formatkey_hierarchy.length);
    for( let i = len; --i >= 0; ){
        let   nh = name_hierarchy[i];
        let   fh = formatkey_hierarchy[i];
        nh = nh?nh:"";
        fh = fh?fh:"";
        const kh = fh!==""?fh:nh;
        if( kh.search(".row$") !== -1 ){
            nh = kh;
        }
        hierarchy1.unshift(kh);
        hierarchy2.unshift(nh);
        format_keys.push(hierarchy1.join(">"));
        format_keys.push(hierarchy2.join(">"));
    }
    //////////////// use chaines ////////////////
    
    if( !!format_key && format_key !== "" ){
        format_keys.push(format_key);
        if( format_key.search("row$") === -1 ){
            format_keys.push(name);
        }
    }else{
        format_keys.push(name)
    }
    return format_keys;
}

// Stateによる画面更新に期待して動作させているが
// stateの更新が遅いようなので
// state_contextを利用する
export const PatternRoot = ({
        name = "root",
        datas,
        // formats = { default:format, keyname:format , keyname:format,... }
        // format  = { view:～,options:～,append_default:～ }
        formats = {},
        default_edit  = false,
        new_row       = false,
        save_state    = undefined,
        discard_state = undefined,
        copy_state    = undefined,
        hide_name     = false,
        ...props})=>{
    
    const root_name = name;
    
    if( datas !== undefined && datas !== null ){
        // pass
    }else if( formats[root_name] === undefined ){
        // pass
    }else if( formats[root_name]["append_default"] === undefined ){
        // pass
    }else{
        datas = formats[root_name]["append_default"];
    }
    
    const [state,setState] = useState(copy_dict(datas))
    const [draft,setDraft] = useState(copy_dict(datas))
    const [edit ,setEdit]  = useState("")
    
    const action_dict = React.useMemo(()=>{
        return {
            "get_edit":(key)=>edit,
            "set_edit":(key)=>setEdit(key),
            "save"    :(key)=>{
                const new_state = copy_dict(draft);
                update_undefined(new_state);
                setState(new_state);
                setEdit("");
                if( save_state !== undefined ){
                    save_state(new_state);
                }
            },
            "discard" :(key)=>{
                setDraft(copy_dict(state));
                setEdit("");
                if( discard_state !== undefined ){
                    discard_state(state);
                }
            },
            "set_copy":(key)=>{
                const new_state = copy_dict(state);
                update_undefined(new_state);
                copy_state(new_state);
            },
            "set"     :(val)=>setDraft(new_address(val))
        }
    },[state,draft,edit,save_state,discard_state]);
    
    const controller = React.useCallback(({type,key=""})=>{
        const callable = action_dict[type];
        if( !callable ){ return }
        return callable(key);
    },[action_dict]);
    
    const liftState2 = React.useCallback((value)=>{
        controller({type:"set",key:value})
    },[controller]);
    
    const get_formats = React.useCallback((names,data,new_row=false)=>{
        const type     = check_type(data);
        const view     = expand_funcs[type];
        let   response = {
            view:view,
            append_default:undefined,
            append_props:{},
            options:{
                appendable : false, // 追加可能な
                deletable  : false, // 削除可能な
                changeable : false, // 変更可能な
                sortable   : false, // 並替可能な
                editbutton : false, // 編集ボタン
                appendable_newrow : false, // 新規追加時、追加可能な
                deletable_newrow  : false, // 新規追加時、削除可能な
                changeable_newrow : false, // 新規追加時、変更可能な
            }
        }
        if( "default" in formats ){
            let def = formats["default"];
            if( is_function(def) ){
                def = def(data);
            }
            if( "view" in def && def["view"] === "" ){
                delete def["view"];
            }
            response = Object.assign(response,def);
        }
        for( let i = -1; ++i < names.length; ){
            const name = names[i];
            if( name in formats ){
                const format = formats[name];
                if( "view" in format && format["view"] === "" ){
                    delete format["view"];
                }
                response = Object.assign(response,format);
            }
        }
        if( ( data === undefined ||
                data === null ) &&
                response["view"] === view &&
                response["append_default"] !== undefined ){
            const type = check_type(response["append_default"]);
            const view = expand_funcs[type];
            response["view"] = view;
        }else if( !is_string(response["view"]) ){
            // pass
        }else if( response["view"] in _global ){
            response["view"] = _global[response["view"]];
        }else if( response["view"].search("\\(") !== -1 ){
            console.alert("get format error name view : ",names.join(","),
                " data : ",JSON.stringify(data),
                " view : ",response["view"]);
        }
        const view_name = response["view"];
        response["view"] = eval(view_name);
        if( !is_string(view_name) ){
            // pass
        }else if( !"name" in response["view"] ){
            console.alert("get format error name : ",names.join(","),
                           " data : ",JSON.stringify(data));
        }else if( view_name !== response["view"].name ){
            console.alert("get format error name : ",names.join(","),
                           " data : ",JSON.stringify(data));
        }
        
        if( new_row ){
            const options = {...response["options"]};
            options["appendable"] = !!(options["appendable"]||options["appendable_newrow"]);
            options["deletable"]  = !!(options["deletable"] ||options["deletable_newrow"]);
            options["changeable"] = !!(options["changeable"]||options["changeable_newrow"]);
            response["options"]   = options;
        }
        
        return response;
    },[formats]);
    
    const update_undefined = (datas,
                               name=root_name,
                               format_key=root_name,
                               name_chaine=head_key,
                               formatkey_chaine=head_key)=>{
        const keys = Object.keys(datas);
        for( let i = -1; ++i < keys.length; ) {
            const key  = keys[i];
            const data = datas[key];
            const type = typeof data;
            if( data === null || data === undefined ){
                const format_keys  = get_formatkeys(format_key,key);
                const format       = get_formats(format_keys,data)
                const default_data = format["append_default"];
                datas[key] = default_data;
                if( datas[key] === undefined ){
                    datas[key] = null;
                }
            }else if( is_object(data) ){
                const format_key = key+(is_array(data)?".row":".value");
                update_undefined(
                    data,key,format_key,name_chaine+">"+key,
                    formatkey_chaine+">"+format_key);
            }
        }
    }
    
    return (<ExpandPattern
        name             = {root_name}
        name_chaine      = {head_key}
        formatkey_chaine = {head_key}
        datas            = {state}
        draft            = {draft}
        edit_key         = {edit}
        get_formats      = {get_formats}
        editable         = {false}
        liftState        = {liftState2}
        controller       = {controller}
        default_edit     = {default_edit}
        new_row          = {new_row}
        hide_name        = {hide_name}
        {...props}
    />);
}

// ExpandPatternに名前を変更して実装を修正する
// 分割表示処理、あるいは下位レイヤーが編集可能かを示す
function ExpandPattern({
        name,
        name_chaine,
        label      = undefined,
        format_key = undefined,
        formatkey_chaine = "",
        datas,
        draft,
        options=undefined,
        edit_key,
        get_formats,
        controller,
        editable=false,
        default_edit=false,
        hide_name=false,
        liftState,
        new_row = false,
        base_types=undefined, // adding append props for selector
        group_clip=undefined, // adding append props for selector
        active_panel=false,
        ...props}){
    
    label = label!==undefined?label:name;
    const format_keys = get_formatkeys(
        format_key,name,name_chaine,formatkey_chaine);
    const format = get_formats(format_keys,datas,new_row);
    if( ( datas === undefined 
            || datas === null )
            && format["append_default"] !== undefined ){
        datas = copy_dict(format["append_default"]);
        draft = copy_dict(format["append_default"]);
    }
    format_key = format_key===undefined?name:format_key;
    
    const use_props = {...props}
    Object.assign(use_props,{
        name             : name,
        label            : label,
        name_chaine      : name_chaine+">"+name,
        formatkey_chaine : formatkey_chaine+">"+format_key,
        options          : format["options"],
        append_default   : format["append_default"],
        get_formats      : get_formats,
        draft            : draft,
        edit_key         : edit_key,
        controller       : controller,
        liftState        : liftState,
        new_row          : new_row,
        ...format["append_props"],
    });
    
    const changeable = !!use_props.options.changeable;
    const editbutton = !!use_props.options.editbutton;
    const to_edit    = edit_key === use_props.name_chaine;
    
    const View   = format["view"];
    const ChgBtn = (<ChangeButton{...{
        editable       : to_edit||default_edit,
        onClickCopy    : controller.bind(null,{type:"set_copy"}),
        onClickEdit    : controller.bind(null,{type:"set_edit",key:use_props.name_chaine}),
        onClickSave    : controller.bind(null,{type:"save"}),
        onClickDiscard : controller.bind(null,{type:"discard"}),
    }}/>);
    
    const copy_props = {
        datas:datas,
        editable:editable
    }
    const showview = <View {...use_props}{...copy_props}/>;
    
    // 編集開始点を区切る
    if( to_edit ){
        const splitstyle = {
            display       : "flex",
            flexDirection : "row"
        }
        const edit_props ={
            datas:draft,
            editable:true
        }
        
        // edit mode side split
        return (<div style={splitstyle}>
            <div>{showview}</div>
            <div>{ChgBtn}</div>
            <div><View {...use_props}{...edit_props}/></div>
        </div>);
    }else if( default_edit ){
        const splitstyle = {
            display       : "flex",
            flexDirection : "row"
        }
        const edit_props ={
            datas:draft,
            editable:true
        }
        return (<div style={splitstyle}>
            <div>{ChgBtn}</div>
            <div><View {...use_props}{...edit_props}/></div>
        </div>);
    }else{

        if( edit_key !== "" ){
            // edit mode
            return showview;
        }else{
            // non edit
            // edit button left / name label right
            return (<span>{changeable && editbutton && ChgBtn}{showview}</span>);
        }
    }
}

export const ExpandSelectOptions = ({
            group={},
            liftState,
            datas=undefined,
            editable=false,
            options:{changeable=false,...option_props},
            disabled=undefined,
            use_none=true,
            ...props
        })=>{
    
    const values     = [];
    const options    = [];
    
    if( use_none ){
        const option_props = {
            key   : -1,
            label : "",
            value : 0,
        }
        options.push(<Option {...option_props}/>)
        values.push(undefined);
    }
    
    const value_keys = Object.keys(group);
    for( let i = -1; ++i < value_keys.length; ){
        const label = value_keys[i];
        const value = group[label];
        const option_props = {
            key:i,
            label:label,
            value:values.length
        }
        options.push(<Option {...option_props}/>);
        values.push(value)
    }
    
    const onChange = React.useCallback((e)=>{
        const select_id    = e.target.selectedIndex||0;
        const selected     = e.target[select_id];
        const select_value = selected.value;
        // lift state on change action
        liftState(values[select_value])
    },[values]);
    
    const select_props = {...props}
    select_props["selectedIndex"] = values.indexOf(datas);
    select_props["onChange"]      = onChange;
    if( disabled !== undefined ){
        select_props["disabled"] = !!disabled;
    }else{
        select_props["disabled"] = !(editable&&changeable);
    }
    
    return (
        <Select {...select_props}>
            {options}
        </Select>);
}

export const ExpandSelectGroupOptions = ({
            groups={},
            datas=undefined,
            liftState,
            editable=false,
            options:{changeable=false,...option_props},
            disabled=undefined,
            use_none=true,
            ...props
        })=>{
    
    const values = [];
    const option_groups = [];

    if( use_none ){
        const option_props = {
            key   : -1,
            label : "",
            value : 0,
        }
        option_groups.push(<Option {...option_props}/>)
        values.push(undefined);
    }    
    
    const group_keys = Object.keys(groups);
    for( let i = -1; ++i < group_keys.length; ){
        const group_key  = group_keys[i];
        const group      = groups[group_key];
        const value_keys = Object.keys(group);
        const options    = [];
        for( let j = -1; ++j < value_keys.length; ){
            const label = value_keys[j];
            const option_props = {
                key:j,
                label:label,
                value:values.length
            }
            options.push(<Option {...option_props}/>);
            values.push(group[label])
        }
        const group_props = {
            label:group_key,
            key:i,
        }
        option_groups.push(
            <OptionGroup {...group_props}>
                {options}
            </OptionGroup>)
    }
    
    const onChange = React.useCallback((e)=>{
        const select_id    = e.target.selectedIndex||0;
        const selected     = e.target[select_id];
        const select_value = selected.value;
        // lift state on change action
        liftState(values[select_value])
    },[values]);
    
    const select_props = {...props}
    select_props["selectedIndex"] = values.indexOf(datas);
    select_props["onChange"] = onChange;
    if( disabled !== undefined ){
        select_props["disabled"] = !!disabled;
    }else{
        select_props["disabled"] = !(editable&&changeable);
    }
    
    return (
        <Select {...select_props}>
            {option_groups}
        </Select>);
}