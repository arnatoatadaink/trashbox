import {load_settings,do_domain,send_urltab} from "./background_util.js"

// // ブラウザ起動時に同時に実行される処理
// chrome.runtime.onInstalled.addListener(function(){
// 
//     // // 右クリックメニューを生成
//     // const parent_menu = chrome.contextMenus.create({
//     //     // type : "all",
//     //     id   : "open popup",
//     //     title: "open popup"
//     // });
// 
// });
// 
// // コンテキストメニュークリック時に起動する処理
// chrome.contextMenus.onClicked.addListener(function() {
//     // chrome.action.openPopup(); // future enabled manifest v3
// });

chrome.runtime.onMessage.addListener(function(request,sender,sendResponse){
    set_zoom(request.domain,request.url);
    return true;
});


function set_zoom(domain,url){
    function suc(settings) {
        if( Object.keys(settings).length == 0 ){
            settings = {"default":{"zoom":100,"selector":"*","full":false},"matches":[]}
        }
        send_urltab(settings,url);
    }
    load_settings(domain,suc);
}

export function update_zoom(){
    do_domain(set_zoom);
}

function send_cancel(domain,url){
    send_urltab({"default":{"zoom":100,"full":false},"matches":[]},url);
}

export function zoom_cancel2(){
    do_domain(send_cancel);
}
