function is_array(obj) { return Array.isArray(obj); }
function is_object(obj) { return typeof obj === 'object' && obj !== null && !is_array(obj); }

// const set_alarms = ()=>{}
var reloadtime = Date.now();
var alarms     = undefined;
function set_alarms(){
    reloadtime = Date.now() + 59000
    if( alarms ){ return; }
    alarms = true;
    chrome.alarms.create("update_storage",{ delayInMinutes: 1, periodInMinutes: 1 });
}
function check_alarms(){
    if( reloadtime > Date.now() ){ return false; }
    chrome.alarms.clear("update_storage");
    alarms = false;
    return true;
}
chrome.alarms.onAlarm.addListener(() => {
    // 処理
    if( !check_alarms() ){ return }
    chrome.storage.session.get(null,(obj)=>{
        const set = ()=>chrome.storage.local.set(obj)
        chrome.storage.local.clear().then(set);
        // set();
    });
});

const set_sessionstorage = ()=>{
    chrome.storage.local.get(null,(obj)=>{
        chrome.storage.session.set(obj);
        chrome.storage.session.get(null,o=>console.log(o));
    });
}
const set_name = (name,func)=>()=>{console.log(name);func();}
chrome.runtime.onStartup.addListener(set_name("startup",set_sessionstorage));
chrome.runtime.onInstalled.addListener(set_name("install",set_sessionstorage));

function makeStorageFunctions(storage,name,delay_save=false){
    
    let save_action = ()=>{}
    if( storage === chrome.storage.session && delay_save ){
        save_action = set_alarms;
    }
    
    // 情報の取得
    function load_storage(domain,do_next){
        storage.get(domain+name,function(dictobj){
            const keys = Object.keys(dictobj);
            let   ret  = {};
            if( keys.length > 0 ){
                ret = dictobj[keys[0]];
            }
            if (typeof ret === "string" || ret instanceof String) {
                ret = JSON.parse(ret);
            }
            do_next(ret);
        });
    }
    
    // 情報の登録
    function save_storage(domain,value){
        const inobj = {};
        inobj[domain+name] = JSON.stringify(value);
        storage.set(inobj);
        save_action();
    }

    function update_storage(domain,value){
        load_storage(domain,(stored)=>{
            Object.assign(stored,value);
            save_storage(domain,stored);
        });
    }

    function delete_storage(domain,keys){
        if( keys == null || keys == "" ){
            save_storage(domain,{});
        }else{
            if( typeof keys == "string" ){
                keys = [keys];
            }
            load_storage(domain,(load_values)=>{
                for( var i = 0; i < keys.length; i++ ){
                    delete(load_values[keys[i]]);
                }
                save_storage(domain,load_values);
            });
        }
    }

    function getall_storage(do_next){
        storage.get(null,function(x){do_next(x)});
    }
    function setall_storage(obj){
        storage.clear().then(()=>{storage.set(obj)});
    }
    
    function control_storage(domain,data){
        load_storage(domain,(load_values)=>{
            if( "update_keys" in data && "value" in data ){
                const stack = [[data["update_keys"],data["value"],load_values]];
                while( stack.length > 0 ){
                    let [keys,set_values,load_values] = stack.pop();
                    if( typeof keys == "string" ){
                        keys = [keys];
                    }
                    if( is_array(keys) ){
                        for( let i = -1; ++i < keys.length; ){
                            const key = keys[i];
                            load_values[key] = set_values[key];
                        }
                    }else if( is_object(keys) ){
                        const keys2 = Object.keys(keys);
                        for( let i = -1; ++i < keys2.length; ){
                            const key = keys2[i];
                            stack.push([keys[key],set_values[key],load_values[key]]);
                        }
                    }
                }
            }
            if( "delete_keys" in data ){
                const stack = [[data["delete_keys"],load_values]];
                while( stack.length > 0 ){
                    let [keys,values] = stack.pop();
                    if( typeof keys == "string" ){
                        keys = [keys];
                    }
                    if( is_array(keys) ){
                        for( let i = -1; ++i < keys.length; ){
                            delete(values[keys[i]]);
                        }
                    }else if( is_object(keys) ){
                        const keys2 = Object.keys(keys);
                        for( let i = -1; ++i < keys2.length; ){
                            const key = keys2[i];
                            stack.push([keys[key],values[key]]);
                        }
                    }
                }
            }
            save_storage(domain,load_values);
        });
    }

    return [load_storage,
             save_storage,
             update_storage,
             delete_storage,
             getall_storage,
             setall_storage,
             control_storage];
}

