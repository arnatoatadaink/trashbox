import {save_settings,load_settings,do_domain} from "./background_util.js"
import {update_zoom,zoom_cancel2} from "./event.js"

// 保存ボタン
function save_all(){
    do_domain(function(domain){
        var value = get_page_values(".save");
        save_settings(domain,value);
    });
}

function plus_step(e){
    var target = e.target.parentElement.querySelector("input[type='number']");
    target.value = min(10+(target.value*1),400);
    target.dispatchEvent(new Event("input"));
}
function minus_step(e){
    var target = e.target.parentElement.querySelector("input[type='number']");
    target.value = max(-10+(target.value*1),1);
    target.dispatchEvent(new Event("input"));
}
function reset_zoom(e){
    var target = e.target.parentElement.querySelector("input[type='number']");
    target.value  = 100;
    target.dispatchEvent(new Event("input"));
}
function switch_checkbox(e){
    var target = e.target.querySelector("input[type='checkbox']");
    if( target ){
        target.checked = !target.checked;
    }
    setTimeout(save_all,1);
    setTimeout(update_zoom,3);
}

function input_action(e){
    if( e.target.value*1 > 400 ){
        e.target.value = 400;
    }else if( e.target.value*1 < 1 ){
        e.target.value = 1;
    }
    save_all();
    setTimeout(update_zoom,1)
}

function update_match(e){
    var div = e.target.closest("div.row").children[1];//.querySelector(".zoom");
    div.setAttribute("name",e.target.value);
    save_all();
    setTimeout(update_zoom,1)
}

function update_select(e){
    save_all();
    setTimeout(update_zoom,1)
}

function set_rowfunc(target_base){
    var set_values = [
        { key : ".addrow"  , action : "click", func : add_rawrow}
       ,{ key : ".cancel"  , action : "click", func : zoom_cancel}
       ,{ key : ".delrow"  , action : "click", func : del_row}
       ,{ key : ".plus"    , action : "click", func : plus_step}
       ,{ key : ".minus"   , action : "click", func : minus_step}
       ,{ key : ".reset"   , action : "click", func : reset_zoom}
       ,{ key : ".zoom"    , action : "input", func : input_action}
       ,{ key : ".match"   , action : "input", func : update_match}
       ,{ key : ".selector", action : "input", func : update_select}
       ,{ key : ".full"    , action : "click", func : switch_checkbox}
    ];
    for( var i = -1; ++i < set_values.length; ){
        var set_value = set_values[i];
        var key     = set_value["key"];
        var action  = set_value["action"];
        var func    = set_value["func"];
        var targets = target_base.querySelectorAll(key);
        for( var j = -1; ++j < targets.length; ){
            var target = targets[j];
            target.addEventListener(action,func);
        }
    }
}

function add_rawrow(e){
    var matches = document.querySelector("#matches");
    add_row(matches,"","",100,false);
}

function add_row(parent_div,key,selector,value,check){
    var div = document.createElement("div");
    parent_div.appendChild(div);
    if( check ){
        check="checked";
    }else{
        check = "";
    }
    selector = selector?selector:"";
    div.innerHTML = "<div class='hover' style='display:block'>"
                  + "<input style='width:213px' class='match' value='"+key+"' placeholder='please input match key'>"
                  + "<input class='delrow' style='float:right;width:20px' type='button' value='×'>"
                  + "</div>"
                  + "<div name='"+key+"'>"
                  + "<div class='hover' style='display:block'>"
                  + "<input style='width:233px' class='selector' name='selector' value='"+selector+"' placeholder='please input selector key'>"
                  + "</div>"
                  + "<div class='hover'>"
                  + "<input class='zoom' name='zoom' value='"+value+"' type='number' min='1' max='400' value='100' step='1'>\r\n"
                  + "<div class='plus'>＋</div>\r\n"
                  + "<div class='minus'>–</div>\r\n"
                  + "<div class='reset'>Reset</div>\r\n"
                  + "<div class='full'><input name='full' type='checkbox' "+check+">fullonly</div>\r\n"
                  + "</div>"
                  + "</div>";
    set_rowfunc(div);
    div.style.display = "block";
    div.classList.toggle("row");
}

function zoom_cancel(e){
    zoom_cancel2();
}

function del_row(e){
    var matches = e.target.closest("#matches");
    var row   = e.target.closest(".row");
    matches.removeChild(row);
    document.querySelector(".zoom").dispatchEvent(new Event("input"));
}
var expand_funcs = {
    matches : expand_matches
};

function expand_matches(target,key,values,options){
    var keys = Object.keys(values);
    for( var i = -1; ++i < keys.length; ){
        var key = keys[i];
        var value = values[key];
        add_row(target,key,value["selector"],value["zoom"],value["full"]);
    }
}
// ページ読み込み時の処理
window.onload = function() {
    do_domain(function(domain){
        load_settings(domain,function(settings){
            set_page_values(".save",settings,{expand_funcs:expand_funcs});
            set_rowfunc(document);
        });
    });
}

