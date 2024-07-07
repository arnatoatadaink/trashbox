// ブラウザ起動時に同時に実行される処理
chrome.runtime.onInstalled.addListener(function(){
  // 右クリックメニューを生成
  const parent_menu = chrome.contextMenus.create({
    type: "normal",
    id: "urlscan_vt",
    title: "urlscan_vt",
    // contexts: ["link"],
    contexts: ["all"],
  });

});

// コンテキストメニュークリック時に起動する処理
chrome.contextMenus.onClicked.addListener(function(info,tab) {	
    chrome.tabs.sendMessage(tab.id, {}).catch(()=>{});
});
