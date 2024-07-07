//#define DEBUG
#if defined(DEBUG)
#define DEBUG_PRINT(...) printf(__VA_ARGS__)
#else
#define DEBUG_PRINT(...)
#endif

#define SAFE_DELETE(a) if(a!=NULL){free(a);a=NULL;}
#define SIZE_ARRAY(a,b) (sizeof(a)/sizeof(b))

#define TRAY_WINAPI 1
#include "wintray.h"

#include <windows.h>
#include <stdio.h>
#include <sysinfoapi.h>
#include <math.h>
// #include "str_map.h"
#include <map>
#include <string>

// 記号定数
#define ID_TRAYICON     (1)                 // 複数のアイコンを識別するためのID定数
#define WM_TASKTRAY     (WM_APP + 1)        // タスクトレイのマウス・
#define CHILD_ID_FIRST  100

#define WINDOW_X 480
#define WINDOW_Y 200
#define CLIENT_X 220
#define CLIENT_Y 210

LRESULT CALLBACK WndProc(
    HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam);
void hidewindow(HWND hwnd);
void printWM(int msg);

void show(tray_menu *,HWND);                // 更新画面表示
void finish(tray_menu *,HWND);              // 終了処理
tray tray_val = {                           // タスクトレイの設定
  TEXT("CLICKICON"),                        // タスクトレイのアイコン画像。別途用意しておく。
  (tray_menu[]){
    {"show",0,0,show},   //サブメニューを指定すれば、階層化も可能
    {"-"},                           // セパレータ
    {"exit",0,0,finish},             // 終了
    {NULL}                                  // 最後の要素。必須。
  }
};

typedef enum{
     LABEL
    ,EDIT
    ,NUMEDIT
    ,BUTTON
    ,RADIO
    ,CHECK
    ,CHECK3
    ,GROUP
    ,COMBO
    ,LIST
//    ,TEST1
} control_type;

typedef struct{
    const char* type;
    DWORD style;
} control_type_set;

control_type_set type_val[] = {
/*LABEL  */ {"static"  ,0                 }
/*EDIT   */,{"edit"    ,WS_BORDER         }
/*NUMEDIT*/,{"edit"    ,WS_BORDER|ES_NUMBER|ES_RIGHT}
/*BUTTON */,{"button"  ,BS_PUSHBUTTON     }
/*RADIO  */,{"button"  ,BS_AUTORADIOBUTTON}
/*CHECK  */,{"button"  ,BS_AUTOCHECKBOX   }
/*CHECK3 */,{"button"  ,BS_AUTO3STATE     }
/*GROUP  */,{"static"  ,BS_GROUPBOX       }
/*COMBO  */,{"combobox",0                 }
/*LIST   */,{"listbox" ,0                 }
//,{"status",0                   }
//,{"tooltip",0                  }
//,{"up-down",0                  }
//,{"toolbars",0                 }
//,{"rebar",0                    }
//,{"header",0                    }
//,{"ipaddress",0                    }
//,{"progress",0                    }
//,{"listview",0                    }
//,{"progressbar",0                    }
};

typedef struct controls{
  const char *name;
  const char *refname;
  const char *text;
  control_type type;
  int posx;
  int posy;
  int width;
  int height;
  int group;
  int checked;
  void (*cb)(struct controls*,HWND parent);
  void *context;
  HWND mine;
  HWND ref;
} controls;

int set_controls(HWND,HINSTANCE,controls*);
int get_control_callback(DWORD wparam,DWORD lparam,HWND root);

void button_save(struct controls*,HWND); // test call back

int BRUSH_COLOR = 0xEEEEEE;

#define NO_GROUP     -1
#define RADIO_GROUP1 0
controls* get_controls(){
    static controls controls_val[] = {
        {"テキスト"      ,NULL,"押下間隔"            ,LABEL  , 20, 10, 80,25,NO_GROUP    ,0,NULL,NULL},
        {"押下間隔"      ,NULL,""                    ,NUMEDIT,100, 10, 60,25,NO_GROUP    ,0,NULL,NULL},
        {"テキスト"      ,NULL,"押下時間"            ,LABEL  , 20, 40, 80,25,NO_GROUP    ,0,NULL,NULL},
        {"押下時間"      ,NULL,""                    ,NUMEDIT,100, 40, 60,25,NO_GROUP    ,0,NULL,NULL},
        {"押している間"  ,NULL,"押している間"        ,RADIO  , 20, 70,120,25,RADIO_GROUP1,0,NULL,NULL},
        {"押して切り替え",NULL,"押して切り替え"      ,RADIO  , 20,100,140,25,RADIO_GROUP1,0,NULL,NULL},
        {"保存して閉じる",NULL,"保存/更新して閉じる" ,BUTTON , 15,130,175,25,NO_GROUP    ,0,button_save,NULL},
//        {"",NULL,"TEST1" ,TEST1,  120, 30,80,25,NO_GROUP    ,0,button_save,NULL},
        NULL
    };
    return controls_val;
}

void scroll_update(HWND hwnd,DWORD wp,DWORD lp);
void load(HWND hwnd);
void save(HWND hwnd);
void press_control(HWND hwnd);
void click_control(HWND hwnd);
int  down_control(HWND hwnd);
int  up_control(HWND hwnd);
void raw_control(HWND hwnd,RAWINPUT* input);

#define PRESS_CONTROL  1
#define CLICK_CONTROL  2
#define DOWN_CONTROL   3
#define UP_CONTROL     4
#define SET_UP_CONTROL 5
#define CYCLE_COUNT (int)(1000/30)
#define KEY_FREE    0
#define KEY_DOWN    1
#define KEY_UP      2
#define KEY_HOLD    3
#define KEY_MAX 256
#define HOLD_CLICK   0
#define SWITCH_CLICK 1
#define UPDATE_STATE(a,b) (a)<<1&3|(b)&1
#define KEY_RAW 3
#define SEND_PROGRAM 1

int retry_time = 90;
int press_time = 10;
int start_type = 0;
int auto_state = 0;
int button_state[KEY_MAX];
int raw_state[KEY_RAW];
const int RAW_MAP[] = {
    VK_LBUTTON,
    VK_RBUTTON,
    VK_MBUTTON
};

const int CHECK_FLG_SHIFT[] = {
    0,//RI_MOUSE_LEFT_BUTTON_DOWN,
    2,//RI_MOUSE_RIGHT_BUTTON_DOWN,
    4 //RI_MOUSE_MIDDLE_BUTTON_DOWN,
};

#define SWITCH_RAWKEY(a,b,c) (a&~b>>c+1|1&b>>c)
// 使用している記号の計算順序
// ~ + >> & |
//a|1&b>>c   // bが1の場合、aが1になる
//a=0,b=0,c=0 r=0
//a=1,b=0,c=0 r=1
//a=0,b=1,c=0 r=1
//a=1,b=1,c=0 r=1
//a&~b>>c+1 // bが2の場合、aが0になる
//a=0,b=0,c=0 r=0
//a=1,b=0,c=0 r=1
//a=0,b=2,c=0 r=0
//a=1,b=2,c=0 r=0

