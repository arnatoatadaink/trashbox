import {check_limit} from './util.js';

export function data2urlencode(args){
    const arr = [];
    for( let key in args ){
        const enc_key = encodeURIComponent(key);
        const enc_arg = encodeURIComponent(args[key]);
        arr.push([enc_key,enc_arg].join("="));
    }
    return arr.join("&");
}

export function get_searchurl(url,args){
    const query    = data2urlencode(args);
    const join_key = url.indexOf("?") === -1?"?":"&";
    const arr      = query === ""?[url]:[url,query];
    return arr.join(join_key);
}

// call back steps
//   シングルプロセスの手続き型処理は上から下に続くが
//   マルチプロセスの非同期関数型処理の場合、事前処理、主処理、事後処理の三工程を常に配置する必要がある
//   　初期化
//   　事前処理
//   　主処理
//   　副処理（Actionなど内部処理）
//   　事後処理
export class CallBackSteps{
    static INIT_PROCESS = 0;
    static PRE_PROCESS  = 1;
    static MAIN_PROCESS = 2;
    static POST_PROCESS = 3;
    static END_PROCESS  = 4;
    constructor(){
        // console.log("init process");
        this.state = CallBackSteps.INIT_PROCESS;
    }
    PreProcess(){
        // console.log("pre process");
        this.state = CallBackSteps.PRE_PROCESS;
    }
    MainProcess(){
        // console.log("main process");
        this.state = CallBackSteps.MAIN_PROCESS;
    }
    PostProcess(){
        // console.log("post process");
        this.state = CallBackSteps.POST_PROCESS;
    }
    EndProcess(){
        // console.log("end process");
        this.state = CallBackSteps.END_PROCESS;
    }
}

class RestRequest {
    get_contenttype(){
        return "application/json";
    }
    constructor(url,token,method,headers,body,
                 suc_func,err_func,fin_func){
        this.suc_func = suc_func?suc_func:()=>{};
        this.err_func = err_func?err_func:()=>{};
        this.fin_func = fin_func?fin_func:()=>{};
        this.url      = url;
        if( !token ){
            token = "-";
        }
        const content_type = this.get_contenttype();
        if( body ){
            if( content_type === "application/json" ){
                body = {body: JSON.stringify(body)};
            }else if( content_type === "application/x-www-form-urlencoded"){
                body = {body: data2urlencode(body)};
            }else{
                body = {body: body};
            }
        }else{
            body = {};
        }
        const request = {
            method: method, // 'GET'・'POST'・'PUT'・'DELETE'
            headers: { 
                'Content-Type': content_type,
                'Accept': 'application/json',
                'Authorization': 'Bearer '+token,
                ...headers
            },
            credentials: "include",
            ...body
        }
        this.request_state = request
    }
    request(){
        // const response = await fetch(url, {
        //         method: 'POST', // *GET, POST, PUT, DELETE, etc.
        //         mode: 'cors', // no-cors, *cors, same-origin
        //         cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
        //         credentials: 'same-origin', // include, *same-origin, omit
        //         headers: {
        //             'Content-Type': 'application/json'
        //             // 'Content-Type': 'application/x-www-form-urlencoded',
        //         },
        //         redirect: 'follow', // manual, *follow, error
        //         referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
        //         body: JSON.stringify(data) // 本体のデータ型は "Content-Type" ヘッダーと一致させる必要があります
        //     })
        //     return response.json(); // JSON のレスポンスをネイティブの JavaScript オブジェクトに解釈
        // }
        // console.log("send",this.url)
        // console.log("status",this.request_state)
        fetch(this.url,this.request_state)
        .then((res)=>{
            console.log("response",res);
            if( check_limit(res.status,200,399) ){
                const response_type = res.headers.get("content-Type");
                if( response_type === "application/json" ){
                    res.json().then((data)=>this.suc_func(res,data));
                }else if( response_type.split(";")[0] === "text/html" ){
                    res.arrayBuffer().then((data)=>this.suc_func(res,data));
                }else{
                    res.text().then((data)=>this.suc_func(res,data));
                }
            }else{
                this.err_func(res);
            }
        })
        .catch((err)=>this.err_func(err))
        .finally(()=>this.fin_func())
    }
    // body: (...)
    // bodyUsed:true
    // headers:Headers {}
    // ok:true
    // redirected: false
    // status: 200
    // statusText: "OK"
    
}

