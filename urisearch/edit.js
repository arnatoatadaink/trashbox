function textarea2storage(){
    const datas = JSON.parse(document.querySelector("textarea").value);
    chrome.storage.local.clear().then(
        ()=>chrome.storage.local.set(datas));
    chrome.storage.session.clear().then(
        ()=>chrome.storage.session.set(datas));
}

function storage2textarea(){
    chrome.storage.local.get(null,function(storage){
        document.querySelector("textarea").value = JSON.stringify(storage);
    });
}

// ページ読み込み時の処理
window.onload = function() {
    document.querySelector("input").addEventListener("click",textarea2storage);
    storage2textarea();
}