int WINAPI WinMain(
    HINSTANCE hInstance, HINSTANCE hPrevInstance,
    LPSTR lpszCmdLine, int nCmdShow)
{
    WNDCLASSEX wc;
    HWND hwnd;
    MSG msg;
    
    memset(button_state,0,sizeof(button_state));
    memset(raw_state,0,sizeof(raw_state));
    memset(&wc, 0, sizeof(wc));
    wc.cbSize = sizeof(WNDCLASSEX);
    
    wc.style         = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc   = WndProc;
    wc.hInstance     = hInstance;
    wc.hIcon         = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor       = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)CreateSolidBrush(BRUSH_COLOR);
    wc.lpszMenuName  = NULL;

    wc.lpszClassName = WC_TRAY_CLASS_NAME;
    if (!RegisterClassEx(&wc)) {
        return -1;
    }

    hwnd = CreateWindowEx(
        WS_EX_CLIENTEDGE|
        WS_EX_WINDOWEDGE,               // ExStyle
        WC_TRAY_CLASS_NAME,             // WindowCls
        TEXT(""),                       // WindowName
        WS_OVERLAPPEDWINDOW,            // Style
        WINDOW_X, WINDOW_Y,   // x,y pos
        CLIENT_X, CLIENT_Y,   // x,y size
        NULL,                           // parent window
        NULL,                           // menu handle
        hInstance,                      // instance handle
        NULL);                          // add param pointer
        
    {
        //RAWINPUTDEVICE rid[2]{};
        RAWINPUTDEVICE rid[1]{};
        // mouse
        rid[0].usUsagePage = 0x01;
        rid[0].usUsage = 0x02;
        rid[0].dwFlags = RIDEV_INPUTSINK;
        rid[0].hwndTarget = hwnd;
        //// keyboard
        //rid[1].usUsagePage = 0x01;
        //rid[1].usUsage = 0x06;
        //rid[1].dwFlags = RIDEV_INPUTSINK;
        //rid[1].hwndTarget = hwnd;
        if( !RegisterRawInputDevices(rid, SIZE_ARRAY(rid,RAWINPUTDEVICE), sizeof(RAWINPUTDEVICE)) ){
            return 0;
        }
    }
    
    // トレイの設定
    hwnd = tray_init(&tray_val,hInstance,hwnd); //タスクトレイに登録
    if (!hwnd) return 0;

    //ボタンコントロール作成
    if( !set_controls(hwnd,hInstance,get_controls()) ){
        return 0;
    }
    
    load(hwnd);

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    //SetTimer(hwnd,PRESS_CONTROL,CYCLE_COUNT,NULL);
    
    while( GetMessage(&msg, NULL, 0, 0) > 0 ){
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
//    while( 1 ){
//        while( PeekMessage(&msg, hwnd,  0, 0, PM_REMOVE) > 0 ){
//            TranslateMessage(&msg);
//            DispatchMessage(&msg);
//        }
//        if( msg.message == WM_QUIT ){
//            break;
//        }
//    }
    
    //KillTimer(hwnd,PRESS_CONTROL);

    DeleteObject(wc.hbrBackground);
    
    UnregisterClass(WC_TRAY_CLASS_NAME,hInstance);

    return msg.wParam;
}

LRESULT CALLBACK WndProc(
    HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam)
{
//    printWM(uMsg);
    if( !getTrayMessage(hwnd,uMsg,wParam,lParam) ){
        return 0;
    }else if( uMsg == WM_COMMAND ){
        DEBUG_PRINT("GET COMMAND wp %d lp %d\r\n",wParam,lParam); // wParam == ID lParam == item handle
        if( wParam >= CHILD_ID_FIRST ){
            get_control_callback(wParam,lParam,hwnd);
        }
    }else if( uMsg == WM_CLOSE ){
        hidewindow(hwnd); //非表示にする場合
        return 1;
    }else if( uMsg == WM_KEYDOWN ){
        if ( wParam == VK_ESCAPE ){
#ifdef DEBUG
            tray_exit();  // タスクトレイから削除
            return 0;
#else
            hidewindow(hwnd); //非表示にする場合
#endif
        }else{
            DEBUG_PRINT("key down %d\r\n",wParam);
        }
    }else if( uMsg == WM_MOUSEWHEEL ){
        scroll_update(hwnd,wParam,lParam);
        return 1;
    }else if( uMsg == WM_INPUT ) {
        int i;
        RAWINPUT  input;
        HRAWINPUT hRawInput    = (HRAWINPUT)lParam;
        UINT      dw_size      = 0;

        // プログラムから送られた場合、これを無視する
        if( GetMessageExtraInfo() != SEND_PROGRAM ){
            GetRawInputData(hRawInput, RID_INPUT, NULL, &dw_size, sizeof(RAWINPUTHEADER));
            if( dw_size == sizeof(RAWINPUT) ){
                GetRawInputData(hRawInput, RID_INPUT, &input, &dw_size, sizeof(RAWINPUTHEADER));
                raw_control(hwnd,&input);
            }else{
                DEBUG_PRINT("dw size error dw : %d sizeof : %d\r\n",dw_size,sizeof(RAWINPUT));
            }
        }
    }else if( uMsg == WM_TIMER ){
        if(wParam == PRESS_CONTROL){
            press_control(hwnd);
        }else if( wParam == CLICK_CONTROL ){
            click_control(hwnd);
        }else if( wParam == DOWN_CONTROL ){
            if( down_control(hwnd) ){
                return 1;
            }
        }else if( wParam == UP_CONTROL ){
            if( up_control(hwnd) ){
                return 1;
            }
        }else if( wParam == SET_UP_CONTROL ){
            SetTimer( hwnd,UP_CONTROL,retry_time+press_time,NULL);
            KillTimer(hwnd,SET_UP_CONTROL);
        }
    }
    
    return DefWindowProc(hwnd, uMsg, wParam, lParam);
}

void show(tray_menu * item,HWND hwnd){
    //表示する場合
    if( GetWindowLong(hwnd, GWL_EXSTYLE) & WS_EX_TOOLWINDOW ){
        SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) & ~WS_EX_TOOLWINDOW);
        ShowWindow(hwnd, SW_SHOW);
    }
}

void finish(tray_menu * item,HWND hwnd){
    tray_exit();
}

int set_controls(HWND hwnd,HINSTANCE hInstance,controls* cont){

    int groupid = -1;
    // str_map<HWND> mp;
    std::map<std::string,HWND> mp;
    controls* cont_base = cont;
    union {
        int intid;
        void* pid;
    } id;
    id.intid = CHILD_ID_FIRST;
    for(;cont != NULL && cont->name != NULL;cont++,id.intid++){
        
        DWORD set_group = WS_GROUP * ( groupid != cont->group );
        control_type_set usetype = type_val[cont->type];
        
        cont->mine = CreateWindow(
            usetype.type,                             // WindowCls
            cont->text,                             // WindowName
            WS_VISIBLE | WS_CHILD |                 // base style
            usetype.style | set_group,                // Style
            cont->posx, cont->posy,                 // x,y pos
            cont->width, cont->height,              // x,y size
            hwnd,                                   // parent window
            (HMENU)id.pid,                          // menu handle
            hInstance,                              // instance handle
            NULL);                                  // add param pointer
            
        groupid = cont->group;
        
        if( !cont->mine ){
            return 0;
        }
        cont->ref = NULL;
        mp[cont->name] = cont->mine;
    }
    for(cont = cont_base;cont != NULL && cont->name != NULL;cont++){
        if( cont->refname == NULL ){ continue; }
        // auto itr = mp.find(cont->refname);
        // if( itr != mp.end() ){
        // auto refval = mp[cont->refname];
        // printf("%x",refval);
        // if( refval != NULL ){
        //     cont->ref = refval;
        // }
        cont->ref = mp[cont->refname];
    }

    return 1;
}

