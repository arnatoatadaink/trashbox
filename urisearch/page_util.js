// example
// https://stackoverflow.com/questions/15408394/how-to-copy-a-dom-node-with-event-listeners
(function() {

    const _originAddEventListener = HTMLElement.prototype.addEventListener;
    const _originRemoveEventListener = HTMLElement.prototype.removeEventListener;
    const _originCloneNode = HTMLElement.prototype.cloneNode;
    const _eventListeners = [];

    const getEventIndex = (target, targetArgs) => _eventListeners.findIndex(([elem, args]) => {
        if(elem !== target) {
            return false;
        }

        for (let i = 0; i < args.length; i++) {
            if(targetArgs[i] !== args[i]) {
                return false;
            }
        }

        return true;
    });

    const getEvents = (target) => _eventListeners.filter(([elem]) => {
        return elem === target;
    });

    const cloneEvents = (source, element, deep) => {
        for (const [_, args] of getEvents(source)) {
            _originAddEventListener.apply(element, args);
        }

        if(deep) {
            for(const i of source.childNodes.keys()) {
                const sourceNode = source.childNodes.item(i);
                if(sourceNode instanceof HTMLElement) {
                    const targetNode = element.childNodes.item(i);
                    cloneEvents(sourceNode, targetNode, deep);
                }
            }
        }
    };

    HTMLElement.prototype.addEventListener = function() {
        _eventListeners.push([this, arguments]);
        return _originAddEventListener.apply(this, arguments);
    };

    HTMLElement.prototype.removeEventListener = function() {

        const eventIndex = getEventIndex(this, arguments);

        if(eventIndex !== -1) {
            _eventListeners.splice(eventIndex, 1);
        }

        return _originRemoveEventListener.apply(this, arguments);
    };

    HTMLElement.prototype.cloneNode = function(deep) {
        const clonedNode = _originCloneNode.apply(this, arguments);
        if(clonedNode instanceof HTMLElement){
            cloneEvents(this, clonedNode, deep);
        }
        return clonedNode;
    };

})()

var _global = globalThis

function is_full(){
    // return Math.abs(window.screen.height-document.documentElement.clientHeight) < 3;
    // return Math.abs(window.screen.height-window.outerHeight) < 20;
    return ( window.screen.height
            - window.devicePixelRatio
            * document.documentElement.clientHeight ) < 60;
}

function get_elmtypes(elm){
    let type = elm.type?elm.type:"default";
    if( type === "default" ){
        const typeclasses = [
            "imitate_select",
            "imitate_list",
            "drop_lane",
            "imitate_table",
            "drop_dict",
        ];
        for( let i = -1; ++i < typeclasses.length; ){
            if( elm.classList.contains(typeclasses[i]) ){
                type = typeclasses[i];
            }
        }
    }
    return type;
}

// 多目的入力
function make_setpagevalues(){
    const setfuncs = {
        "input":{
            "default" :function(target,value){ target.value   = value; },
            "checkbox":function(target,value){ target.checked = value; },
            "text"    :function(target,value){ target.value   = value; },
            "number"  :function(target,value){ target.value   = value; },
            "radio"   :function(target,value){
                if( ""+target.value === ""+value ){
                    target.checked = true;
                    target.removeAttribute("checked");
                }else{
                    target.checked = false;
                    target.setAttribute("checked",true);
                }
            },
        },
        "textarea":{
            "default" :function(target,value){ target.value   = value; },
        },
        "select":{
            "default":function(target,value){
                const elm   = target.querySelector("option[value='"+value+"']");
                const index = elm?elm.index:0;
                target.selectedIndex = index;
            },
        },
        "table":{
            "default":table_expand,
            "imitate_select":function(target,value){
                const targets = target.querySelectorAll(".imitate_pulldown tr");
                for( let i = -1; ++i < targets.length; ){
                    const checktarget = targets[i].querySelector(".imitate_text");
                    const checktext   = checktarget.textContent;
                    if( checktext === value ){
                        // targets[i].click();
                        return;
                    }
                }
            },
        },
        "div":{
            "default"       : div_expand,
            "imitate_table" : imitatetable_expand,
            "imitate_list"  : imitatelist_expand,
            "drop_lane"     : imitatelist_expand,
            "drop_dict"     : div_expand,
        },
        "span":{
            "default"       : div_expand,
            "imitate_table" : imitatetable_expand,
            "imitate_list"  : imitatelist_expand,
            "drop_lane"     : imitatelist_expand,
            "drop_dict"     : div_expand,
        },
    };
    function set_page_value(elm,value,options){
        const setfuncstype = setfuncs[elm.localName];
        if( !setfuncstype ){ return; }
        const funckey      = get_elmtypes(elm);
        if( funckey === "button" ){ return; }
        const func         = setfuncstype[funckey]?setfuncstype[funckey]:setfuncstype["default"];
        let   key = "";
        if( elm.hasAttribute("id") ){
            key = elm.getAttribute("id");
        }else if( elm.hasAttribute("data-rawname") ){
            key = elm.getAttribute("data-rawname");
        }else if( elm.hasAttribute("name") ){
            key = elm.getAttribute("name");
        }
        if( key in value ){
            func(elm,value[key],options);
        }
    }
    function set_page_values(target,value,options){
        const setelements = document.querySelectorAll(target);
        for( let i = 0; i < setelements.length; i++ ){
            set_page_value(setelements[i],value,options);
        }
    }
    return [set_page_value,set_page_values];
}
let funcs = make_setpagevalues();
const set_page_value  = funcs[0];
const set_page_values = funcs[1];

