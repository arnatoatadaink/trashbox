import React from 'react';
import {generate_uuidv4,get_funcs} from './util.js';
import {make_inputstyle_dict,make_numstyle_dict} from './page_util.js';

function showlabel({
            label:l=undefined,
            name :n=undefined,
        }){
    return l!==undefined?l:n;
}

const InputWrapp = React.forwardRef((props,ref) => {
    const ref2 = React.useRef();
    const checked = props["defaultChecked"];
    const value   = props["defaultValue"];
    
    React.useEffect(()=>{
        let target = null;
        if( ref ){
            target = ref.current;
        }else if( ref2 ){
            target = ref2.current;
        }
        if( props.type === ["text","number","password",undefined] ){
            target.value = value;
        }else if( props.type in ["radio","checkbox"] ){
            target.checked = checked;
        }
    },[value,checked]);
    
    const base_props = {...props}
    if( "className" in base_props ){
        base_props["className"] += !!base_props.hidden?" hidden":"";
    }else{
        base_props["className"] = !!base_props.hidden?" hidden":"";
    }
    
    return <input ref={ref||ref2} {...base_props}/>
});

const LabelInInput = React.forwardRef(({
            name,
            input_value,
            hidden=false,
        },ref)=>{
    const className = hidden?"hidden":"";
    return (<label className={className}>
        <InputWrapp ref={ref}{...input_value}/>{name}
    </label>);
});
const LabelInInput2 = React.forwardRef(({
            name,
            input_value,
            hidden=false,
        },ref)=>{
    const className = hidden?"hidden":"";
    const ref2  = React.useRef();
    const refcl = ()=>(ref||ref2).current.click();
    return (<>
        <label className={className} onClick={refcl}>{name}</label>
        <InputWrapp hidden={hidden} ref={ref||ref2}{...input_value}/>
    </>);
});
const LabelAndInput = React.forwardRef(({
            name,
            input_value,
            hidden=false,
        },ref)=>{
    const className = hidden?"hidden":"";
    return (<>
        <label className={className}>{name}</label>
        <InputWrapp hidden={hidden}ref={ref}{...input_value}/>
    </>);
});

export const RadioButton = React.forwardRef((props,ref)=>{
    const key     = props["dbkey"]||props["name"];
    const checked = props["value"]||props["val"];
    const input_value = {
        ...get_funcs(props),
        type           : "radio",
        style          : props["style"],
        id             : props["id"],
        name           : props["group"],
        "data-rawname" : props["rawgroup"],
        className      : props["className"],
        value          : key,
        defaultChecked : checked,
        disabled       : props["disabled"]||false,
    }
    return <LabelInInput
        name={showlabel(props)}
        input_value={input_value}
        ref={ref}
        hidden={!!props["hidden"]}
    />;
});

export const RadioButtonNone = React.forwardRef((props,ref)=>{
    const name    = showlabel(props)||"None";
    const checked = props["value"]||props["val"];
    const input_value = {
        ...get_funcs(props),
        type           : "radio",
        style          : props["style"],
        id             : props["id"],
        name           : props["group"],
        "data-rawname" : props["rawgroup"],
        className      : props["className"],
        value          : props["dbkey"]||"None",
        defaultChecked : checked,
        disabled       : props["disabled"]||false,
    }
    return <LabelInInput
        name={name}
        input_value={input_value}
        ref={ref}
        hidden={!!props["hidden"]}
    />;
});

export const CheckBox = React.forwardRef((props,ref)=>{
    const input_value = {
        ...get_funcs(props),
        type           : "checkbox",
        style          : props["style"],
        id             : props["id"],
        name           : props["dbkey"]||props["name"],
        className      : props["class"]||props["className"],
        defaultChecked : props["value"]||props["val"],
        disabled       : props["disabled"]||false,
    }
    
    let LF = LabelInInput;
    if( props["checkbox_right"] ){
        LF = LabelInInput2;
    }
    
    return <LF
        name={showlabel(props)}
        input_value={input_value}
        ref={ref}
        hidden={!!props["hidden"]}
    />;
});