int get_control_callback(DWORD wParam,DWORD lParam,HWND root){
    auto cont = get_controls()+(wParam-CHILD_ID_FIRST);
    if( cont->cb != NULL ){
        cont->cb(cont,root);
    }
    return 0;
}

void readsettingfile(int* retry_time,int* press_time,int* start_type){
    FILE *fp;  /* ファイルポインタの宣言 */
    char s[256];
    if ((fp = fopen("init.txt", "r")) == NULL) {  /* ファイルのオープン */
        DEBUG_PRINT("file open error!!\n");
        return;
    }
    fscanf(fp,
        "retry_time:%d\r\npress_time:%d\r\nstart_type:%d",
        retry_time,press_time,start_type);
    fclose(fp);  /* ファイルのクローズ */

    DEBUG_PRINT("readed\r\n");
    DEBUG_PRINT("retry %d\r\n",*retry_time);
    DEBUG_PRINT("press %d\r\n",*press_time);
    DEBUG_PRINT("start type %d\r\n",*start_type);
}

void writesettingfile(int retry_time,int press_time,int start_type){
    FILE *fp;  /* ファイルポインタの宣言 */
    if ((fp = fopen("init.txt", "w")) == NULL) {  /* ファイルのオープン */
        DEBUG_PRINT("file open error!!\n");
        return;
    }
    /* fprintf()による出力 */
    fprintf(fp, "retry_time:%d\r\n", retry_time);
    fprintf(fp, "press_time:%d\r\n", press_time);
    fprintf(fp, "start_type:%d", start_type);
    fclose(fp);  /* ファイルのクローズ */

    DEBUG_PRINT("writed\r\n");
    DEBUG_PRINT("retry %d\r\n",retry_time);
    DEBUG_PRINT("press %d\r\n",press_time);
    DEBUG_PRINT("start type %d\r\n",start_type);
}


#define OFFSET_X 8
void scroll_update(HWND hwnd,DWORD wp,DWORD lp){
    controls* cont = get_controls();
    char strbuffer[32];
    int bufsize = sizeof(strbuffer);
    int mousex = lp&0xffff;
    int mousey = (lp>>16)&0xffff;
    float zd = (float)(GET_WHEEL_DELTA_WPARAM(wp));
    zd = zd / WHEEL_DELTA;
    
    POINT pos = {0,0};
    ClientToScreen(hwnd, (LPPOINT)&pos);
    mousex -= pos.x;
    mousey -= pos.y;
    
    DEBUG_PRINT("z:%f x:%d y:%d cl:%d ct:%d\r\n",
        zd,mousex,mousey,
        pos.x,pos.y);
    
    for(;cont != NULL && cont->name != NULL;cont++){
        if( cont->name == "押下時間" ||
                cont->name == "押下間隔"  ){
            // check rect on target
            if( mousex < cont->posx  ||
                    mousey < cont->posy  ||
                    mousex > cont->posx + cont->width + OFFSET_X ||
                    mousey > cont->posy + cont->height ){
                continue;
            }
            // 60で7文字入るため、8point毎に1桁増える、4桁が最大
            // check move point
            int size = std::min(3,( cont->posx + cont->width + OFFSET_X - mousex ) / 8);
            // check move value
            int movesize = (int)(powf(10.0,(float)size)*zd);
            int intbuf = 0;

            GetWindowText(cont->mine,strbuffer,bufsize);
            sscanf(strbuffer,"%d",&intbuf);
            // add and limit
            intbuf += movesize;
            intbuf  = std::min(999999,std::max(10,intbuf));
            sprintf(strbuffer,"%d",intbuf);
            SetWindowText(cont->mine,strbuffer);
            break;
        }
    }
}

void load(HWND hwnd){
    controls* cont = get_controls();
    char strbuffer[32];
//    int retry_time = 90;
//    int press_time = 10;
//    int start_type = 0;
    
    readsettingfile(&retry_time,&press_time,&start_type);
    
    for(;cont != NULL && cont->name != NULL;cont++){
        if( cont->name == "押下間隔" ){
            sprintf(strbuffer,"%d",retry_time);
            SetWindowText(cont->mine,strbuffer);
        }else if( cont->name == "押下時間" ){
            sprintf(strbuffer,"%d",press_time);
            SetWindowText(cont->mine,strbuffer);
        }else if( cont->name == "押している間" && start_type == HOLD_CLICK ){
            SendMessage(cont->mine, BM_SETCHECK , (WPARAM) 1, TRUE);
        }else if( cont->name == "押して切り替え" && start_type == SWITCH_CLICK ){
            SendMessage(cont->mine, BM_SETCHECK , (WPARAM) 1, TRUE);
        }
    }
}

void save(HWND hwnd){
    controls* cont = get_controls();
    char strbuffer[32];
    int bufsize = sizeof(strbuffer);
//    int retry_time = 90;
//    int press_time = 10;
//    int start_type = 0;
    
    for(;cont != NULL && cont->name != NULL;cont++){
        if( cont->name == "押下間隔" ){
            GetWindowText(cont->mine,strbuffer,bufsize);
            sscanf(strbuffer,"%d",&retry_time);
        }else if( cont->name == "押下時間" ){
            GetWindowText(cont->mine,strbuffer,bufsize);
            sscanf(strbuffer,"%d",&press_time);
        }else if( cont->name == "押している間" ){
            if ( SendMessage(cont->mine, BM_GETCHECK, 0, 0) == BST_CHECKED){
                start_type = 0;
            }
        }else if( cont->name == "押して切り替え" ){
            if ( SendMessage(cont->mine, BM_GETCHECK, 0, 0) == BST_CHECKED){
                start_type = 1;
            }
        }
    }

    writesettingfile(retry_time,press_time,start_type);
}

void button_save(struct controls* control,HWND root){
    save(root);
    hidewindow(root);
}