// 多目的取得
function make_getpagevalues(){
    const getfuncs = {
        "input":{
            "default" :function(target){ return target.value; },
            "checkbox":function(target){ return target.checked; },
            "text"    :function(target){ return target.value; },
            "number"  :function(target){ return target.value * 1; },
            "radio"   :function(target){ if( target.checked ){ return target.value } },
        },
        "textarea":{
            "default" :function(target){ return target.value; },
        },
        "select":{
            "default":function(target){ return target.selectedOptions[0].value; },
        },
        "table":{
            "default":table_correct,
            "imitate_select":function(target){
                return target.querySelector(".imitate_text").textContent;
            },
        },
        "div":{
            "default"       : div_correct,
            "imitate_table" : imitatetable_correct,
            "imitate_list"  : imitatelist_correct,
            "drop_lane"     : imitatelist_correct,
            "drop_dict"     : div_correct,
        },
        "span":{
            "default"       : div_correct,
            "imitate_table" : imitatetable_correct,
            "imitate_list"  : imitatelist_correct,
            "drop_lane"     : imitatelist_correct,
            "drop_dict"     : div_correct,
        },
    };
    function get_page_value(elm){
        const getfuncstype = getfuncs[elm.localName];
        if( !getfuncstype ){ return; }
        const funckey      = get_elmtypes(elm);
        if( funckey === "button" ){ return; }
        const func         = getfuncstype[funckey]?getfuncstype[funckey]:getfuncstype["default"];
        return func(elm);
    }
    
    function get_page_value2dict(elm,argdict){
        if( !argdict ){ return; }
        const getfuncstype = getfuncs[elm.localName];
        if( !getfuncstype ){ return; }
        const funckey      = get_elmtypes(elm);
        const func         = getfuncstype[funckey]?getfuncstype[funckey]:getfuncstype["default"];
        let   key = "";
        if( elm.hasAttribute("id") ){
            key = elm.getAttribute("id");
        }else if( elm.hasAttribute("data-rawname") ){
            key = elm.getAttribute("data-rawname");
        }else if( elm.hasAttribute("name") ){
            key = elm.getAttribute("name");
        }
        if( key !== "" ){
            const value = func(elm);
            if( funckey !== "radio" || value !== undefined ){
                argdict[key] = value;
            }
        }
    }
    function get_page_values(target,argdict){
        const retdict = argdict?argdict:{};
        const getelements = document.querySelectorAll(target);
        for( let i = 0; i < getelements.length; i++ ){
            const elm = getelements[i];
            get_page_value2dict(elm,retdict);
        }
        return retdict;
    }
    return [get_page_value,get_page_value2dict,get_page_values];
}
funcs = make_getpagevalues();
const get_elm_value       = funcs[0];
const get_page_value2dict = funcs[1];
const get_page_values     = funcs[2];


//////////////// page data controller ////////////////
function table_expand(target,value){
    // valueはdict-array前提
    // targetはtable
    
}
function table_correct(target){
    // targetをdict-arrayに起こす
    // target上にあるth-tdを項目名にする
    // target上にあるtr-tdをth行数毎に1つのdictとして取り込む
}

function apply_children(action){
    function apply_children_imple(first_target,value){
        const stack = [first_target];
        while( stack.length > 0 ){
            const target = stack.pop();
            if( target.hasAttribute("name") ){
                action(target,value);
            }else{
                for( let i = target.children.length; --i >= 0; ){
                    stack.push(target.children[i]);
                }
            }
        }
    }
    return apply_children_imple;
}
    