const INPUTMARGIN = 3;
function maxlength_color(e){
    const maxlen = e.target.getAttribute("maxlength");
    const key = e.target.value.length > maxlen - INPUTMARGIN;
    e.target.style.backgroundColor = key?"#FDD":"";
}

function get_length_props(props){
    const maxlength = (props.size||props.maxLength)+INPUTMARGIN;
    if( isNaN(maxlength) ){ return {} }
    return {
        "data-rawmaxlength" : maxlength,
        maxLength           : maxlength,
        onInput             : maxlength_color,
    }
}

function get_lengthstyle(
        type,style={},length_props={},use_lengthstyle=false){
    if( !use_lengthstyle ){ return style }
    if( !"maxLength" in length_props ){ return style; }
    if( "width" in length_props ){ return style; }
    
    let   addstyle = {};
    const length   = length_props["maxLength"];
    if( type !== "number" ){
        addstyle = make_inputstyle_dict(length);
    }else{
        addstyle = make_numstyle_dict(length);
    }
    return {...style,...addstyle};
}

function get_input_props({
        style={},
        use_lengthstyle=false,
        ...props}){
    const length_props = get_length_props(props);
    const use_style    = get_lengthstyle(
        props.type,style,length_props,use_lengthstyle);
    // const use_style = props.style;
    return {
        ...get_funcs(props),
        type         : props.type,
        style        : use_style,
        id           : props.id,
        name         : props.dbkey||props.name,
        className    : props["class"]||props.className,
        defaultValue : props.value||props.val,
        disabled     : props.disabled||false,
        ...length_props,
    }
}

const InputBase = React.forwardRef((props,ref)=>{
    const props2 = {
        name:showlabel(props),
        input_value:get_input_props(props),
        ref:ref,
        hidden:!!props.hidden,
    };
    return <LabelAndInput {...props2}/>
});

export const InputNumber = React.forwardRef(
    (props,ref)=>(<InputBase ref={ref} {...props} type="number"/>)
)

export const InputText = React.forwardRef(
    (props,ref)=>(<InputBase ref={ref} {...props} type="text"/>)
)

export const InputPassword = React.forwardRef(
    (props,ref)=>(<InputBase ref={ref} {...props} type="password"/>)
)

export const InputButton = React.forwardRef((props,ref)=>{
    const input_props = {
        ...get_funcs(props),
        type      : "button",
        style     : props["style"],
        className : props["class"]||props["className"],
        value     : showlabel(props),
        disabled  : props["disabled"]||false,
    }
    input_props["className"] += !!props.hidden?" hidden":"";
    return (<input ref={ref} {...input_props} />);
});

export const InputTextArea = React.forwardRef((props,ref)=>{
    
    const area_props = {
        ...get_funcs(props),
        // type         : props.type,
        style        : props.style,
        id           : props.id,
        name         : props.dbkey||props.name,
        className    : props["class"]||props.className,
        defaultValue : props.value||props.val,
        disabled     : props.disabled||false,
        // ...get_length_props(props),
    }
    const className = props.hidden?"hidden":"";
    
    return (<>
        <div className={className}>
            {showlabel(props)}</div>
        <div className={className}>
            <textarea ref={ref}{...area_props}/></div>
    </>);
});

export const LabelDiv = React.forwardRef((props,ref)=>{
    const className = props.hidden?"hidden":"";
    return (<div 
        className={className}
        ref={ref}>
            {props.value}
    </div>);
});

export const Option = ({value=undefined,label=undefined})=>{
    if( value === undefined ){ value = label }
    if( label === undefined ){ label = value }
    return (<option value={value}>{label}</option>);
}
export const OptionGroup = ({label,children})=>{
    return (<optgroup label={label}>
        {children}</optgroup>);
}
export const Select = ({
            onChange=()=>{},
            disabled=false,
            hidden =false,
            children=[],
            selectedIndex=undefined,
        })=>{
    const ref = React.useRef();
    const select_props = {
        disabled  : disabled, // switch disabled
        onChange  : onChange,
        ref       : ref,
        className : hidden?"hidden":"",
    }
    
    // default selected
    React.useEffect(()=>{
        const target = ref.current;
        target.selectedIndex = selectedIndex;
    },[selectedIndex]);
    
    return (
        <select {...select_props}>
            {children}
        </select>);
}