void press_control(HWND hwnd){
    int old_state[] = {
        button_state[VK_LBUTTON],
        button_state[VK_RBUTTON],
        auto_state,
    };
    // all vkeys update
    {
        int i = - 1;
        for(;++i<KEY_MAX;){
            button_state[i] = UPDATE_STATE(button_state[i],(GetKeyState(i)&-128)<0);
        }
    }
    // set raw keys state
    {
        int i = -1;
        for( ;++i<KEY_RAW; ){
            // button_stateの第一フラグは常に0に設定し
            // raw_stateの第一フラグを設定する
            button_state[RAW_MAP[i]] = button_state[RAW_MAP[i]]&~1|raw_state[i];
        }
    }
        
    // auto click state update
    {
        int key_auto = 0;
        if( start_type == HOLD_CLICK ){
            key_auto = button_state[VK_LBUTTON]
                     + button_state[VK_RBUTTON]
                     == KEY_HOLD * 2;
        }else if( start_type == SWITCH_CLICK ){
            if( button_state[VK_LBUTTON]
                + button_state[VK_RBUTTON]
                == KEY_HOLD + KEY_DOWN ){
                key_auto = ~auto_state&1;
            }else{
                key_auto = auto_state&1;
            }
        }
        
        auto_state = UPDATE_STATE(auto_state,key_auto);
    }
    
    if( old_state[0] != button_state[VK_LBUTTON] ||
            old_state[1] != button_state[VK_RBUTTON] ||
            old_state[2] != auto_state ){
        DEBUG_PRINT(
            "L %d , R %d , A %d\r\n",
            button_state[VK_LBUTTON],
            button_state[VK_RBUTTON],
            auto_state);
    }
        
    
    // 指定されている間隔でクリック
    if( auto_state == KEY_DOWN ){
        SetTimer( hwnd,DOWN_CONTROL,retry_time+press_time,NULL);
        SetTimer( hwnd,SET_UP_CONTROL,press_time,NULL);
//    }else if( auto_state == KEY_UP ){
//        KillTimer(hwnd,CLICK_CONTROL);
    }

    
}

void send_leftbutton_event(DWORD msg){
    POINT pos;
    DWORD wp = 0;
    DWORD lp = 0;
    wp |= ( button_state[VK_MBUTTON] == KEY_HOLD ) * MK_MBUTTON; // 中央ボタンが押されている
    wp |= ( button_state[VK_RBUTTON] == KEY_HOLD ) * MK_RBUTTON; // 右ボタンが押されている
    wp |= ( button_state[VK_SHIFT  ] == KEY_HOLD ) * MK_SHIFT;   // Shift キーが押されている
    wp |= ( button_state[VK_CONTROL] == KEY_HOLD ) * MK_CONTROL; // Ctrl キーが押されている
    GetCursorPos(&pos);
    lp |= pos.x;
    lp |= pos.y << 16;

    //
#define TEST_SENDMOUSE

#if defined(TEST_POSTBROAD)
    // Mouseでフォーカスしている画面を調査し
    // 対象のクライアント座標を計算して
    // それに対してクリックを送信する必要がある
    DEBUG_PRINT("TEST_POSTBROAD ");
    PostMessage(HWND_BROADCAST, msg, wp, lp); // タスクバー近傍で動作する
#elif defined(TEST_POSTNULL)
    DEBUG_PRINT("TEST_POSTNULL ");
    PostMessage(NULL, msg, wp, lp); // 止まらず流れる、何も起きない
#elif defined(TEST_DEFBROAD)
    DEBUG_PRINT("TEST_DEFBROAD ");
    DefWindowProc(HWND_BROADCAST, msg, wp, lp); // 止まらず流れる、何も起きない
#elif defined(TEST_DEFNULL)
    DEBUG_PRINT("TEST_DEFNULL ");
    DefWindowProc(NULL, msg, wp, lp); // 止まらず流れる、何も起きない
#elif defined(TEST_SENDBROAD)
    DEBUG_PRINT("TEST_SENDBROAD ");
    SendMessage(  // 固まる
        HWND_BROADCAST,
        msg,wp,lp);
#elif defined(TEST_SENDNULL)
    DEBUG_PRINT("TEST_SENDNULL ");
    SendMessage( // 止まらず流れる、何も起きない
        NULL,
        msg,wp,lp);
#elif defined(TEST_SENDKEY)
    DEBUG_PRINT("TEST_SENDKEY ");
    INPUT inputs[1] = {};// Loop上のステータスだけ解除される
    ZeroMemory(inputs, sizeof(inputs));

    inputs[0].type       = INPUT_KEYBOARD;
    inputs[0].ki.wVk     = VK_LBUTTON;
    inputs[0].ki.dwFlags = KEYEVENTF_KEYUP * (msg==WM_LBUTTONUP);
    inputs[0].ki.dwExtraInfo = SEND_PROGRAM;

    UINT uSent = SendInput(ARRAYSIZE(inputs), inputs, sizeof(INPUT));
    if (uSent != ARRAYSIZE(inputs))
    {
        DEBUG_PRINT("SendInput failed: 0x%x\r\n", HRESULT_FROM_WIN32(GetLastError()));
    } 
#elif defined(TEST_SENDMOUSE)
    DEBUG_PRINT("TEST_SENDMOUSE ");
    INPUT inputs[1] = {};// 初回動作確認済
    ZeroMemory(inputs, sizeof(inputs));

    inputs[0].type  = INPUT_MOUSE;//INPUT_KEYBOARD;
    inputs[0].mi.dx = pos.x;
    inputs[0].mi.dy = pos.y;
    inputs[0].mi.dwExtraInfo = SEND_PROGRAM;
    
    if( msg == WM_LBUTTONDOWN ){
        inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    }else if( msg == WM_LBUTTONUP ){
        inputs[0].mi.dwFlags = MOUSEEVENTF_LEFTUP;
    }

    UINT uSent = SendInput(ARRAYSIZE(inputs), inputs, sizeof(INPUT));
    if (uSent != ARRAYSIZE(inputs))
    {
        DEBUG_PRINT("SendInput failed: 0x%x\r\n", HRESULT_FROM_WIN32(GetLastError()));
    } 
#elif defined(TEST_SENDHARDWARE)
    DEBUG_PRINT("TEST_SENDHARDWARE ");
    INPUT inputs[1] = {};// テスト未実施
    ZeroMemory(inputs, sizeof(inputs));

    //inputs[0].type = INPUT_MOUSE;//INPUT_KEYBOARD;
    inputs[0].type = INPUT_HARDWARE;
    inputs[0].hi.wVk = VK_LBUTTON;
    
    if( msg == WM_LBUTTONDOWN ){
        //inputs[0].ki.dwFlags = MOUSEEVENTF_LEFTDOWN;
        inputs[0].ki.dwFlags = 0;
    }else if( msg == WM_LBUTTONUP ){
        //inputs[0].ki.dwFlags = MOUSEEVENTF_LEFTUP;
        inputs[0].ki.dwFlags = KEYEVENTF_KEYUP;
    }

    UINT uSent = SendInput(ARRAYSIZE(inputs), inputs, sizeof(INPUT));
    if (uSent != ARRAYSIZE(inputs))
    {
        DEBUG_PRINT("SendInput failed: 0x%x\r\n", HRESULT_FROM_WIN32(GetLastError()));
    } 
#endif
}

void click_control(HWND hwnd){
//    send_leftbutton_event(WM_LBUTTONDOWN);
//    Sleep(press_time);
//    send_leftbutton_event(WM_LBUTTONUP);    
}

int down_control(HWND hwnd){
    if( auto_state&KEY_DOWN ){
        send_leftbutton_event(WM_LBUTTONDOWN);
        {
            SYSTEMTIME systime;
            GetSystemTime(&systime);
            DEBUG_PRINT("systime %02d:%02d.%03d ",
                systime.wMinute,
                systime.wSecond,
                systime.wMilliseconds);
        }
        {
            POINT pos;
            GetCursorPos(&pos);
            DEBUG_PRINT("down x = %d y = %d",pos.x,pos.y);
        }
        return 1;
    }else{
        KillTimer(hwnd,DOWN_CONTROL);
        return 0;
    }
}