function default_expand(target,key,value,options){
    let pattern_func = "";
    if( !!options && "pattern_funcs" in options ){
        pattern_func = options["pattern_funcs"][key];
    }else if( "pattern_funcs" in _global ){
        pattern_func = _global["pattern_funcs"][key];
    }
    // idと対応するパターン関数があれば
    if( !pattern_func ){
        pattern_func = default_pattern;
    }
    
    let patterns = [];
    patterns = pattern_func(value,options);
    for( let i = -1; ++i < patterns.length; ){
        const elm = expand_pattern(patterns[i]);
        target.appendChild(elm);
    }
}

function child_expand(target,value,options){
    // valueはdict-array前提
    // targetはdiv
    let key = "";
    key = target.getAttribute("id");
    if( !key ){
        key = target.getAttribute("name");
    }
    let expand_func = "";
    if( !!options && "expand_funcs" in options ){
        expand_func = options["expand_funcs"][key];
    }else if( "expand_funcs" in _global ){
        expand_func = _global["expand_funcs"][key];
    }
    if( !expand_func ){
        expand_func = default_expand;
    }
    expand_func(target,key,value,options);
}
    
function div_expand(target,value,options){
    if( target.children.length === 0 ){
        child_expand(target,value,options);
    }else{
        
        const set_children = apply_children(function(child,value){
            set_page_value(child,value,options)
        });
        
        if( target.hasAttribute("name")
                && !(target.getAttribute("name") in value) ){
            for( let i = -1; ++i < target.children.length; ){
                set_children(target.children[i],value);
            }
        }else{
            set_children(target,value);
        }
    }
}
function div_correct(target){
    // targetをdict-arrayに起こす
    // target上にあるname付きの項目をnameを項目名として値を取り込む
    // target上にあるchildを行数にする
    
    // 指定されたtargetのchildをたどって、name付きの項目を探し
    // localNameが取得対象の場合、それを取り込む
    const correct_children = apply_children(get_page_value2dict);
    
    // array,dictの切り替え
    // class等でarrayの制御を装飾する
    // それを確認して戻り値を決定する
    // 暫定的にarray
    if( target.classList.contains("imitate_table") ){
        const array = [];
        for( let i = -1; ++i < target.children.length;){
            const dict = {};
            correct_children(target.children[i],dict);
            if( Object.keys(dict).length > 0 ){
                array.push(dict);
            }
        }
        return array;
    }else{
        const dict = {};
        for( let i = -1; ++i < target.children.length;){
            correct_children(target.children[i],dict);
        }
        return dict;
    }
}

// name 無しのアイテムも扱いたい
// array object
// array data
// object
// data
// name無しのアイテムはarray dataのdata部分
// これを直接的に配置、収集するためにimitatetableを設計する
function imitatetable_expand(target,value_array,options){
    // checkkeys
    // key  record
    // data record
    imitatelist_expand(target,value_array,options);
}

function imitatetable_correct(target){
    // ヘッダ行
    // データ行...
    div_correct(target);
}

function imitatelist_expand(target,value_array,options){
    const changeable = target.classList.contains("changeable")
    const appendable = target.classList.contains("appendable")
    const len = Math.min(target.children.length,value_array.length);
    if( target.children.length == 0 ){
        child_expand(target,value_array,options);
    }else{
        for( let i = -1; ++i < len; ){
            const value = value_array[i];
            let   child = target.children[i];
            if( changeable ){
                child = child.children[1];
            }
            div_expand(child,value,options);
        }
        if( appendable ){
            // console.log()
        }
    }
}

function imitatelist_correct(target){
    // データ行...
    const result = [];
    const changeable = target.classList.contains("changeable");
    const appendable = target.classList.contains("appendable");
    for( let i = -1; ++i < target.children.length - appendable; ){
        let child = target.children[i];
        if( changeable ){
            child = child.children[1];
        }
        const ret = get_elm_value(child);
        if( ret === undefined ){ continue }
        result.push(ret);
    }
    return result;
}
//////////////// page data controller ////////////////

