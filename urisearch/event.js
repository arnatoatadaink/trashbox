import {load_settings} from "./background_util.js"
// import {load_settings,do_domain,send_urltab} from "./background_util.js"

function set_menuid(title,id){
    // 右クリックメニューを生成
    chrome.contextMenus.create({
        type: "normal",
        id: id,
        title: title,
        contexts: ["selection"],
    });
}

export function update_rightclick(){
    load_settings("default",(settings) => {
        chrome.contextMenus.removeAll();
        if( !("urls" in settings) ){
            return;
        }
        for( var i = -1; ++i < settings.urls.length; ){
            var title = settings.urls[i].title;
            var url   = settings.urls[i].url;
            if( title && url ){
                set_menuid(title,i.toString());
            }
        }
    });
}

// ブラウザ起動時に同時に実行される処理
chrome.runtime.onInstalled.addListener(update_rightclick);

// コンテキストメニュークリック時に起動する処理
chrome.contextMenus.onClicked.addListener((info,tab) => {
    load_settings("default",(settings) => {
        chrome.tabs.sendMessage(tab.id, {url:settings.urls[info.menuItemId].url});
    });
});
