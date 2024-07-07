function textarea2storage(){
    var newobj = {};
    var values = document.querySelector("textarea").value;
    values = values.replaceAll("'","\"");
    // var save_dict = JSON.parse(values);
    // keys   = Object.keys(save_dict);
    // for( var i = -1; ++i < keys.length; ){
    //     var key   = keys[i];
    //     var value = JSON.stringify(save_dict[key]);
    //     window.localStorage.setItem(key+"_settings",value);
    // }
    values = values.split(RegExp("\\r|\\n|(?=//)"));
    for( var i = values.length; --i >= 0; ){
        if( values[i].match("^([\\s]*$|//)") ){
            values.splice(i, 1);
        }
    }
    var save_dict = {};
    for( var i = -1; ++i < values.length; ){
        var value = values[i];
        var splited = value.split(":");

        var key  = undefined;
        var zoom = undefined;
        
        if( splited.length < 2 ){
            continue;
        }else if( splited.length == 2 ){
            key  = splited[0].trim();
            zoom = splited[1].trim();
            if( isNaN(zoom) ){ continue; }
        }else{
            key  = splited.shift().trim();
            zoom = splited.join(":");
        }
        zoom = JSON.parse(zoom);
        var page = "";
        if( key.search("/") != -1 ){
            var splited = key.split("/");
            key  = splited[0];
            splited.splice(0,1);
            page = splited.join("/");
        }
        if( !(key in save_dict) ){
            save_dict[key] = {"matches":{}};
        }
        if( !page ){
            save_dict[key]["default"] = zoom;
        }else{
            save_dict[key]["matches"][page] = zoom;
        }
    }
    var keys   = Object.keys(save_dict);
    for( var i = -1; ++i < keys.length; ){
        var key   = keys[i];
        var value = JSON.stringify(save_dict[key]);
        newobj[key+"_settings"] = value;
    }
    chrome.storage.local.clear().then(()=>{
        chrome.storage.local.set(newobj);
    });
    chrome.storage.session.clear().then(
        ()=>chrome.storage.session.set(newobj));
}

function storage2textarea(){
    chrome.storage.local.get(null,function(storage){
        var setvalue = "";
        var keys = Object.keys(storage).sort();
        for( var i = -1; ++i < keys.length; ){
            var key = keys[i];
            if( key.search("_settings$") == -1 ){ continue; }
            var value = JSON.parse(storage[key]);
            if( !("default" in value) ){ continue; }
            key = key.slice(0,-9);
            setvalue += key + " : " + JSON.stringify(value["default"]) + "\r\n"
            if( !("matches" in value) ){
                continue;
            }
            var matches    = value["matches"];
            var match_keys = Object.keys(matches);
            for( var j = -1; ++j < match_keys.length; ){
                var match_key = match_keys[j];
                setvalue += key+"/"+match_key + " : " + JSON.stringify(matches[match_key]) + "\r\n"
            }
        }
        document.querySelector("textarea").value = setvalue;
    });
}

// ページ読み込み時の処理
window.onload = function() {
    document.querySelector("input").addEventListener("click",textarea2storage);
    storage2textarea();
}