//////////////// page writer ////////////////
function default_pattern(first_target,options){
    // options はdummy
    options = options?options:{};
    const base_patterns = [];
    const disabled_key  = !options["changeable"]?true:false;
    const appendable    =  options["appendable"]?true:false;
    const disp_margin   = disabled_key?"margin:5px 5px 5px 20px;":"margin:5px;";
    const draggable     = !disabled_key;

    const del_pattern = {
        func:make_button,
        value:"×",
        style:"height: 15px;"
            + "width: 15px;"
            + "border: none;"
            + "font-size: 12px;",
        action:{
            "click":(e)=>{
                const target = e.target.parentElement;
                const parent = target.parentElement;
                parent.removeChild(target);
                const host = parent.closest(".save");
                const send = document.getElementById(host.id);
                const props = {
                    bubbles:true,cancelable:false,capture:true,
                }
                send.dispatchEvent(new CustomEvent("div_change",props))
            }
        },
        classes:["del"]
    };
    
    // TODO accordion
    const accordion_key = options["accordion"]?true:false;
    
    
    // 現状のパターン展開はname無しの手順に対応していない
    // name無しの場合、どのように収集し、展開するのか設計が必要
    function check_type(value){
        if( is_array(value) ){
            return "array";
        }else if( is_object(value) ){
            return "object";
        }else if( is_boolean(value) ){
            return "bool";
        }else if( !isNaN(value) ){
            return "numeric";
        }else if( !value ){
            return "error";
        }else if( is_string(value) ){
            if( value.match("\r|\n") ){
                return "strings";
            }else{
                return "string";
            }
        }
        return "other";
    }
    const expand_funcs = {
        "array"  :function(value,name,patterns,stack){
            // object系は対象のinnerとobjectをunshiftでqueueに詰める
            // valueがarrayの場合はimitate_tableを付けてinnerで展開する
            const arraypatterns = [];
            const classes      = ["imitate_list"];
            // TODO set del button
            if( !disabled_key ){
                classes.push("changeable")
                for( let i = -1; ++i < value.length; ){
                    const inner = [];
                    arraypatterns.push({inner:inner})
                    inner.push(del_pattern);
                    stack.unshift({object:value[i],patterns:inner});
                }
                if( appendable ){
                    classes.push("appendable")
                    arraypatterns.push({
                        classes:["append"], // valueが全てobjectならimitate_tableでも
                        func:make_button,
                        value:"+",
                        style:make_inputstyle(0),
                        action:{click:(e)=>{
                            const text_pattern = {
                                func:make_input,
                                value:"",
                                classes:["save"],
                                disabled:disabled_key,
                                style:make_inputstyle(0)
                            }
                            const add_pattern = [
                                del_pattern,
                                text_pattern
                            ];
                            const target  = e.target.parentElement;
                            const add_elm = expand_pattern({inner:add_pattern});
                            target.insertBefore(add_elm,e.target);
                        }}
                    })
                }
            }else{
                for( let i = -1; ++i < value.length; ){
                    stack.unshift({object:value[i],patterns:arraypatterns});
                }
            }
            if( accordion_key && patterns.length > 0 ){
                const last = patterns.length-1;
                if( patterns[last]["classes"] ){
                    patterns[last]["classes"].push("accordion");
                }else{
                    patterns[last]["classes"] = ["accordion"];
                }
                classes.push("panel");
            }
            patterns.push({
                style:disp_margin
                    + "display: flex;"
                    + "flex-direction: column;",
                classes:classes, // valueが全てobjectならimitate_tableでも
                inner:arraypatterns,
                name:name,
            });
        },
        "object" :function(value,name,patterns,stack){
            // object系は対象のinnerとobjectをunshiftでqueueに詰める
            // valueがobjectの場合はinnerで展開する
            const classes     = [];
            const divpatterns = [];
            if( accordion_key && patterns.length > 0 ){
                const last = patterns.length-1;
                if( patterns[last]["classes"] ){
                    patterns[last]["classes"].push("accordion");
                }else{
                    patterns[last]["classes"] = ["accordion"];
                }
                classes.push("panel");
            }
            if( draggable ){
                classes.push("drop_dict");
            }
            patterns.push({
                style:disp_margin
                    + "display: flex;"
                    + "flex-direction: column;",
                inner:divpatterns,
                classes:classes,
                name:name,
            });
            
            const keys = Object.keys(value);
            let   px = 0;
            for( let i = -1; ++i < keys.length; ){
                px = Math.max(px,getTextWidth(keys[i],getCanvasFontSize()));
            }
            const style = make_labelstyle(px);
            for( let i = -1; ++i < keys.length; ){
                const key   = keys[i];
                const inner = [];
                divpatterns.push({inner:inner});
                // ここのラベルとデータの区切りは明確化が必要
                if( !disabled_key ){
                    inner.push(del_pattern);
                }
                inner.push({func:make_label,value:key,style:style});
                stack.unshift({object:value[key],patterns:inner,name:key});
            }
        },
        "numeric":function(value,name,patterns,stack){
            patterns.push({
                func:make_input,
                value:""+value,
                name:name,
                disabled:disabled_key,
                style:make_numstyle(0)
            });
        },
        "error"  :function(value,name,patterns,stack){
            patterns.push({func:make_input,value:""+value,
                disabled:disabled_key,name:name,style:make_labelstyle()});
        },
        "strings":function(value,name,patterns,stack){
            // make textarea
            patterns.push({func:make_textarea,value:value,disabled:disabled_key,name:name});
        },
        "string" :function(value,name,patterns,stack){
            patterns.push({
                func:make_input,
                value:""+value,
                name:name,
                disabled:disabled_key,
                style:make_inputstyle(0)
            });
            if( value.match("^http") ){
                patterns.push({
                    func:make_anchor,
                    value:""+value,
                    classes:["jumpbutton"]
                });
            }
        },
        "bool": function(value,name,patterns,stack){
            patterns.push({
                func:make_checkbox,
                value:value,
                name:name,
                disabled:disabled_key,
                style:make_inputstyle(0)
            });
        },
        "other"  :function(value,name,patterns,stack){
            patterns.push({
                func:make_input,
                value:""+value,
                name:name,
                disabled:disabled_key,
                style:make_inputstyle(0)
            });
        },
    };
    
    // key毎に展開
    // class等、展開規定が難しいものが入ってきた場合、[class class名]と表示したい
    // objectを拾った場合、それのidをstackで記録し
    // 同一オブジェクトの参照を検知する
    const stack   = [{object:first_target,patterns:base_patterns}];
    while( stack.length > 0 ){
        const target   = stack.pop();
        const patterns = get_dictvalue(target,"patterns",undefined);
        const value    = get_dictvalue(target,"object"  ,undefined);
        const name     = get_dictvalue(target,"name"    ,undefined);
        const typekey  = check_type(value);
        expand_funcs[typekey](value,name,patterns,stack);
    }
    
    return base_patterns;
}