// let funcs1 = makeStorageFunctions(chrome.storage.local,"_info");
let funcs1 = makeStorageFunctions(chrome.storage.session,"_info",true);
export var load_info       = funcs1[0];
export var save_info       = funcs1[1];
export var update_info     = funcs1[2];
export var delete_info     = funcs1[3];
export var getall_storage  = funcs1[4];
export var setall_storage  = funcs1[5];
export var control_storage = funcs1[6];

// let funcs2 = makeStorageFunctions(chrome.storage.local,"_settings");
let funcs2 = makeStorageFunctions(chrome.storage.session,"_settings",true);
export var load_settings    = funcs2[0];
export var save_settings    = funcs2[1];
export var update_settings  = funcs2[2];
export var delete_settings  = funcs2[3];
export var control_settings = funcs2[6];

// let funcs3 = makeStorageFunctions(chrome.storage.local,"_logs");
let funcs3 = makeStorageFunctions(chrome.storage.session,"_logs",true);
export var load_logs    = funcs3[0];
export var save_logs    = funcs3[1];
export var update_logs  = funcs3[2];
export var delete_logs  = funcs3[3];
export var control_logs = funcs3[6];


export function conv_url(url){
    if( url == null ){
        url = document.URL;
    }
    var split_url = url.split("/");
    var page = split_url.slice(3,split_url.length).join("/");
    return {domain:split_url[2],page:page}
}

export function send_urltab(value,url,respfunc){
    var key = true;
    function send_value(tabs) {
        if( !key ){ return; } 
        function reaction(response) {
            respfunc(response);
            if( response ){
                console.log(response);
            }else{
                var error = chrome.runtime.lastError;
                if( error ){
                    console.log(error);
                }
            }
        }
        for( var i = -1; ++i<tabs.length; ){
            var tab = tabs[i];
            if( !tab ){ continue; }
            if( !tab.url ){ continue; }
            if( tab.url != url ){
                continue;
            }
            key = false;
            if( respfunc ){
                chrome.tabs.sendMessage(tab.id, value, {},reaction);
            }else{
                chrome.tabs.sendMessage(tab.id, value).then(()=>{}).catch(()=>{});
            }
            return;
        }
    }
    
    var query_url = url;
    if( query_url.indexOf("#") != -1 ){
        query_url = query_url.split("#")[0]+"*";
    }
    chrome.tabs.query({url:query_url,active:true,currentWindow:true}, send_value);
    chrome.tabs.query({url:query_url,active:true}, send_value);
    chrome.tabs.query({url:query_url}, send_value);
}

export function send_currenttab(value,respfunc){
    chrome.tabs.query({active: true, currentWindow: true}, function (tabs) {
        
        function reaction(response) {
            respfunc(response);
            if( response ){
                console.log(response);
            }else{
                var error = chrome.runtime.lastError;
                if( error ){
                    console.log(error);
                }
            }
        }
        for( var i = -1; ++i<tabs.length; ){
            var tab = tabs[i];
            if( respfunc ){
                chrome.tabs.sendMessage(tab.id, value, {},reaction);
            }else{
                chrome.tabs.sendMessage(tab.id, value);
            }
            return;
        }
    });
}

export function do_domain(func){
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        if( !tabs ){ return; }
        if( !tabs[0] ){ return; }
        var domain = conv_url(tabs[0].url).domain;
        func(domain,tabs[0].url);
    });
}

// 保存ボタン
function save_all(){
    do_domain(function(domain){
        var value = get_page_values(".save");
        save_settings(domain,value);
    });
}

export function control_save(){
    control_function("save",save_all);
}

