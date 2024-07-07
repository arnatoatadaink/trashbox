// https%253A%252F%252Fsn-jp.com%252Farchives%252F74357
var mouseEvent = undefined;
document.addEventListener('contextmenu',function(e){mouseEvent = e;},true);

function check_select(){
    // 対象のテキストを確認
    const selected      = window.getSelection();
    const selected_text = selected.toString();
    // テキストを選択していない
    if( selected_text == "" ){
        return false;
    }
    if( [...selected_text.matchAll(/[^\r\n 　]+/g)].length == 0 ){
        return false;
    }
    if( [...selected_text.match(/^http/)].length == 0 ){
        return false;
    }
    return openurl(selected_text);
}

function check_item(item){
    let   targeturl = "";
    const item_parent = goback_overlay(item).closest("[href]");
    const item_child  = goback_overlay(item).querySelector("[href]");
    item = item_parent?item_parent:item;
    item = item_child?item_child:item;
    if( item.href ){
        const urlsplit = item.href.split("http");
        if( urlsplit.length == 1 ){
            targeturl = urlsplit[0];
        }else if( urlsplit.length == 2 ){
            targeturl = "http"+urlsplit[1];
        }else if( urlsplit.length >= 3 ){
            delete urlsplit[1];
            targeturl = decodeURIComponent(urlsplit.slice(1).join("http").split("&")[0].split("?")[0]);
        }
    }
    return openurl(targeturl);
}

function openurl(targeturl){
    if( targeturl !== "" ){
        const encodeUrl        = encodeURIComponent(targeturl);
        const dobble_encodeUrl = encodeURIComponent(encodeUrl);
        const url = "https://www.virustotal.com/gui/search/"+dobble_encodeUrl;
        window.open(url, "_blank","");
        return true;
    }else{
        return false;
    }
}

function get_clientrect(target){
    // return {
    //     w:target.clientWidth,
    //     h:target.clientHeight,
    //     l:target.clientLeft,
    //     t:target.clientTop,
    // }
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

chrome.runtime.onMessage.addListener(function(request) {
    if( check_select() ){
        return true;
    }
    
    if( check_item(mouseEvent.target) ){
        return true;
    }
    const items = mouseEvent.target.querySelectorAll("[href]");
    for( var i = 0; i < items.length; i++ ){
        if( check_item(items[i]) ){
            return true;
        }
    }
    const item = mouseEvent.target.closest("[href]");
    if( check_item(item) ){
        return true;
    }
    return false;
});