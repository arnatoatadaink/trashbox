function conv_url(url){
    if( url == null ){
        url = document.URL;
    }
    var split_url = url.split("/");
    var page = split_url.slice(3,split_url.length).join("/");
    return {domain:split_url[2],page:page}
}

function send_activate(){
    var request = {
        domain : conv_url(document.URL).domain,
        url    : document.URL,
    };
    chrome.runtime.sendMessage(request);
}

function set_zoom(request){
    var urlinfo = conv_url();
    var page    = decodeURIComponent(urlinfo["page"]);
    // 対象のテキストを確認
    var zoom     = request["default"]["zoom"];
    var matches  = request["matches"]?request["matches"]:{};
    var keys     = Object.keys(matches);
    for( var i = -1; ++i < keys.length; ){
        var key  = keys[i];
        var full = matches[key]["full"];
        var selector = matches[key]["selector"]?matches[key]["selector"]:"*";
        if( page.search(RegExp(key)) == -1 ){
            continue;
        }else if( !document.querySelector(selector) ){
            continue;
        }else if( full&&!is_full() ){
            continue;
        }
        zoom = matches[key]["zoom"];
        break;
    }
    if( zoom ){
        if( zoom == 100 ){
            document.body.style.zoom = "";
        }else{
            document.body.style.zoom = (""+zoom*0.01);
        }
    }
}

// content starter
send_activate();
window.addEventListener("visibilitychange",send_activate);
window.addEventListener("locationchange",send_activate);
window.addEventListener('hashchange',send_activate);
window.addEventListener('popstate',send_activate);
window.addEventListener('pageshow',send_activate);
window.addEventListener('resize',send_activate);
window.addEventListener('onload',send_activate);
window.addEventListener('load',send_activate);
window.addEventListener('DOMContentLoaded',send_activate);
document.addEventListener("resize",send_activate);
chrome.runtime.onMessage.addListener(set_zoom);

// 変更が発見されたときに実行されるコールバック関数
const callback = function(mutationsList, observer) {
    const head = document.querySelector("head");
    if( head ){ return }
    send_activate();
    console.log("observe html",mutationsList);
    observer.disconnect()
};

// コールバック関数に結びつけられたオブザーバーのインスタンスを生成
const observer = new MutationObserver(callback);

// (変更を監視する) オブザーバーのオプション
const config = {
    attributes: false,
    childList : true ,
    subtree   : false
};

window.addEventListener('load',()=>{
    // 対象ノードの設定された変更の監視を開始
    const html = document.querySelector("html");
    observer.observe(html, config);
});
