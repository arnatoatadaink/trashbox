import {generate_uuidv4} from './util.js';
import {PostRequest} from './connect.js';

// class LogHandler{
//     
//     constructor(target){
//         
//     }
//     
//     set_log(log){
//         var message_view = document.getElementById("message_view");
//         var div = document.createElement("div"); // make_div();
//         div.innerHTML = log;
//         message_view.insertBefore(div, message_view.firstChild);
//         return div;
//     }
// 
//     update_log(elm,log){
//         elm.innerHTML = log;
//     }
// 
// }

const STATUS = Object.freeze({
    UNSEND    : Symbol(0),
    SENDING   : Symbol(1),
    SUCCEEDED : Symbol(2),
    RETRY     : Symbol(3),
    ERROR     : Symbol(3),
});

const POLL_SLEEP_TIME_ms  = 3000;
const POLL_RETRY_COUNT    = 5;

class Sender {
    constructor(){
        this.intervalID = null;
        this.interval   = POLL_SLEEP_TIME_ms;
        this.retry      = POLL_RETRY_COUNT;
        this.sendvalues = {};
        this.sendarray  = [];
        this.send_count = 0;
    }
    
    set(url:str,query:dict,values:dict,token:str,regkey:str=undefined){
        
        if( !this.sendarray.includes(regkey) ){
            regkey = generate_uuidv4()
            this.sendarray.push(regkey);
        }
        const senditem = {
            "status"  : STATUS.UNSEND,
            "url"     : url,
            "query"   : query,
            "token"   : token,
            "headers" : "",
            "retry"   : this.retry,
            "body"    : values,
            "log"     : null,
            "suc_func":()=>{
                senditem["status"] = STATUS.SUCCEEDED;
                delete this.sendvalues[regkey];
                this.send_count--;
                this.set_log(senditem);
            },
            "err_func":()=>{
                if( senditem["retry"] > 0 ){
                    senditem["status"] = STATUS.RETRY;
                    senditem["retry"] -= 1;
                    this.sendarray.push(regkey);
                }else{
                    senditem["status"] = STATUS.ERROR;
                    delete this.sendvalues[regkey];
                    this.send_count--;
                }
                this.set_log(senditem);
            }
        };
        this.sendvalues[regkey] = senditem;
        
        if( this.intervalID == null ){
            this.intervalID = setInterval(()=>{this.poll()},this.interval);
        }
        return regkey;
    }
    set_log(senditem){

        const key = "";
        let log_value = "";
        switch (senditem["STATUS"]){
            case STATUS.UNSEND:
                log_value = "set sender : "+key;
                break
            case STATUS.SENDING:
                log_value = "sending : "+key;
                break
            case STATUS.SUCCEEDED:
                log_value = "post succeeded key : "+key;
                break
            case STATUS.RETRY:
                log_value = "post retry "+senditem["RETRY"]+" key : "+key;
                break
            case STATUS.ERROR:
                log_value = "post error key : "+key;
                break
            default:
        }
        if( senditem["log"] ){
            senditem["log"](log_value,senditem);
        }else{
            console.log(log_value,senditem);
        }
    }
    poll(){
        if( this.sendarray.length === 0 && this.send_count <= 0 ){
            clearInterval(this.intervalID);
            this.intervalID = null;
            return;
        }
        const regkey      = this.sendarray.shift();
        const senditem    = this.sendvalues[regkey];
        const url         = senditem["url"];
        const query       = senditem["query"];
        const token       = senditem["token"];
        const headers     = senditem["headers"];
        const body        = senditem["body"];
        const suc_func    = senditem["suc_func"];
        const err_func    = senditem["err_func"];
        const post        = new PostRequest(url,token,headers,query,
                                             body,suc_func,err_func);
        this.send_count  += senditem["status"] === STATUS.UNSEND;
        senditem["status"] = STATUS.SENDING;
        post.request();
    }
}
export default new Sender();