//////////////// accordion controls ////////////////
function control_max_height(panel,controlHeight,first=false){
    // 親を遡ってパネルの高さを調整
    let target = panel.parentElement.closest(".panel");
    while( target ){
        let baseheight = 0;
        if( first ){
            baseheight = target.scrollHeight;
        }else if( target.style.maxHeight ){
            baseheight = target.style.maxHeight.slice(0,-2) * 1;
        }
        if( baseheight === 0 ){
            break;
        }
        target.style.maxHeight = (baseheight + controlHeight)+"px";
        if( !target.parentElement ){ break }
        target = target.parentElement.closest(".panel");
    }
    return panel;
}

function toggle_accordion(first=false) {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */

    /* Toggle between hiding and showing the active panel */
    let panel = undefined;
    if( this.id ){
        panel = document.getElementById(this.id+"_panel");
    }
    if( !panel ){
        panel = this.nextElementSibling;
    }
    let controlHeight = panel.scrollHeight;
    if( panel.style.maxHeight ) {
        panel.style.maxHeight = null;
        controlHeight *= -1;
    } else {
        panel.style.maxHeight = panel.scrollHeight+"px";
    }
    
    this.classList.toggle("active");
    panel.classList.toggle("active");
    
    control_max_height(panel,controlHeight,first);
    if( this.classList.contains("active")
     && this.classList.contains("close_other") ){
        for( let i = -1; ++i < this.parentElement.children.length; ){
            if( this === this.parentElement.children[i] ){
                continue;
            }
            const target = this.parentElement.children[i];
            if( target.classList.contains("active")
             && target.classList.contains("accordion")
             && target.classList.contains("close_other") ){
                target.click();
            }
        }
    }
}
function toggle_accordion_radio(first=false) {
    /* Toggle between adding and removing the "active" class,
    to highlight the button that controls the panel */
    if( this.checked && this.classList.contains("active") ){ return; }

    /* Toggle between hiding and showing the active panel */
    let panel = undefined;
    if( this.getAttribute("data-rawname") ){
        const key = this.getAttribute("data-rawname");
        panel = document.getElementById(key+"_panel");
    }
    if( this.id ){
        panel = document.getElementById(this.id+"_panel");
    }
    if( !panel ){
        panel = this.nextElementSibling;
    }
    if( !panel ){
        console.assert(false,"accordion html error");
        return;
    }
    let controlHeight = panel.scrollHeight;
    if( panel.style.maxHeight ) {
        panel.style.maxHeight = null;
        controlHeight *= -1;
    } else {
        panel.style.maxHeight = panel.scrollHeight+"px";
    }
    
    this.classList.toggle("active");
    panel.classList.toggle("active");
    
    control_max_height(panel,controlHeight,first);
    if( this.classList.contains("active") ){
        const name    = this.name;
        const targets = document.querySelectorAll("input[type='radio'][name='"+name+"']:not(:checked)");
        for( let i = -1; ++i < targets.length; ){
            const target = targets[i];
            if( target.classList.contains("active")
             && target.classList.contains("accordion")){
                toggle_accordion_radio.bind(target,false)();
            }
        }
    }
}
function control_accordions(top_node=document,target_only=false){
    
    const types = {"radio":"radio"}
    const funcs = {
        undefined:toggle_accordion,
        "radio":toggle_accordion_radio
    }

    if( target_only && !top_node.classList.contains("accordion") ){ return }
    
    const under_tree = top_node.querySelectorAll(".accordion");
    const accordions = target_only?[top_node]:under_tree;
    for( let i = 0; i < accordions.length; i++ ){
        const target = accordions[i];
        const type   = types[target.type];
        const func   = funcs[type];
        target.addEventListener("click",func);
    }
    setTimeout(()=>{

        if( target_only
                && ( top_node.classList.contains("active")
                ||  !top_node.classList.contains("open") )){ return }
        const under_tree = top_node.querySelectorAll(".accordion.open:not(.active)");
        const accordions = target_only?[top_node]:under_tree;
        for( let i = 0; i < accordions.length; i++ ){
            const target = accordions[i];
            const type   = types[target.type];
            const func   = funcs[type];
            func.bind(target)(true);
        }
    },200)
}

