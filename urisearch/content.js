chrome.runtime.onMessage.addListener(function(request) {
    
    if( !("url" in request) ){
        return true;
    }
    
    if( !request.url ){
        return true;
    }
    
    // 対象のテキストを確認
    let selected = window.getSelection().toString();
    // テキストを選択していない
    if( selected == "" ){
        return true;
    }
    if( [...selected.matchAll(/[^\r\n 　]+/g)].length == 0 ){
        return true;
    }
    let url = request.url;
    if( !request.url.match("{}") ){
        url += "{}";
    }
    
    const enc = request.enc?true:false;
    if( enc ){
        selected = encodeURIComponent(selected);
    }
    
    url = url.replace("{}", selected);
    window.open(url, '_blank',"");
});