int up_control(HWND hwnd){
    if( auto_state&KEY_DOWN ){
        send_leftbutton_event(WM_LBUTTONUP);
        {
            SYSTEMTIME systime;
            GetSystemTime(&systime);
            DEBUG_PRINT("systime %02d:%02d.%03d ",
                systime.wMinute,
                systime.wSecond,
                systime.wMilliseconds);
        }
        {
            POINT pos;
            GetCursorPos(&pos);
            DEBUG_PRINT("up   x = %d y = %d\r\n",pos.x,pos.y);
        }
        return 1;
    }else{
        KillTimer(hwnd,UP_CONTROL);
        return 0;
    }
}

//void raw_control(HWND hwnd,RAWINPUT* input){
//    if ( input->header.dwType == RIM_TYPEMOUSE ) {
//        int i;
//        int btn_flg = input->data.mouse.usButtonFlags;
//        for( i=-1;++i<KEY_RAW; ){
//            raw_state[i] = SWITCH_RAWKEY(raw_state[i],btn_flg,CHECK_FLG_SHIFT[i]);
//        }
//    }
//}

void raw_control(HWND hwnd,RAWINPUT* input){
    if ( input->header.dwType == RIM_TYPEMOUSE ) {
        int i;
        int btn_flg = input->data.mouse.usButtonFlags;
        for( i=-1;++i<KEY_RAW; ){
            raw_state[i] = SWITCH_RAWKEY(raw_state[i],btn_flg,CHECK_FLG_SHIFT[i]);
        }
        int old_state[] = {
            button_state[VK_LBUTTON],
            button_state[VK_RBUTTON],
            auto_state,
        };
        
        // set raw keys state
        {
            int i = -1;
            for( ;++i<KEY_RAW; ){
                // button_stateの第一フラグは常に0に設定し
                // raw_stateの第一フラグを設定する
                button_state[RAW_MAP[i]] = button_state[RAW_MAP[i]]<<1&2|raw_state[i];
            }
        }
        
        // auto click state update
        {
            int key_auto = 0;
            
            if( start_type == HOLD_CLICK ){
                key_auto = button_state[VK_LBUTTON]
                          &button_state[VK_RBUTTON]&1;
            }else if( start_type == SWITCH_CLICK ){
                if( button_state[VK_LBUTTON]
                  + button_state[VK_RBUTTON]
                  == KEY_HOLD + KEY_DOWN ){
                    key_auto = ~auto_state&1;
                }else{
                    key_auto = auto_state&1;
                }
            }
            
            auto_state = UPDATE_STATE(auto_state,key_auto);
        }
        
        if( old_state[0] != button_state[VK_LBUTTON] ||
                old_state[1] != button_state[VK_RBUTTON] ||
                old_state[2] != auto_state ){
            DEBUG_PRINT(
                "L %d , R %d , A %d\r\n",
                button_state[VK_LBUTTON],
                button_state[VK_RBUTTON],
                auto_state);
        }
        
        // 指定されている間隔でクリック
        if( auto_state == KEY_DOWN ){
            SetTimer( hwnd,DOWN_CONTROL,retry_time+press_time,NULL);
            SetTimer( hwnd,SET_UP_CONTROL,press_time,NULL);
        }
        
    }
}

void hidewindow(HWND hwnd){
    ShowWindow(hwnd, SW_HIDE);
    SetWindowLong(hwnd, GWL_EXSTYLE, GetWindowLong(hwnd, GWL_EXSTYLE) | WS_EX_TOOLWINDOW);
}