//////////////// drag controls ////////////////
function drag(e){
    //テキストをdataTransferにセットする
    const dragid = generateUuid();
    e.target.setAttribute("data-dragid",dragid);
    e.dataTransfer.setData( "text" , dragid);
    e.stopPropagation();
}

function make_drop(options = {}){
    const vertical_design   = options["direction_design"] === "horizontal"?false:true;
    const drop_callback     = options["drop_callback"]?options["drop_callback"]:()=>{};
    const parent_free       = options["parent_free"]?true:false;
    const clone_othergroups = options["clone_othergroups"]?true:false;
    function drop_imple(e){
        
        //ブラウザのデフォルト動作の抑制
        e.preventDefault();
        
        //dataTransferからテキストデータを受け取る
        const droptxt = e.dataTransfer.getData("text");
        //ドロップエリアに受け取ったテキストを記述
        const dragitem      = document.querySelector("[data-dragid='"+droptxt+"']");
        const base          = bubbling_class(dragitem,"drag")
        let   target        = bubbling_class(e.target,"drag");
        const base_parent   = bubbling_class(base,["drop_lane","drop_dict"]);
        const target_parent = bubbling_class(target,["drop_lane","drop_dict"]);
        
        if( dragitem ){
            dragitem.toggleAttribute("data-dragid");
        }
        
        if( !target_parent.parentElement ){
            return;
        }
        
        if( target_parent === base_parent ){
            // pass
        }else if( !parent_free ){
            return
        }else if( clone_othergroups ){
            base = cloneNodeUpdateId(base,true);
        }
        
        // 同一laneに追加する場合
        let direction = 0;
        if( vertical_design ){
            direction = e.offsetY/(getCssStyle(target,"height").slice(0,-2)*1);
        }else{
            direction = e.offsetX/(getCssStyle(target,"width").slice(0,-2)*1);
        }
        
        if( target && direction > 0.5 ){
            target = target.nextSibling;
        }
        target_parent.insertBefore(base,target);
        drop_callback(base,target);
    }
    return drop_imple;
}

function prevent_default(e){
    e.preventDefault();
}

function jqevent_wrapp(func){
    return function(e){func(e.originalEvent)}
}

function control_draganddrop(options = {}){
    document.addEventListener("drop"     ,make_drop(options),false);
    document.addEventListener("dragstart",drag              ,false);
    document.addEventListener("dragenter",prevent_default   ,false);
    document.addEventListener("dragover" ,prevent_default   ,false);
    //ドラッグ開始時の処理
    const targets = document.querySelectorAll(".drop_lane,.drop_dict");
    for( let i = -1; ++i < targets.length; ){
        const drop_lane = targets[i];
        for( let j = -1; ++j < drop_lane.children.length; ){
            const dragitem = drop_lane.children[j];
            if( !dragitem.classList.contains("drag") ){
                dragitem.classList.toggle("drag");
            }
            dragitem.setAttribute("draggable",true);
        }
    }
}

