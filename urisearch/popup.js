import {load_settings,save_settings} from "./background_util.js"
import {update_rightclick} from "./event.js"
// 保存ボタン
function save_all_default(){
    var value = get_page_values(".save");
    save_settings("default",value);
}

function set_bodywidth(){
    var value     = get_page_values(".save");
    var width     = 0;
    var right_pad = 6;
    if( "urls" in value ){
        var input = document.querySelector("input");
        var font  = getCanvasFontSize(input);
        var delbutton_width = 20;
        for( var i = -1; ++i < value.urls.length; ){
            
            var url   = value.urls[i].url;
            var title = value.urls[i].title;
            
            var url_width   = getTextWidth(url  , font);
            var title_width = getTextWidth(title, font)+delbutton_width;
            
            if( width < url_width ){
                width = url_width;
            }
            if( width < title_width ){
                width = title_width;
            }
            
        }
    }
    document.body.style.width = (width+right_pad).toString()+"px";
}

function input_action(e){
    save_all_default();
    set_bodywidth();
    setTimeout(update_rightclick,1)
}

function set_rowfunc(target_base){
    var set_values = [
        { key : ".addrow" , action : "click", func : add_rawrow}
       ,{ key : ".delrow" , action : "click", func : del_row}
       ,{ key : ".title"  , action : "input", func : input_action}
       ,{ key : ".url"    , action : "input", func : input_action}
       ,{ key : ".enc"    , action : "input", func : input_action}
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
    var urls = document.querySelector("#urls");
    add_row(urls,"","");
}

function set_firstrow(){
    var urls = document.querySelector("#urls");
    if( urls.children.length == 0 ){
        add_rawrow();
    }
}

function add_row(parent_div,url,title,enc=1){
    enc = enc?"checked":"";
    const div = document.createElement("div");
    parent_div.appendChild(div);
    div.innerHTML = "<div class='hover' style='display:block'>"
                  + "<input class='title' name='title' value='"+title+"' placeholder='please input title'>\r\n"
                  + "<label class='enclabel'>enc</label>"
                  + "<input class='enc' name='enc' "+enc+" type='checkbox'>"
                  + "<input class='delrow' type='button' value='×'>"
                  + "</div><div class='hover'>"
                  + "<input class='url' name='url' value='"+url+"' placeholder='please input search url (replace key {})'>"
                  + "</div>";
    set_rowfunc(div);
    div.style.display = "block";
    div.classList.toggle("row");
}

function del_row(e){
    var urls = e.target.closest("#urls");
    var row   = e.target.closest(".row");
    urls.removeChild(row);
    document.querySelector(".url").dispatchEvent(new Event("input"));
}

// ページ読み込み時の処理
window.onload = function() {
    load_settings("default",(settings) => {
        set_page_values(".save",settings,{expand_funcs:expand_funcs});
        const options = {
            "direction_design":"vertical",
            "drop_callback":(base,target)=>{
                input_action();
            }
        };
        control_draganddrop(options);        
        set_firstrow();
        set_rowfunc(document);
        set_bodywidth();
    });
}

var expand_funcs = {
    urls : expand_urls
};

function expand_urls(target,key,urls,options){
    if( !is_array(urls) ){
        urls = [urls];
    }
    for( var i = -1; ++i < urls.length; ){
        if( !("enc" in urls[i]) ){ urls[i].enc = 1; }
        add_row(target,urls[i].url,urls[i].title,urls[i].enc);
    }
}
