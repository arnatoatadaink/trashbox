function makeStorageFunctions(storage,name){
    // 情報の取得
    function load_storage(domain){
        let value = storage.getItem(domain+name);
        if( value != null ){
            value = JSON.parse(value);
        }else{
            value = {}
        }
        return value;
    }

    // 情報の登録
    function save_storage(domain,value){
        storage.setItem(domain+name,JSON.stringify(value));
    }

    function update_storage(domain,value){
        var oldvalue = load_storage(domain);
        var value = Object.assign(oldvalue,value);
        save_storage(domain,value);
    }

    function delete_storage(domain,keys){
        if( keys == null || keys == "" ){
            var newvalue = {}
        }else{
            if( typeof keys == "string" ){
                keys = [keys];
            }
            var newvalue = load_storage(domain);
            for( let i = 0; i < keys.length; i++ ){
                delete(newvalue[keys[i]]);
            }
        }
        save_storage(domain,newvalue);
    }

    return [load_storage,
             save_storage,
             update_storage,
             delete_storage];
}

const funcs = makeStorageFunctions(window.localStorage,"_info");
const load_info   = funcs[0];
const save_info   = funcs[1];
const update_info = funcs[2];
const delete_info = funcs[3];

export { load_info,save_info,update_info,delete_info  }