export function control_function(class_name,func){
    var keys = [
        {action:"blur"  ,key:"input:not([type])."+class_name+"[id]"},
        {action:"blur"  ,key:"input[type='text']."+class_name+"[id]"},
        {action:"click" ,key:"input[type='radio']."+class_name+"[id]"},
        {action:"click" ,key:"input[type='checkbox']."+class_name+"[id]"},
        {action:"blur"  ,key:"textarea."+class_name+"[id]"},
        {action:"change",key:"select."+class_name+"[id]"},
        {action:"click" ,key:".imitate_select."+class_name+"[id] .imitate_pulldown"},
        {action:"drop"  ,key:".drop_lane."+class_name+"[id]"},
        {action:"blur"  ,key:"."+class_name+"[id] input:not([type])[name]"},
        {action:"blur"  ,key:"."+class_name+"[id] input[type='text'][name]"},
        {action:"click" ,key:"."+class_name+"[id] input[type='radio'][name]"},
        {action:"click" ,key:"."+class_name+"[id] input[type='checkbox'][name]"},
        {action:"click" ,key:"."+class_name+"[id] input[type='button'].del"},
        {action:"blur"  ,key:"."+class_name+"[id] textarea[name]"},
        {action:"change",key:"."+class_name+"[id] select[name]"},
        {action:"click" ,key:"."+class_name+"[id] .imitate_select[name] .imitate_pulldown"},
        {action:"drop"  ,key:"."+class_name+"[id] .drop_lane[name]"},
        {action:"blur"  ,key:"."+class_name+"[id] .imitate_list[name] > input:not([type])"},
        {action:"blur"  ,key:"."+class_name+"[id] .imitate_list[name] > input[type='text']"},
        {action:"click" ,key:"."+class_name+"[id] .imitate_list[name] > input[type='radio']"},
        {action:"click" ,key:"."+class_name+"[id] .imitate_list[name] > input[type='checkbox']"},
        {action:"click" ,key:"."+class_name+"[id] .imitate_list[name] > input[type='button'].del"},
        {action:"blur"  ,key:"."+class_name+"[id] .imitate_list[name] > textarea"},
        {action:"change",key:"."+class_name+"[id] .imitate_list[name] > select"},
        {action:"click" ,key:"."+class_name+"[id] .imitate_list[name] > .imitate_select .imitate_pulldown"},
        {action:"drop"  ,key:"."+class_name+"[id] .imitate_list[name] > .drop_lane"},
        {action:"blur"  ,key:"."+class_name+"[id] .drop_lane[name] > input:not([type])"},
        {action:"blur"  ,key:"."+class_name+"[id] .drop_lane[name] > input[type='text']"},
        {action:"click" ,key:"."+class_name+"[id] .drop_lane[name] > input[type='radio']"},
        {action:"click" ,key:"."+class_name+"[id] .drop_lane[name] > input[type='checkbox']"},
        {action:"click" ,key:"."+class_name+"[id] .drop_lane[name] > input[type='button'].del"},
        {action:"blur"  ,key:"."+class_name+"[id] .drop_lane[name] > textarea"},
        {action:"change",key:"."+class_name+"[id] .drop_lane[name] > select"},
        {action:"click" ,key:"."+class_name+"[id] .drop_lane[name] > .imitate_select .imitate_pulldown"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > input:not([type])"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > input[type='text']"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > input[type='radio']"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > input[type='checkbox']"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > input[type='button'].del"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > textarea"},
        {action:"change",key:".imitate_list."+class_name+"[id] > select"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > .imitate_select .imitate_pulldown"},
        {action:"drop"  ,key:".imitate_list."+class_name+"[id] > .drop_lane"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > * input:not([type])[name]"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > * input[type='text'][name]"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > * input[type='radio'][name]"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > * input[type='checkbox'][name]"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > * input[type='button'].del"},
        {action:"blur"  ,key:".imitate_list."+class_name+"[id] > * textarea[name]"},
        {action:"change",key:".imitate_list."+class_name+"[id] > * select[name]"},
        {action:"click" ,key:".imitate_list."+class_name+"[id] > * .imitate_select[name] .imitate_pulldown"},
        {action:"drop"  ,key:".imitate_list."+class_name+"[id] > * .drop_lane[name]"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > input:not([type])"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > input[type='text']"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > input[type='radio']"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > input[type='checkbox']"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > input[type='button'].del"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > textarea"},
        {action:"change",key:".drop_lane."+class_name+"[id] > select"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > .imitate_select .imitate_pulldown"},
        {action:"drop"  ,key:".drop_lane."+class_name+"[id] > .drop_lane"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > * input:not([type])[name]"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > * input[type='text'][name]"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > * input[type='radio'][name]"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > * input[type='checkbox'][name]"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > * input[type='button'].del"},
        {action:"blur"  ,key:".drop_lane."+class_name+"[id] > * textarea[name]"},
        {action:"change",key:".drop_lane."+class_name+"[id] > * select[name]"},
        {action:"click" ,key:".drop_lane."+class_name+"[id] > * .imitate_select[name] .imitate_pulldown"},
    ];
    for( var i = -1; ++i < keys.length; ){
        var key  = keys[i];
        var checkkey = get_dictvalue(key,"key","");
        var action   = get_dictvalue(key,"action","");
        var save_elements = document.querySelectorAll(checkkey);
        for( var j = 0; j < save_elements.length; j++ ){
            var save_element = save_elements[j];
            save_element.addEventListener(action,func);
        }
    }
}