void printWM(int msg){
    static int prevmsg = -1;
    if( prevmsg == msg ){
        return;
    }
    prevmsg = msg;
    switch(msg){
        case WM_NULL:
            DEBUG_PRINT("WM_NULL\r\n");
            break;
        case WM_CREATE:
            DEBUG_PRINT("WM_CREATE\r\n");
            break;
        case WM_DESTROY:
            DEBUG_PRINT("WM_DESTROY\r\n");
            break;
        case WM_MOVE:
            DEBUG_PRINT("WM_MOVE\r\n");
            break;
        case WM_SIZE:
            DEBUG_PRINT("WM_SIZE\r\n");
            break;
        case WM_ACTIVATE:
            DEBUG_PRINT("WM_ACTIVATE\r\n");
            break;
        case WM_SETFOCUS:
            DEBUG_PRINT("WM_SETFOCUS\r\n");
            break;
        case WM_KILLFOCUS:
            DEBUG_PRINT("WM_KILLFOCUS\r\n");
            break;
        case WM_ENABLE:
            DEBUG_PRINT("WM_ENABLE\r\n");
            break;
        case WM_SETREDRAW:
            DEBUG_PRINT("WM_SETREDRAW\r\n");
            break;
        case WM_SETTEXT:
            DEBUG_PRINT("WM_SETTEXT\r\n");
            break;
        case WM_GETTEXT:
            DEBUG_PRINT("WM_GETTEXT\r\n");
            break;
        case WM_GETTEXTLENGTH:
            DEBUG_PRINT("WM_GETTEXTLENGTH\r\n");
            break;
        case WM_PAINT:
            DEBUG_PRINT("WM_PAINT\r\n");
            break;
        case WM_CLOSE:
            DEBUG_PRINT("WM_CLOSE\r\n");
            break;
        case WM_QUERYENDSESSION:
            DEBUG_PRINT("WM_QUERYENDSESSION\r\n");
            break;
        case WM_QUIT:
            DEBUG_PRINT("WM_QUIT\r\n");
            break;
        case WM_QUERYOPEN:
            DEBUG_PRINT("WM_QUERYOPEN\r\n");
            break;
        case WM_ERASEBKGND:
            DEBUG_PRINT("WM_ERASEBKGND\r\n");
            break;
        case WM_SYSCOLORCHANGE:
            DEBUG_PRINT("WM_SYSCOLORCHANGE\r\n");
            break;
        case WM_ENDSESSION:
            DEBUG_PRINT("WM_ENDSESSION\r\n");
            break;
        case WM_SHOWWINDOW:
            DEBUG_PRINT("WM_SHOWWINDOW\r\n");
            break;
        case WM_WININICHANGE:
            DEBUG_PRINT("WM_WININICHANGE\r\n");
            break;
        case WM_DEVMODECHANGE:
            DEBUG_PRINT("WM_DEVMODECHANGE\r\n");
            break;
        case WM_ACTIVATEAPP:
            DEBUG_PRINT("WM_ACTIVATEAPP\r\n");
            break;
        case WM_FONTCHANGE:
            DEBUG_PRINT("WM_FONTCHANGE\r\n");
            break;
        case WM_TIMECHANGE:
            DEBUG_PRINT("WM_TIMECHANGE\r\n");
            break;
        case WM_CANCELMODE:
            DEBUG_PRINT("WM_CANCELMODE\r\n");
            break;
        case WM_SETCURSOR:
//            DEBUG_PRINT("WM_SETCURSOR\r\n");
            break;
        case WM_MOUSEACTIVATE:
            DEBUG_PRINT("WM_MOUSEACTIVATE\r\n");
            break;
        case WM_CHILDACTIVATE:
            DEBUG_PRINT("WM_CHILDACTIVATE\r\n");
            break;
        case WM_QUEUESYNC:
            DEBUG_PRINT("WM_QUEUESYNC\r\n");
            break;
        case WM_GETMINMAXINFO:
            DEBUG_PRINT("WM_GETMINMAXINFO\r\n");
            break;
        case WM_PAINTICON:
            DEBUG_PRINT("WM_PAINTICON\r\n");
            break;
        case WM_ICONERASEBKGND:
            DEBUG_PRINT("WM_ICONERASEBKGND\r\n");
            break;
        case WM_NEXTDLGCTL:
            DEBUG_PRINT("WM_NEXTDLGCTL\r\n");
            break;
        case WM_SPOOLERSTATUS:
            DEBUG_PRINT("WM_SPOOLERSTATUS\r\n");
            break;
        case WM_DRAWITEM:
            DEBUG_PRINT("WM_DRAWITEM\r\n");
            break;
        case WM_MEASUREITEM:
            DEBUG_PRINT("WM_MEASUREITEM\r\n");
            break;
        case WM_DELETEITEM:
            DEBUG_PRINT("WM_DELETEITEM\r\n");
            break;
        case WM_VKEYTOITEM:
            DEBUG_PRINT("WM_VKEYTOITEM\r\n");
            break;
        case WM_CHARTOITEM:
            DEBUG_PRINT("WM_CHARTOITEM\r\n");
            break;
        case WM_SETFONT:
            DEBUG_PRINT("WM_SETFONT\r\n");
            break;
        case WM_GETFONT:
            DEBUG_PRINT("WM_GETFONT\r\n");
            break;
        case WM_SETHOTKEY:
            DEBUG_PRINT("WM_SETHOTKEY\r\n");
            break;
        case WM_GETHOTKEY:
            DEBUG_PRINT("WM_GETHOTKEY\r\n");
            break;
        case WM_QUERYDRAGICON:
            DEBUG_PRINT("WM_QUERYDRAGICON\r\n");
            break;
        case WM_COMPAREITEM:
            DEBUG_PRINT("WM_COMPAREITEM\r\n");
            break;
        case WM_GETOBJECT:
            DEBUG_PRINT("WM_GETOBJECT\r\n");
            break;
        case WM_COMPACTING:
            DEBUG_PRINT("WM_COMPACTING\r\n");
            break;
        case WM_COMMNOTIFY:
            DEBUG_PRINT("WM_COMMNOTIFY\r\n");
            break;
        case WM_WINDOWPOSCHANGING:
            DEBUG_PRINT("WM_WINDOWPOSCHANGING\r\n");
            break;
        case WM_WINDOWPOSCHANGED:
            DEBUG_PRINT("WM_WINDOWPOSCHANGED\r\n");
            break;
        case WM_POWER:
            DEBUG_PRINT("WM_POWER\r\n");
            break;
        case WM_COPYDATA:
            DEBUG_PRINT("WM_COPYDATA\r\n");
            break;
        case WM_CANCELJOURNAL:
            DEBUG_PRINT("WM_CANCELJOURNAL\r\n");
            break;
        case WM_NOTIFY:
            DEBUG_PRINT("WM_NOTIFY\r\n");
            break;
        case WM_INPUTLANGCHANGEREQUEST:
            DEBUG_PRINT("WM_INPUTLANGCHANGEREQUEST\r\n");
            break;
        case WM_INPUTLANGCHANGE:
            DEBUG_PRINT("WM_INPUTLANGCHANGE\r\n");
            break;
        case WM_TCARD:
            DEBUG_PRINT("WM_TCARD\r\n");
            break;
        case WM_HELP:
            DEBUG_PRINT("WM_HELP\r\n");
            break;
        case WM_USERCHANGED:
            DEBUG_PRINT("WM_USERCHANGED\r\n");
            break;
        case WM_NOTIFYFORMAT:
            DEBUG_PRINT("WM_NOTIFYFORMAT\r\n");
            break;
        case WM_CONTEXTMENU:
            DEBUG_PRINT("WM_CONTEXTMENU\r\n");
            break;
        case WM_STYLECHANGING:
            DEBUG_PRINT("WM_STYLECHANGING\r\n");
            break;
        case WM_STYLECHANGED:
            DEBUG_PRINT("WM_STYLECHANGED\r\n");
            break;
        case WM_DISPLAYCHANGE:
            DEBUG_PRINT("WM_DISPLAYCHANGE\r\n");
            break;
        case WM_GETICON:
            DEBUG_PRINT("WM_GETICON\r\n");
            break;
        case WM_SETICON:
            DEBUG_PRINT("WM_SETICON\r\n");
            break;
        case WM_NCCREATE:
            DEBUG_PRINT("WM_NCCREATE\r\n");
            break;
        case WM_NCDESTROY:
            DEBUG_PRINT("WM_NCDESTROY\r\n");
            break;
        case WM_NCCALCSIZE:
            DEBUG_PRINT("WM_NCCALCSIZE\r\n");
            break;
        case WM_NCHITTEST:
//            DEBUG_PRINT("WM_NCHITTEST\r\n");
            break;
        case WM_NCPAINT:
            DEBUG_PRINT("WM_NCPAINT\r\n");
            break;
        case WM_NCACTIVATE:
            DEBUG_PRINT("WM_NCACTIVATE\r\n");
            break;
        case WM_GETDLGCODE:
            DEBUG_PRINT("WM_GETDLGCODE\r\n");
            break;
        case WM_SYNCPAINT:
            DEBUG_PRINT("WM_SYNCPAINT\r\n");
            break;
        case WM_NCMOUSEMOVE:
//            DEBUG_PRINT("WM_NCMOUSEMOVE\r\n");
            break;
        case WM_NCLBUTTONDOWN:
            DEBUG_PRINT("WM_NCLBUTTONDOWN\r\n");
            break;
        case WM_NCLBUTTONUP:
            DEBUG_PRINT("WM_NCLBUTTONUP\r\n");
            break;
        case WM_NCLBUTTONDBLCLK:
            DEBUG_PRINT("WM_NCLBUTTONDBLCLK\r\n");
            break;
        case WM_NCRBUTTONDOWN:
            DEBUG_PRINT("WM_NCRBUTTONDOWN\r\n");
            break;
        case WM_NCRBUTTONUP:
            DEBUG_PRINT("WM_NCRBUTTONUP\r\n");
            break;
        case WM_NCRBUTTONDBLCLK:
            DEBUG_PRINT("WM_NCRBUTTONDBLCLK\r\n");
            break;
        case WM_NCMBUTTONDOWN:
            DEBUG_PRINT("WM_NCMBUTTONDOWN\r\n");
            break;
        case WM_NCMBUTTONUP:
            DEBUG_PRINT("WM_NCMBUTTONUP\r\n");
            break;
        case WM_NCMBUTTONDBLCLK:
            DEBUG_PRINT("WM_NCMBUTTONDBLCLK\r\n");
            break;
        case WM_NCXBUTTONDOWN:
            DEBUG_PRINT("WM_NCXBUTTONDOWN\r\n");
            break;
        case WM_NCXBUTTONUP:
            DEBUG_PRINT("WM_NCXBUTTONUP\r\n");
            break;
        case WM_NCXBUTTONDBLCLK:
            DEBUG_PRINT("WM_NCXBUTTONDBLCLK\r\n");
            break;
        case WM_INPUT:
            DEBUG_PRINT("WM_INPUT\r\n");
            break;
        case WM_KEYFIRST:
            DEBUG_PRINT("WM_KEYFIRST\r\n");
            break;
        case WM_KEYUP:
            DEBUG_PRINT("WM_KEYUP\r\n");
            break;
        case WM_CHAR:
            DEBUG_PRINT("WM_CHAR\r\n");
            break;
        case WM_DEADCHAR:
            DEBUG_PRINT("WM_DEADCHAR\r\n");
            break;
        case WM_SYSKEYDOWN:
            DEBUG_PRINT("WM_SYSKEYDOWN\r\n");
            break;
        case WM_SYSKEYUP:
            DEBUG_PRINT("WM_SYSKEYUP\r\n");
            break;
        case WM_SYSCHAR:
            DEBUG_PRINT("WM_SYSCHAR\r\n");
            break;
        case WM_SYSDEADCHAR:
            DEBUG_PRINT("WM_SYSDEADCHAR\r\n");
            break;
        case WM_KEYLAST:
            DEBUG_PRINT("WM_KEYLAST\r\n");
            break;
        case WM_INITDIALOG:
            DEBUG_PRINT("WM_INITDIALOG\r\n");
            break;
        case WM_COMMAND:
            DEBUG_PRINT("WM_COMMAND\r\n");
            break;
        case WM_SYSCOMMAND:
            DEBUG_PRINT("WM_SYSCOMMAND\r\n");
            break;
        case WM_TIMER:
            DEBUG_PRINT("WM_TIMER\r\n");
            break;
        case WM_HSCROLL:
            DEBUG_PRINT("WM_HSCROLL\r\n");
            break;
        case WM_VSCROLL:
            DEBUG_PRINT("WM_VSCROLL\r\n");
            break;
        case WM_INITMENU:
            DEBUG_PRINT("WM_INITMENU\r\n");
            break;
        case WM_INITMENUPOPUP:
            DEBUG_PRINT("WM_INITMENUPOPUP\r\n");
            break;
        case WM_MENUSELECT:
            DEBUG_PRINT("WM_MENUSELECT\r\n");
            break;
        case WM_MENUCHAR:
            DEBUG_PRINT("WM_MENUCHAR\r\n");
            break;
        case WM_ENTERIDLE:
            DEBUG_PRINT("WM_ENTERIDLE\r\n");
            break;
        case WM_MENURBUTTONUP:
            DEBUG_PRINT("WM_MENURBUTTONUP\r\n");
            break;
        case WM_MENUDRAG:
            DEBUG_PRINT("WM_MENUDRAG\r\n");
            break;
        case WM_MENUGETOBJECT:
            DEBUG_PRINT("WM_MENUGETOBJECT\r\n");
            break;
        case WM_UNINITMENUPOPUP:
            DEBUG_PRINT("WM_UNINITMENUPOPUP\r\n");
            break;
        case WM_MENUCOMMAND:
            DEBUG_PRINT("WM_MENUCOMMAND\r\n");
            break;
        case WM_CHANGEUISTATE:
            DEBUG_PRINT("WM_CHANGEUISTATE\r\n");
            break;
        case WM_UPDATEUISTATE:
            DEBUG_PRINT("WM_UPDATEUISTATE\r\n");
            break;
        case WM_QUERYUISTATE:
            DEBUG_PRINT("WM_QUERYUISTATE\r\n");
            break;
        case WM_CTLCOLORMSGBOX:
            DEBUG_PRINT("WM_CTLCOLORMSGBOX\r\n");
            break;
        case WM_CTLCOLOREDIT:
            DEBUG_PRINT("WM_CTLCOLOREDIT\r\n");
            break;
        case WM_CTLCOLORLISTBOX:
            DEBUG_PRINT("WM_CTLCOLORLISTBOX\r\n");
            break;
        case WM_CTLCOLORBTN:
            DEBUG_PRINT("WM_CTLCOLORBTN\r\n");
            break;
        case WM_CTLCOLORDLG:
            DEBUG_PRINT("WM_CTLCOLORDLG\r\n");
            break;
        case WM_CTLCOLORSCROLLBAR:
            DEBUG_PRINT("WM_CTLCOLORSCROLLBAR\r\n");
            break;
        case WM_CTLCOLORSTATIC:
            DEBUG_PRINT("WM_CTLCOLORSTATIC\r\n");
            break;
        case WM_MOUSEFIRST:
//            DEBUG_PRINT("WM_MOUSEFIRST\r\n");
            break;
        case WM_LBUTTONDOWN:
            DEBUG_PRINT("WM_LBUTTONDOWN\r\n");
            break;
        case WM_LBUTTONUP:
            DEBUG_PRINT("WM_LBUTTONUP\r\n");
            break;
        case WM_LBUTTONDBLCLK:
            DEBUG_PRINT("WM_LBUTTONDBLCLK\r\n");
            break;
        case WM_RBUTTONDOWN:
            DEBUG_PRINT("WM_RBUTTONDOWN\r\n");
            break;
        case WM_RBUTTONUP:
            DEBUG_PRINT("WM_RBUTTONUP\r\n");
            break;
        case WM_RBUTTONDBLCLK:
            DEBUG_PRINT("WM_RBUTTONDBLCLK\r\n");
            break;
        case WM_MBUTTONDOWN:
            DEBUG_PRINT("WM_MBUTTONDOWN\r\n");
            break;
        case WM_MBUTTONUP:
            DEBUG_PRINT("WM_MBUTTONUP\r\n");
            break;
        case WM_MBUTTONDBLCLK:
            DEBUG_PRINT("WM_MBUTTONDBLCLK\r\n");
            break;
        case WM_MOUSEWHEEL:
            DEBUG_PRINT("WM_MOUSEWHEEL\r\n");
            break;
        case WM_XBUTTONDOWN:
            DEBUG_PRINT("WM_XBUTTONDOWN\r\n");
            break;
        case WM_XBUTTONUP:
            DEBUG_PRINT("WM_XBUTTONUP\r\n");
            break;
        case WM_MOUSELAST:
            DEBUG_PRINT("WM_MOUSELAST\r\n");
            break;
        case WM_PARENTNOTIFY:
            DEBUG_PRINT("WM_PARENTNOTIFY\r\n");
            break;
        case WM_ENTERMENULOOP:
            DEBUG_PRINT("WM_ENTERMENULOOP\r\n");
            break;
        case WM_EXITMENULOOP:
            DEBUG_PRINT("WM_EXITMENULOOP\r\n");
            break;
        case WM_NEXTMENU:
            DEBUG_PRINT("WM_NEXTMENU\r\n");
            break;
        case WM_SIZING:
            DEBUG_PRINT("WM_SIZING\r\n");
            break;
        case WM_CAPTURECHANGED:
            DEBUG_PRINT("WM_CAPTURECHANGED\r\n");
            break;
        case WM_MOVING:
            DEBUG_PRINT("WM_MOVING\r\n");
            break;
        case WM_POWERBROADCAST:
            DEBUG_PRINT("WM_POWERBROADCAST\r\n");
            break;
        case WM_DEVICECHANGE:
            DEBUG_PRINT("WM_DEVICECHANGE\r\n");
            break;
        case WM_MDICREATE:
            DEBUG_PRINT("WM_MDICREATE\r\n");
            break;
        case WM_MDIDESTROY:
            DEBUG_PRINT("WM_MDIDESTROY\r\n");
            break;
        case WM_MDIACTIVATE:
            DEBUG_PRINT("WM_MDIACTIVATE\r\n");
            break;
        case WM_MDIRESTORE:
            DEBUG_PRINT("WM_MDIRESTORE\r\n");
            break;
        case WM_MDINEXT:
            DEBUG_PRINT("WM_MDINEXT\r\n");
            break;
        case WM_MDIMAXIMIZE:
            DEBUG_PRINT("WM_MDIMAXIMIZE\r\n");
            break;
        case WM_MDITILE:
            DEBUG_PRINT("WM_MDITILE\r\n");
            break;
        case WM_MDICASCADE:
            DEBUG_PRINT("WM_MDICASCADE\r\n");
            break;
        case WM_MDIICONARRANGE:
            DEBUG_PRINT("WM_MDIICONARRANGE\r\n");
            break;
        case WM_MDIGETACTIVE:
            DEBUG_PRINT("WM_MDIGETACTIVE\r\n");
            break;
        case WM_MDISETMENU:
            DEBUG_PRINT("WM_MDISETMENU\r\n");
            break;
        case WM_ENTERSIZEMOVE:
            DEBUG_PRINT("WM_ENTERSIZEMOVE\r\n");
            break;
        case WM_EXITSIZEMOVE:
            DEBUG_PRINT("WM_EXITSIZEMOVE\r\n");
            break;
        case WM_DROPFILES:
            DEBUG_PRINT("WM_DROPFILES\r\n");
            break;
        case WM_MDIREFRESHMENU:
            DEBUG_PRINT("WM_MDIREFRESHMENU\r\n");
            break;
        case WM_NCMOUSEHOVER:
            DEBUG_PRINT("WM_NCMOUSEHOVER\r\n");
            break;
        case WM_MOUSEHOVER:
            DEBUG_PRINT("WM_MOUSEHOVER\r\n");
            break;
        case WM_NCMOUSELEAVE:
            DEBUG_PRINT("WM_NCMOUSELEAVE\r\n");
            break;
        case WM_MOUSELEAVE:
            DEBUG_PRINT("WM_MOUSELEAVE\r\n");
            break;
        case WM_CUT:
            DEBUG_PRINT("WM_CUT\r\n");
            break;
        case WM_COPY:
            DEBUG_PRINT("WM_COPY\r\n");
            break;
        case WM_PASTE:
            DEBUG_PRINT("WM_PASTE\r\n");
            break;
        case WM_CLEAR:
            DEBUG_PRINT("WM_CLEAR\r\n");
            break;
        case WM_UNDO:
            DEBUG_PRINT("WM_UNDO\r\n");
            break;
        case WM_RENDERFORMAT:
            DEBUG_PRINT("WM_RENDERFORMAT\r\n");
            break;
        case WM_RENDERALLFORMATS:
            DEBUG_PRINT("WM_RENDERALLFORMATS\r\n");
            break;
        case WM_DESTROYCLIPBOARD:
            DEBUG_PRINT("WM_DESTROYCLIPBOARD\r\n");
            break;
        case WM_DRAWCLIPBOARD:
            DEBUG_PRINT("WM_DRAWCLIPBOARD\r\n");
            break;
        case WM_PAINTCLIPBOARD:
            DEBUG_PRINT("WM_PAINTCLIPBOARD\r\n");
            break;
        case WM_VSCROLLCLIPBOARD:
            DEBUG_PRINT("WM_VSCROLLCLIPBOARD\r\n");
            break;
        case WM_SIZECLIPBOARD:
            DEBUG_PRINT("WM_SIZECLIPBOARD\r\n");
            break;
        case WM_ASKCBFORMATNAME:
            DEBUG_PRINT("WM_ASKCBFORMATNAME\r\n");
            break;
        case WM_CHANGECBCHAIN:
            DEBUG_PRINT("WM_CHANGECBCHAIN\r\n");
            break;
        case WM_HSCROLLCLIPBOARD:
            DEBUG_PRINT("WM_HSCROLLCLIPBOARD\r\n");
            break;
        case WM_QUERYNEWPALETTE:
            DEBUG_PRINT("WM_QUERYNEWPALETTE\r\n");
            break;
        case WM_PALETTEISCHANGING:
            DEBUG_PRINT("WM_PALETTEISCHANGING\r\n");
            break;
        case WM_PALETTECHANGED:
            DEBUG_PRINT("WM_PALETTECHANGED\r\n");
            break;
        case WM_HOTKEY:
            DEBUG_PRINT("WM_HOTKEY\r\n");
            break;
        case WM_PRINT:
            DEBUG_PRINT("WM_PRINT\r\n");
            break;
        case WM_PRINTCLIENT:
            DEBUG_PRINT("WM_PRINTCLIENT\r\n");
            break;
        case WM_APPCOMMAND:
            DEBUG_PRINT("WM_APPCOMMAND\r\n");
            break;
        case WM_THEMECHANGED:
            DEBUG_PRINT("WM_THEMECHANGED\r\n");
            break;
        case WM_HANDHELDFIRST:
            DEBUG_PRINT("WM_HANDHELDFIRST\r\n");
            break;
        case WM_HANDHELDLAST:
            DEBUG_PRINT("WM_HANDHELDLAST\r\n");
            break;
        case WM_AFXFIRST:
            DEBUG_PRINT("WM_AFXFIRST\r\n");
            break;
        case WM_AFXLAST:
            DEBUG_PRINT("WM_AFXLAST\r\n");
            break;
        case WM_PENWINFIRST:
            DEBUG_PRINT("WM_PENWINFIRST\r\n");
            break;
        case WM_PENWINLAST:
            DEBUG_PRINT("WM_PENWINLAST\r\n");
            break;
        case WM_USER:
            DEBUG_PRINT("WM_USER\r\n");
            break;
        case (WM_USER+1):
            DEBUG_PRINT("WM_USER+1 DM_SETDEFID\r\n");
            break;
        case (WM_USER+2):
            DEBUG_PRINT("WM_USER+2 DM_REPOSITION\r\n");
            break;
        case (WM_USER+100):
            DEBUG_PRINT("WM_USER+100 PSM_PAGEINFO\r\n");
            break;
        case (WM_USER+101):
            DEBUG_PRINT("WM_USER+101 PSM_SHEETINFO\r\n");
            break;
        case WM_APP:
            DEBUG_PRINT("WM_APP\r\n");
            break;
        default:
            DEBUG_PRINT("%d\r\n",msg);
    }
}