// Fetch
// export class FormRequest extends RestRequest{
//     get_contenttype(){
//         return 'application/x-www-form-urlencoded'
//     }
//     set_body(body){
//         return data2urlencode(body)
//     }
// }

export class GetRequest extends RestRequest {
    constructor(url,token,headers,query,
            suc_func,err_func,fin_func){
        super(
            get_searchurl(url,query),
            token,"GET",
            headers,null,
            suc_func,err_func,fin_func)
    }
}

// export class GetRequest2 extends GetRequest {
//     constructor(url,token,headers,query,steps){
//         super(url,token,headers,query,
//             (...arg)=>{steps.MainProcess(...arg)},
//             (err)=>{console.log("err",new Date(),err)},
//             (...arg)=>{steps.PostProcess(...arg)});
//         this.steps = steps;
//     }
//     request(){
//         this.steps.PreProcess();
//         super.request();
//     }
// }
// 
// export class GetRequest3 extends GetRequest {
//     constructor(url,token,headers,query,steps){
//         super(url,token,headers,query,
//             (...arg)=>{steps.MainProcess(...arg)},
//             (...arg)=>{steps.MainProcess(...arg)},
//             (...arg)=>{steps.PostProcess(...arg)});
//         this.steps = steps;
//     }
//     request(){
//         this.steps.PreProcess();
//         super.request();
//     }
// }

export class PostRequest extends RestRequest {
    constructor(url,token,headers,query,body,
            suc_func,err_func,fin_func){
        super(
            get_searchurl(url,query),
            token,"POST",headers,body,
            suc_func,err_func,fin_func);
    }
}

export class PostRequestByForm extends PostRequest {
    get_contenttype(){
        return "application/x-www-form-urlencoded";
    }
}
// export class PostRequest2 extends PostRequest {
//     constructor(url,token,headers,body,steps){
//         super(
//             url,token,headers,body,
//             (...arg)=>{steps.MainProcess(...arg)},
//             (err)=>{console.log("err",new Date(),err)},
//             (...arg)=>{steps.PostProcess(...arg)});
//         this.steps = steps;
//     }
//     request(){
//         this.steps.PreProcess();
//         super.request();
//     }
// }
// 
// export class PostRequest3 extends PostRequest {
//     constructor(url,token,headers,body,steps){
//         super(
//             url,token,headers,body,
//             (...arg)=>{steps.MainProcess(...arg)},
//             (...arg)=>{steps.MainProcess(...arg)},
//             (...arg)=>{steps.PostProcess(...arg)});
//         this.steps = steps;
//     }
//     request(){
//         this.steps.PreProcess();
//         super.request();
//     }
// }

// // 認証に不安？
// class PutRequest extends RestRequest {
//     constructor(
//             url,
//             token,
//             headers,
//             body,
//             suc_func,
//             err_func,
//             fin_func){
//         super(
//             url,
//             token,
//             "PUT",
//             headers,
//             body,
//             suc_func,
//             err_func,
//             fin_func)
//     }
// }
// 
// // 認証に不安？
// class DeleteRequest extends RestRequest {
//     constructor(
//             url,
//             token,
//             headers,
//             query,
//             suc_func,
//             err_func,
//             fin_func){
//         super(
//             url + data2urlencode(query),
//             token,
//             "DELETE",
//             headers,
//             null,
//             suc_func,
//             err_func,
//             fin_func)
//     }
// }

// 管理の都合上一括りで実装したいデータ
export class LoadHundler {
    constructor(props){
        this.props = props;
        this.retry_count = props["retry_count"]?props["retry_count"]:5;
        this.retry_cycle = props["retry_cycle"]?props["retry_cycle"]:5000; // mill second
        this.time_out    = props["time_out"]   ?props["time_out"]   :60000; // mill second
    }
    load(){
        // load action
    }
    reload(){
        // check retry
        // load function
    }
    loaded(){
        // loaded action
    }
    retry(){
        
    }
    error(){
        // load error handling
    }
}