//////////////// html util ////////////////
function update_idnum(target){
    const target_id = target.getAttribute("id");
    if( !target_id ){
        return;
    }
    // change id
    let offset  = 1;
    let head_id = "";
    const lastnum = target_id.search("[0-9]+$");
    if( lastnum != -1 ){
        head_id = target_id.slice(0,lastnum);
        offset  = target_id.slice(lastnum)*1+1;
        while( document.getElementById(head_id+offset) ){
            offset++;
        }
    }else{
        head_id = target_id+"_";
    }
    target.setAttribute("id",head_id+offset);
}

function cloneNodeUpdateId(src,deep){
    const clone = src.cloneNode(deep);
    const stack = [clone];
    while( stack.length > 0 ){
        const target    = stack.pop();
        // set stack
        for( let i = -1; ++i < target.children.length; ){
            stack.push(target.children[i]);
        }
        update_idnum(target);
    }
    return clone;
}

// accordion buttonを作成（value:{text:str,open:bool} ）
function create_accordion(value){
    const textval     = value["text"];
    const defaultopen = value["open"];
    const button_value = document.createElement("input");
    button_value.value = textval;
    button_value.setAttribute("type","button");
    button_value.classList.add("class","accordion");
    if( defaultopen ){ button_value.classList.add("open"); }
    return button_value;
}

function packing_panel(childvalue){
    const panel = document.createElement("div");
    panel.appendChild(childvalue);
    panel.classList.add("class","panel");
    return panel;
}

function make_span(value){
    return document.createElement("span");
}

// 数値リストを作成（value:{id,space,limit:int} ）
function make_numlist(value){
    const selectlist = make_select(value["id"]);
    const limit      = value["limit"];
    if( value["space"] ){
        selectlist.appendChild(make_option({"value":"","text":" "}));
    }
    for( let i = 0; i < limit; i++ ){
        selectlist.appendChild(make_option({"value":i,"text":""+i}));
    }
}

// リストを作成（value:{id,space,options:[{value,text},...]} ）
function make_list(value){
    const selectlist = make_select(value["id"]);
    const options    = value["options"];
    if( value["space"] ){
        selectlist.appendChild(make_option({"value":"","text":" "}));
    }
    for( let i = 0; i <= options.length; i++ ){
        selectlist.appendChild(make_option(options[i]));
    }
    return selectlist;
}

// リストを作成（value:{id,space,options:[text,...]} ）
function make_textlist(value){
    const selectlist = make_select(value["id"]);
    const options    = value["options"];
    if( value["space"] ){
        selectlist.appendChild(make_option({"value":"","text":" "}));
    }
    for( let i = 0; i <= options.length; i++ ){
        selectlist.appendChild(make_option({"value":options[i],"text":options[i]}));
    }
    return selectlist;
}

function make_select(selected){
    // selectを生成する
    const select_value = document.createElement("select");
    if( selected ){
        select_value.selectedIndex = selected;
    }
    return select_value;
}

// value:{value,text:str}
function make_option(value){
    // optionを生成する
    const option_value = document.createElement("option");
    if( value ){
        if( value["value"] ){
            option_value.value = value["value"];
        }
        if( value["text"] ){
            const text_value = document.createTextNode(value["text"]);
            option_value.appendChild(text_value);
        }
    }
    return option_value;
}

// textval:union{text,{text,for:str}}
function make_label(textval){
    const label      = document.createElement("label");
    if( is_object(textval) ){
        const text_value = document.createTextNode(textval["text"]);
        label.setAttribute("for",textval["for"]);
        label.appendChild(text_value);
    }else{
        const text_value = document.createTextNode(textval);
        label.appendChild(text_value);
    }
    return label;
}

function make_button(buttontext){
    // ボタンを生成する、functionは別途定義
    const button_value = document.createElement("input");
    button_value.value = buttontext;
    button_value.setAttribute("type","button");
    return button_value;
}

function make_checkbox(checked){
    // checkboxを生成する
    const check_value = document.createElement("input");
    if( checked ){
        check_value.checked = true;
    }
    check_value.setAttribute("type","checkbox");
    return check_value;
}

function make_input(default_value){
    // Inputを生成する
    const input_value = document.createElement("input");
    if( default_value ){
        input_value.value = default_value;
    }
    input_value.setAttribute("type","text");
    return input_value;
}

function make_anchor(default_value){
    // Inputを生成する
    const anchor_value = document.createElement("a");
    if( default_value ){
        anchor_value.href   = default_value;
        anchor_value.target = "_blank;";
        anchor_value.rel    = "noopener,noreferrer";
    }
    return anchor_value;
}

// value:union{text,{text,cols,rows}}
function make_textarea(value){
    // TextAreaを生成する
    const textarea = document.createElement("textarea");
    if( is_object(value) ){
        if( value.hasOwnProperty("text") ){
            textarea.value = value["text"];
        }
        if( value.hasOwnProperty("cols") ){
            textarea.setAttribute("cols",value["cols"]);
        }
        if( value.hasOwnProperty("rows") ){
            textarea.setAttribute("rows",value["rows"]);
        }
    }else if( value ){
        textarea.value = value;
    }
    return textarea;
}

//////////////// expand util ////////////////
function make_styletext(value){
    
    if( !value ){ return; }
    
    const margin     = value["margin"];
    const width      = value["width"];
    const block      = value["block"];
    const text_align = value["text_align"]; 
    
    let setstyle = "";
    if( margin ){
        setstyle += "margin:0 "+margin+"px 0 "+margin+"px;padding: 0 0 0 0;";
    }else{
        setstyle += "margin:0 0 0 0;padding: 0 0 0 0;";
    }
    if( width ){
        let suffix = "";
        if( width !== "auto" ){ suffix = "px"; }
        setstyle += "width:"+width+suffix+";";
    }
    if( block ){
        setstyle += "display:inline-block;";
    }
    if( text_align ){
        setstyle += "text-align:"+text_align+";";
    }
    return setstyle;
}
// label style     {margin:3,width:"auto",block:true,text_align:undefined}
function make_labelstyle(px){ return make_styletext({margin:3,width:px?px:"auto",block:true,text_align:undefined}); }
// input style     {margin:0,with:input.length*4 ,block:true,text_align:undefined}
function make_inputstyle(input_length){
    const px = getTextWidth("m",getCanvasFontSize())*input_length;
    return make_styletext({margin:0,width:px?px:"auto",block:true,text_align:undefined});
}
// num input style {margin:0,width:input.length*4,block:true,text_align:"right"}
function make_numstyle(input_length){
    const px = getTextWidth("0",getCanvasFontSize())*input_length;
    return make_styletext({margin:0,width:px?px:"auto",block:true,text_align:"right"});
}

function set_param(elm,id,name,classes,style,disabled){
    if( id ){
        elm.setAttribute("id",id);
    }
    if( name ){
        elm.setAttribute("name",name);
    }
    if( classes ){
        for( let i = 0; i < classes.length; i++ ){
            elm.classList.add(classes[i]);
        }
    }
    if( style ){
        elm.style = style;
    }
    if( disabled ){
        elm.toggleAttribute("disabled");
    }
    return elm;
}

// e => e;
function flat(v){return v;}

function expand_pattern(pattern){
    const get_pattern = get_dictvalue.bind(null,pattern);
    const id          = get_pattern("id",undefined);
    const name        = get_pattern("name",undefined);
    const classes     = get_pattern("classes",undefined);
    const style       = get_pattern("style",undefined);
    const func        = get_pattern("func",flat);
    const value       = get_pattern("value",undefined);
    const disabled    = get_pattern("disabled",false);
    const action      = get_pattern("action",{});
    const inner       = get_pattern("inner",[]);

    let elm = func(value);
    elm = elm?elm:document.createElement("div");
    elm = elm["localName"]?elm:document.createElement("div");
    elm = set_param(elm,id,name,classes,style,disabled);
    const keys = Object.keys(action);
    for( let i = 0; i < keys.length; i++ ){
        const key = keys[i];
        elm.addEventListener(key,action[key])
    }
    for( let i = 0; i < inner.length; i++ ){
        const child = expand_pattern(inner[i]);
        elm.appendChild(child);
    }
    return elm;
}

//////////////// page action ////////////////
function get_clientrect(target){
    return [
        target.clientWidth,
        target.clientHeight,
        target.clientLeft,
        target.clientTop,
    ]
}

function goback_overlay(target){
    const targetrect = get_clientrect(target).toString();
    while( target.parentElement &&
            get_clientrect(target.parentElement).toString() === targetrect ){
        target = target.parentElement;
    }
    return target;
}

//////////////// unuse ////////////////
function switch_siblingclass(target,class_name){
    const target_parent = target.parentElement;
    const target_siglings = target_parent.querySelectorAll(
        ":scope > ."+class_name);
    for( let i = -1; ++i < target_siglings.length; ){
        target_siglings[i].classList.remove(class_name);
    }
    target.classList.add(class_name);
}

