//================================================
/*

Zoom
Zoom in or out on web content using the zoom button for more comfortable reading.
Copyright (C) 2020 Stefan vd
www.stefanvd.net

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


To view a copy of this license, visit http://creativecommons.org/licenses/GPL/2.0/

*/
//================================================

var currentURL;var allzoom;var allzoomvalue;var badge;var lightcolor;var zoomchrome;var zoomweb;var backgroundnumber;var zoombydomain;var zoombypage;var defaultallscreen;var defaultsinglescreen;var websitezoom;var zoomfont;var goturlinside = false;var currentscreen;var chromedisplay;var screenzoom;var zoomsingleclick;var zoomnewsingleclick;var zoomdoubleclick;var contexta;var contextb;
chrome.runtime.onMessage.addListener(function request(request,sender,sendResponse){
if(request.action == 'getallRatio'){
currentURL = request.website;
chromedisplay = request.screen;
chrome.storage.sync.get(['allzoom','allzoomvalue','websitezoom','badge','lightcolor','zoomchrome','zoomweb','zoombydomain','zoombypage','defaultallscreen','defaultsinglescreen','screenzoom','zoomfont',], function(response){
allzoom = response.allzoom;if(allzoom == null)allzoom = false; // default allzoom false
allzoomvalue = response.allzoomvalue;if(allzoomvalue == null)allzoomvalue = 1; // default allzoomvalue value
badge = response.badge;if(badge == null)badge = false;
lightcolor = response.lightcolor;if(lightcolor == null)lightcolor = '#3cb4fe';
zoomchrome = response.zoomchrome;if(zoomchrome == null)zoomchrome = false;
zoomweb = response.zoomweb;if(zoomweb == null)zoomweb = true;
zoomfont = response.zoomfont;if(zoomfont == null)zoomfont = false;
zoombydomain = response.zoombydomain;if(zoombydomain == null)zoombydomain = true;
zoombypage = response.zoombypage;if(zoombypage == null)zoombypage = false;
if(zoombydomain == true){currentURL = currentURL.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/)[0];}
else{currentURL = currentURL;}
defaultallscreen = response.defaultallscreen;if(defaultallscreen == null)defaultallscreen = true;
defaultsinglescreen = response.defaultsinglescreen;if(defaultsinglescreen == null)defaultsinglescreen = false;
websitezoom = response['websitezoom'];
// if empty use this
if(typeof websitezoom == "undefined" || websitezoom == null){
    websitezoom = JSON.stringify({'https://www.example.com': ["90"], 'https://www.nytimes.com': ["85"]});
}
websitezoom = JSON.parse(websitezoom);

//---
if(defaultallscreen == true){} // no change
else if(defaultsinglescreen == true){

    var screenzoom = response['screenzoom'];
    screenzoom = JSON.parse(screenzoom);
    var satbbuf = [];
    var domain;
    for(domain in screenzoom)
        satbbuf.push(domain);
        satbbuf.sort();
        var i;
        var l = satbbuf.length;
        for(i = 0; i < l; i++){
        if(satbbuf[i] == chromedisplay){
            allzoomvalue = screenzoom[satbbuf[i]]/100;
        }
        }

}

//---
if(allzoom == true){
        chrome.tabs.query({active: true, currentWindow: true},
        function(tabs){
            // NOTE
            // do not open the Chrome dev background script, else it detect this as first active tab and window
            if(tabs[0]){
            chrome.tabs.getZoom(tabs[0].id, function(zoomFactor){
                if(zoomFactor != allzoomvalue){
                    if(zoomchrome == true){
                        chrome.tabs.setZoom(tabs[0].id, allzoomvalue); // needed for the default zoom value such as 110%
                    }else if(zoomweb == true){
                        // Check for transform support so that we can fallback otherwise
                        chrome.tabs.query({},function(opentabs){
                            opentabs.forEach(function(opentab){
                                // inject only if different than 1
                                if(allzoomvalue != 1){
                                    chrome.tabs.sendMessage(opentab.id,{text:'setbodycsszoom',value:allzoomvalue});
                                }
                            });
                        });
                    }else if(zoomfont == true){
                        chrome.tabs.sendMessage(tabs[0].id,{text:'setfontsize'});
                        chrome.tabs.sendMessage(tabs[0].id,{text:'changefontsize', value: Math.round(allzoomvalue*100)});
                    }
                    if(badge == true){
                        chrome.browserAction.setBadgeBackgroundColor({color:lightcolor});
                        chrome.browserAction.setBadgeText({text:""+Math.round(allzoomvalue*100)+""});
                    }else{
                        chrome.browserAction.setBadgeText({text:""});
                    }
                }else{
                    // Needed if the zoom value is the same, update the badge value
                    chrome.browserAction.setBadgeBackgroundColor({color:lightcolor});
                    chrome.browserAction.setBadgeText({text:""+Math.round(allzoomvalue*100)+""});
                }
            });
        }
        });
}
else{
    var atbbuf = [];
    var domain;
    for(domain in websitezoom){atbbuf.push(domain);atbbuf.sort();}
    var i;
    var l = atbbuf.length;
    for(i = 0; i < l; i++){
      if(atbbuf[i] == currentURL){
        var tempatbbuf = atbbuf[i];
        var editzoom = websitezoom[atbbuf[i]]/100;
              chrome.tabs.query({},
              function(tabs){
                  tabs.forEach(function(tab){
                        var tor = tab.url;
                        if(typeof tor !== "undefined"){
                        var filtermatch = tor.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/);
                        if(zoombydomain == true){if(filtermatch){webtor = filtermatch[0];}}
                        else{var webtor = tor;}
                        if(webtor == tempatbbuf){
                            if(zoomchrome == true){
                                chrome.tabs.getZoom(sender.tab.id, function(zoomFactor){
                                if(zoomFactor != editzoom){
                                    // this to keep to zoom level by tab and not the whole domain (= automatic)
                                    if(zoombypage == true){
                                        chrome.tabs.setZoomSettings(sender.tab.id,{mode: 'automatic', scope: 'per-tab'},
                                        function(){
                                          if(chrome.runtime.lastError){
                                          //console.log('[ZoomDemoExtension] doSetMode() error: ' + chrome.runtime.lastError.message);
                                          }
                                        });
                                    }else{
                                        chrome.tabs.setZoomSettings(sender.tab.id,{mode: 'automatic'/*, scope: 'per-tab'*/},
                                        function(){
                                          if(chrome.runtime.lastError){
                                          //console.log('[ZoomDemoExtension] doSetMode() error: ' + chrome.runtime.lastError.message);
                                          }
                                        });
                                    }
                                    chrome.tabs.setZoom(sender.tab.id, editzoom); // needed for the default zoom value such as 110%
                                }
                                });
                            }else if(zoomweb == true){
                                // inject only if different than 1
                                if(editzoom != 1){
                                    chrome.tabs.sendMessage(tab.id,{text:'setbodycsszoom',value:editzoom});
                                }
                            }else if(zoomfont == true){
                                chrome.tabs.sendMessage(tab.id,{text:'setfontsize'});
                                chrome.tabs.sendMessage(tab.id,{text:'changefontsize', value: Math.round(editzoom*100)});
                            }
                            if(badge == true){
                                chrome.browserAction.setBadgeBackgroundColor({color:lightcolor});
                                chrome.browserAction.setBadgeText({text:"" + Math.round(editzoom * 100) + "", tabId: tab.id });
                            }else{
                                chrome.browserAction.setBadgeText({text:""});
                            }
                        }
                        }
                  });
              });
        goturlinside = true;
      }
    }

// URL is not in the table, so use the default zoom value (that by screen size)
// reset got inside
  if(goturlinside == true){}
  else{
  // use default zoom from the Options page -- normal is 100%
  chrome.tabs.query({active: true, currentWindow: true},
    function(tabs){
        chrome.tabs.getZoom(sender.tab.id, function(zoomFactor){
            if(zoomFactor != allzoomvalue){
                if(zoomchrome == true){
                    // this to keep to zoom level by tab and not the whole domain (= automatic)
                    if(zoombypage == true){
                        chrome.tabs.setZoomSettings(sender.tab.id,{mode: 'automatic', scope: 'per-tab'},
                        function(){
                          if(chrome.runtime.lastError){
                          //console.log('[ZoomDemoExtension] doSetMode() error: ' + chrome.runtime.lastError.message);
                          }
                        });
                    }else{
                        chrome.tabs.setZoomSettings(sender.tab.id,{mode: 'automatic'/*, scope: 'per-tab'*/},
                        function(){
                          if(chrome.runtime.lastError){
                          //console.log('[ZoomDemoExtension] doSetMode() error: ' + chrome.runtime.lastError.message);
                          }
                        });
                    }
                    chrome.tabs.setZoom(sender.tab.id, allzoomvalue); // needed for the default zoom value such as 110%
                }else if(zoomweb == true){
                    // inject only if different than 1
                    if(allzoomvalue != 1){
                        chrome.tabs.sendMessage(sender.tab.id,{text:'setbodycsszoom',value:allzoomvalue});
                    }
                }else if(zoomfont == true){
                    chrome.tabs.sendMessage(sender.tab.id,{text:'setfontsize'});
                    chrome.tabs.sendMessage(sender.tab.id,{text:'changefontsize', value: Math.round(allzoomvalue*100)});
                }
                if(badge == true){
                    chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                    chrome.browserAction.setBadgeText({text:""+Math.round(allzoomvalue*100)+"", tabId: sender.tab.id});
                }else{
                    chrome.browserAction.setBadgeText({text:""});
                }
            }else{
                if(badge == true){
                    chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                    chrome.browserAction.setBadgeText({text:""+Math.round(allzoomvalue*100)+"", tabId: sender.tab.id});
                }else{
                    chrome.browserAction.setBadgeText({text:""});
                }
            }
        });
    });
  }
  goturlinside = false;
}

});
}
// contextmenu
else if(request.name == "contextmenuon"){checkcontextmenus();}
else if(request.name == "contextmenuoff"){removecontexmenus();}
// from context
else if(request.name == "contentzoomin"){zoomview(+1);}
else if(request.name == "contentzoomout"){zoomview(-1);}
else if(request.name == "getscreenshot"){
    chrome.tabs.captureVisibleTab(null,{"format": "png"}, function(dataURI){
        if(typeof dataURI !== "undefined"){
            chrome.tabs.sendMessage(sender.tab.id,{text: 'showmagnifyglass', value: dataURI});
        }
    });
}
else if(request.name == "getallpermissions"){
    var result = "";
    chrome.permissions.getAll(function(permissions){
       result = permissions.permissions;
       chrome.tabs.sendMessage(sender.tab.id,{text: 'receiveallpermissions', value: result});
    });
}
});

chrome.webNavigation.onCommitted.addListener(webNavigation_committed);

function webNavigation_committed(data){
    if(data.frameId !== 0){
        return;
    }
    chrome.tabs.get(data.tabId, function(tab){
        if (!chrome.runtime.lastError){
            setTabView(tab.id, tab.url);
        }
    });
}

function setTabView(tabId, url){
    if(tabId >= 0){
        chrome.tabs.executeScript(tabId,{file: "js/content.js", runAt: "document_start"},function(){
            if(chrome.runtime.lastError){
                // if current tab do not have the content.js and can not send the message to local chrome:// page.
                // The line will excute, and log 'ERROR:  {message: "Could not establish connection. Receiving end does not exist."}' 
                //console.log('ERROR: ', chrome.runtime.lastError);
            }
            //viewController.setactionzoom(tabId, viewSettings);

        });
    }
}

// Begin zoom engine ---
var currentRatio = 1; var ratio = 1; var job = null;
var allzoom; var allzoomvalue; var webjob; var websitezoom = {}; var badge; var steps; var lightcolor; var zoomchrome; var zoomweb; var zoomfont;

function zoom(ratio){
currentRatio = ratio / 100;
chrome.tabs.query({active: true, currentWindow: true}, function(tabs){zoomtab(tabs[0].id,currentRatio);});
}

function zoomtab(a,b){
    backgroundnumber=Math.round(b*100);

    if(zoomchrome == true){
        if(allzoom == true){
                chrome.tabs.query({},
                function(tabs){
                    tabs.forEach(function(tab){
                        chrome.tabs.setZoom(tab.id, b);
                    });
                });
        }else{
            try{
                chrome.tabs.setZoom(a, b);
            }
            catch(e){}
        }
    }else if(zoomweb == true){
        if(allzoom == true){
                chrome.tabs.query({},
                function(tabs){
                    tabs.forEach(function(tab){
                        try{
                            chrome.tabs.sendMessage(tab.id,{text:'setbodycsszoom',value:b});
                        }
                        catch(e){}
                        if(badge == true){
                            chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                            chrome.browserAction.setBadgeText({text:""+parseInt(b*100)+""});}
                        else{chrome.browserAction.setBadgeText({text:""});}
                    });
                });
        }else{
            chrome.tabs.query({},
                function(tabs){
                    tabs.forEach(function(tab){
                        var pop = tab.url;
                        if(typeof pop !== "undefined"){
                        var filtermatch = pop.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/);
                        if(zoombydomain == true){if(filtermatch){webpop = filtermatch[0];}}
                        else{var webpop = pop;}
                        if(webpop == webjob){
                            try{
                                chrome.tabs.sendMessage(tab.id,{text:'setbodycsszoom',value:b});
                            }
                            catch(e){}
                            if(badge == true){
                                chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                                chrome.browserAction.setBadgeText({text:""+parseInt(b*100)+"", tabId: tab.id } ); }
                            else{chrome.browserAction.setBadgeText({text:""});}
                        }
                        }
                    });
                });
        }
    }else if(zoomfont == true){
        if(allzoom == true){
            chrome.tabs.query({},
            function(tabs){
                tabs.forEach(function(tab){
                        chrome.tabs.sendMessage(tab.id,{text: 'changefontsize', value: Math.round(b*100)});
                    if(badge == true){
                        chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                        chrome.browserAction.setBadgeText({text:""+parseInt(b*100)+""});}
                    else{chrome.browserAction.setBadgeText({text:""});}
                });
            });
    }else{
        chrome.tabs.query({},
            function(tabs){
                tabs.forEach(function(tab){
                    var pop = tab.url;
                    if(typeof pop !== "undefined"){
                    var filtermatch = pop.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/);
                    if(zoombydomain == true){if(filtermatch){webpop = filtermatch[0];}}
                    else{var webpop = pop;}
                    if(webpop == webjob){
                            chrome.tabs.sendMessage(tab.id,{text: 'changefontsize', value: Math.round(b*100)});
                        if(badge == true){
                            chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                            chrome.browserAction.setBadgeText({text:""+parseInt(b*100)+"", tabId: tab.id});}
                        else{chrome.browserAction.setBadgeText({text:""});}
                    }
                    }
                });
            });
        }
    }

    // saving feature
    if(allzoom == true){
        // save for all zoom feature
        chrome.storage.sync.set({"allzoomvalue": b});
    }else{
            var atbbuf = [];
            var domain;
            for(domain in websitezoom){atbbuf.push(domain);atbbuf.sort();}
            var i;
            var l = atbbuf.length;
            for(i = 0; i < l; i++){
                if(atbbuf[i] == webjob){ //update
                    if(b == 1){
                        // remove from list
                        delete websitezoom['' + atbbuf[i] + ''];
                        atbbuf = websitezoom;
                    }else{
                        // update ratio
                        websitezoom['' + atbbuf[i] + ''] = parseInt(b * 100);
                    }
                }else{
                    // add to list
                    websitezoom['' + webjob + ''] = parseInt(b * 100);
                }
            }
            // save for zoom feature
            chrome.storage.sync.set({"websitezoom":JSON.stringify(websitezoom)});
    }
}
function zoomview(direction){zoom(nextratio(currentRatio*100,direction));}

function nextratio(ratio,direction){
ratio = Math.round(ratio);
var prevratio = parseInt(ratio)-parseInt(steps);
var nextratio = parseInt(ratio)+parseInt(steps);
if(direction==-1){
    if(ratio == 10){prevratio = 100;nextratio = 100;}
}else{
    if(ratio == 400){prevratio = 100;nextratio = 100;}
}
return(direction==-1)?prevratio:nextratio;
}
// End zoom engine ---

//Set click to false at beginning
var alreadyClicked = false;
//Declare a timer variable
var timer;

var openactiondoubleclick = function(tabs){
    //Check for previous click
    if(alreadyClicked){
        //console.log("Doubleclick");
        //Yes, Previous Click Detected
        //Clear timer already set in earlier Click
        window.clearTimeout(timer);
        if(zoomdoubleclick == true){
            // zoom in
            zoomview(+1);
        }
        else if(zoomnewsingleclick == true){
            chrome.browserAction.setPopup({tabId: tabs.id, popup:""});
        }

        //Clear all Clicks
        alreadyClicked = false;
        return;
    }

    //Set Click to  true
    alreadyClicked = true;
    if(zoomdoubleclick == true){

    }
    else if(zoomnewsingleclick == true){
        chrome.browserAction.setPopup({tabId: tabs.id, popup:"popup.html"});
    }

    //Add a timer to detect next click to a sample of 250
    timer = window.setTimeout(function(){
        //console.log("Singelclick");
        //No more clicks so, this is a single click
        if(zoomdoubleclick == true){
            // zoom out
            zoomview(-1);
        }
        else if(zoomnewsingleclick == true){
            var popups = chrome.extension.getViews({type:"popup"});
            if(popups.length != 0){// popup exist

            }else{ // not exist
                chrome.tabs.sendMessage(tabs.id,{text:'enablemagnifyingglass'});
            }
        }

        //Clear all timers
        window.clearTimeout(timer);
        //Ignore clicks
        alreadyClicked = false;
        if(zoomnewsingleclick == true){
            chrome.browserAction.setPopup({tabId: tabs.id, popup:""});
        }
    }, 250);
};

function doubleclickaction(){
chrome.browserAction.setPopup({popup:''});
if(chrome.browserAction.onClicked.hasListener(openactiondoubleclick)){chrome.browserAction.onClicked.removeListener(openactiondoubleclick);}
chrome.browserAction.onClicked.addListener(openactiondoubleclick);
}

function regularaction(){
if(chrome.browserAction.onClicked.hasListener(openactiondoubleclick)){chrome.browserAction.onClicked.removeListener(openactiondoubleclick);}
chrome.browserAction.setPopup({popup:"popup.html"});
}

function backgroundrefreshzoom(){
chrome.storage.sync.get(['allzoom','allzoomvalue','websitezoom','badge','steps','lightcolor','zoomchrome','zoomweb','zoombydomain','zoombypage','zoomfont'], function(response){
allzoom = response.allzoom;if(allzoom == null)allzoom = false; // default allzoom false
allzoomvalue = response.allzoomvalue;if(allzoomvalue == null)allzoomvalue = 1; // default allzoomvalue value
badge = response.badge;if(badge == null)badge = false;
lightcolor = response.lightcolor;if(lightcolor == null)lightcolor = "#3cb4fe";
steps = response.steps;if(steps == null)steps = 10;
zoomchrome = response.zoomchrome;if(zoomchrome == null)zoomchrome = false;
zoomweb = response.zoomweb;if(zoomweb == null)zoomweb = true;
zoomfont = response.zoomfont;if(zoomfont == null)zoomfont = false;
websitezoom = response.websitezoom;
zoombydomain = response.zoombydomain;if(zoombydomain == null)zoombydomain = true;
zoombypage = response.zoombypage;if(zoombypage == null)zoombypage = false;
// if empty use this
if(typeof websitezoom == "undefined" || websitezoom == null){
websitezoom = JSON.stringify({'https://www.example.com': ["90"], 'https://www.nytimes.com': ["85"]});
}
websitezoom = JSON.parse(websitezoom);

    chrome.tabs.query({active: true, currentWindow: true},
    function(tabs){
        if(tabs[0]){
        var job = tabs[0].url;
        if(typeof job !== "undefined"){
        var filtermatch = job.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/);
        if(zoombydomain == true){if(filtermatch){webjob = filtermatch[0];}}
        else{webjob = job;}
        if(zoomchrome == true){
            chrome.tabs.getZoom(tabs[0].id,function(zoomFactor){
                if(chrome.runtime.lastError){
                // if current tab do not have the content.js and can not send the message to local chrome:// page.
                // The line will excute, and log 'ERROR:  {message: "Could not establish connection. Receiving end does not exist."}' 
                //console.log('ERROR: ', chrome.runtime.lastError);
                }
                ratio = zoomFactor;
                if(ratio == null){ratio = 1}
                currentRatio = ratio;
                backgroundnumber = Math.round(ratio * 100);
                if(badge == true){
                chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                chrome.browserAction.setBadgeText({text:""+Math.round(currentRatio*100)+"", tabId: tabs[0].id});}
                else{chrome.browserAction.setBadgeText({text:""});}
            });
        }else if(zoomweb == true){
            chrome.tabs.sendMessage(tabs[0].id,{text: 'getwebzoom' },function(info){
                if(chrome.runtime.lastError){
                // if current tab do not have the content.js and can not send the message to local chrome:// page.
                // The line will excute, and log 'ERROR:  {message: "Could not establish connection. Receiving end does not exist."}' 
                //console.log('ERROR: ', chrome.runtime.lastError);
                }
                if(info == null || info == ""){info = 1}
                ratio = info;
                currentRatio = ratio;
                backgroundnumber = Math.round(ratio * 100);
                if(badge == true){
                chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                chrome.browserAction.setBadgeText({text:""+Math.round(currentRatio*100)+"", tabId: tabs[0].id } ); }
                else{chrome.browserAction.setBadgeText({text:"" });}
            });
        }else if(zoomfont == true){
            chrome.tabs.sendMessage(tabs[0].id,{text: 'getfontsize' },function(info){
                if(chrome.runtime.lastError){
                // if current tab do not have the content.js and can not send the message to local chrome:// page.
                // The line will excute, and log 'ERROR:  {message: "Could not establish connection. Receiving end does not exist."}' 
                //console.log('ERROR: ', chrome.runtime.lastError);
                }
                if(info == null || info == ""){info = 1}
                ratio = info;
                currentRatio = ratio;
                backgroundnumber = Math.round(ratio * 100);
                if(badge == true){
                chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
                chrome.browserAction.setBadgeText({text:""+Math.round(currentRatio*100)+"", tabId: tabs[0].id });}
                else{chrome.browserAction.setBadgeText({text:""});}
            });
        }
    }
    }


    });

});
}

// update on refresh tab
chrome.tabs.onUpdated.addListener(function(){
    //backgroundrefreshzoom();// Chrome bug, because screen size do not show the correct badge label
});

// update when click on the tab
chrome.tabs.onHighlighted.addListener(function(){
    backgroundrefreshzoom();
});

chrome.commands.onCommand.addListener(function(command){
if(command == "toggle-feature-zoomin"){
    zoomview(+1);
}else if(command == "toggle-feature-zoomout"){
    zoomview(-1);
}else if(command == "toggle-feature-zoomreset"){
    zoom(allzoomvalue*100);
}else if(command == "toggle-feature-magnify"){
    chrome.tabs.query({active: true, currentWindow: true},
        function(tabs){
            if(tabs[0]){
                chrome.tabs.sendMessage(tabs[0].id,{text: 'enablemagnifyingglass' });
            }
        });
}
});

// contextMenus
function onClickHandler(info, tab){
var str = info.menuItemId;var respage = str.substring(0, 8);var czl = str.substring(8);var reszoomin = str.substring(0, 8);var reszoomout = str.substring(0, 9);var reszoomreset = str.substring(0, 11);
if(respage == "zoompage"){
    chrome.storage.sync.get(['allzoom','allzoomvalue','badge','zoomchrome','zoomweb','websitezoom','zoombydomain','zoombypage','zoomfont'], function(response){
    allzoom = response.allzoom;
    allzoomvalue = response.allzoomvalue;if(allzoomvalue == null)allzoomvalue = 1; // default allzoomvalue value
    badge = response.badge;if(badge == null)badge = false;
    zoomchrome = response.zoomchrome;if(zoomchrome == null)zoomchrome = false;
    zoomweb = response.zoomweb;if(zoomweb == null)zoomweb = true;
    zoomfont = response.zoomfont;if(zoomfont == null)zoomfont = false;
    websitezoom = response.websitezoom;websitezoom = JSON.parse(websitezoom);
    zoombydomain = response.zoombydomain;if(zoombydomain == null)zoombydomain = true;
    zoombypage = response.zoombypage;if(zoombypage == null)zoombypage = false;
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
        if(zoomchrome == true){
            chrome.tabs.setZoom(tabs[0].id, czl/100);
        }else if(zoomweb == true){
            chrome.tabs.sendMessage(tabs[0].id,{text:'setbodycsszoom',value:czl/100});
        }else if(zoomfont == true){
            chrome.tabs.sendMessage(sender.tab.id,{text: 'setfontsize' });
            chrome.tabs.sendMessage(sender.tab.id,{text: 'changefontsize', value: Math.round(czl)});
        }
        if(badge == true){
            chrome.browserAction.setBadgeBackgroundColor({color:lightcolor}); 
            chrome.browserAction.setBadgeText({text:""+Math.round(czl)+""});}else{chrome.browserAction.setBadgeText({text:""});
        }
        var job = tabs[0].url;
        if(typeof job !== "undefined"){
        var filtermatch = job.match(/^[\w-]+:\/*\[?([\w\.:-]+)\]?(?::\d+)?/);
        if(zoombydomain == true){if(filtermatch){webjob = filtermatch[0];}}
        else{var webjob = job;}
        if(allzoom == true){
            // save for all zoom feature
            chrome.storage.sync.set({"allzoomvalue": czl/100});
        }else{
                var atbbuf = [];
                var domain;
                for(domain in websitezoom){atbbuf.push(domain);atbbuf.sort();}
                var i;
                var l = atbbuf.length;
                for(i = 0; i < l; i++){
                    if(atbbuf[i] == webjob){ //update
                        if(parseInt(czl/100) == 1){
                        // remove from list
                        delete websitezoom[''+atbbuf[i]+''];
                        break; // go out of the loop because it found the current web page to save the new zoom value
                        }else{
                        // update ratio
                        websitezoom[''+atbbuf[i]+''] = parseInt(czl);
                        break; // go out of the loop because it found the current web page to save the new zoom value
                        }
                    }else{
                        // add to list
                        websitezoom[''+webjob+''] = parseInt(czl);
                    }
                }
                // save for zoom feature
                chrome.storage.sync.set({"websitezoom": JSON.stringify(websitezoom)});
        }
        }
    });
    });
}
else if(reszoomin == "ctzoomin"){zoomview(+1);}
else if(reszoomout == "ctzoomout"){zoomview(-1);}
else if(reszoomreset == "ctzoomreset"){zoom(allzoomvalue*100);}
else if(info.menuItemId == "totlguideemenu"){window.open(linkguide, "_blank");}
else if(info.menuItemId == "totldevelopmenu"){window.open(donatewebsite, "_blank");}
else if(info.menuItemId == "totlratemenu"){window.open(writereview, "_blank");}
else if(info.menuItemId == "totlsharemenu"){window.open(zoomwebsite, "_blank");}
else if(info.menuItemId == "totlshareemail"){window.open("mailto:youremail?subject=Zoom extension&body=Hé, This is amazing. I just tried today this Zoom Browser extension"+zoomproduct+"", "_blank");}
else if(info.menuItemId == "totlsharetwitter"){var szoomproductcodeurl = encodeURIComponent("The Best and Amazing Zoom Browser extension "+zoomproduct+"");window.open("https://twitter.com/home?status="+szoomproductcodeurl+"", "_blank");}
else if(info.menuItemId == "totlsharefacebook"){window.open("https://www.facebook.com/sharer/sharer.php?u="+zoomproduct, "_blank");}
else if(info.menuItemId == "totlsubscribe"){chrome.tabs.create({url: linkyoutube, active:true})}
else if(info.menuItemId == "totlapplyresetzoom"){
function applyallresetzoom(){
    // Apply reset zoom to all tabs and in all window
    chrome.tabs.query({}, function(tabs){
        var i;
        var l = tabs.length;
        for(i = 0; i < l; i++){
            if(chrome.runtime.lastError){
            // if current tab do not have the content.js and can not send the message to local chrome:// page.
            // The line will excute, and log 'ERROR:  {message: "Could not establish connection. Receiving end does not exist."}' 
            //console.log('ERROR: ', chrome.runtime.lastError);
            }
            chrome.tabs.sendMessage(tabs[i].id,{text: 'refreshscreen' },function(info){});
        }
    });
}
applyallresetzoom();
}
}

// check to remove all contextmenus
chrome.contextMenus.removeAll(function(){
//console.log("contextMenus.removeAll callback");
});

// pageaction
var sharemenusharetitle = chrome.i18n.getMessage("sharemenusharetitle");
var sharemenuwelcomeguidetitle = chrome.i18n.getMessage("sharemenuwelcomeguidetitle");
var sharemenutellafriend = chrome.i18n.getMessage("sharemenutellafriend");
var sharemenusendatweet = chrome.i18n.getMessage("sharemenusendatweet");
var sharemenupostonfacebook = chrome.i18n.getMessage("sharemenupostonfacebook");
var sharemenuratetitle = chrome.i18n.getMessage("sharemenuratetitle");
var sharemenudonatetitle = chrome.i18n.getMessage("sharemenudonatetitle");
var sharemenusubscribetitle = chrome.i18n.getMessage("desremyoutube");
var sharemenuapplyzoomresettitle = chrome.i18n.getMessage("desapplyzoomreset");
var contexts = ["page_action", "browser_action"];

chrome.contextMenus.create({"title": sharemenuapplyzoomresettitle, "type":"normal", "id": "totlapplyresetzoom", "contexts": contexts});

try{
    // try show web browsers that do support "icons"
    // Firefox, Opera, Microsoft Edge

    chrome.contextMenus.create({"title": sharemenuwelcomeguidetitle, "type":"normal", "id": "totlguideemenu", "contexts": contexts, "icons":{"16": "images/IconGuide.png","32": "images/IconGuide@2x.png"}});
    chrome.contextMenus.create({"title": sharemenudonatetitle, "type":"normal", "id": "totldevelopmenu", "contexts": contexts, "icons":{"16": "images/IconDonate.png","32": "images/IconDonate@2x.png"}});
    chrome.contextMenus.create({"title": sharemenuratetitle, "type":"normal", "id": "totlratemenu", "contexts": contexts, "icons":{"16": "images/IconStar.png","32": "images/IconStar@2x.png"}});
}
catch(e){
    // catch web browsers that do NOT show the icon
    // Google Chrome
    chrome.contextMenus.create({"title": sharemenuwelcomeguidetitle, "type":"normal", "id": "totlguideemenu", "contexts": contexts});
    chrome.contextMenus.create({"title": sharemenudonatetitle, "type":"normal", "id": "totldevelopmenu", "contexts": contexts});
    chrome.contextMenus.create({"title": sharemenuratetitle, "type":"normal", "id": "totlratemenu", "contexts": contexts});
}

// Create a parent item and two children.
try{
    // try show web browsers that do support "icons"
    // Firefox, Opera, Microsoft Edge
    var parent = chrome.contextMenus.create({"title": sharemenusharetitle, "id": "totlsharemenu", "contexts": contexts, "icons":{"16": "images/IconShare.png","32": "images/IconShare@2x.png"}});
    var child1 = chrome.contextMenus.create({"title": sharemenutellafriend, "id": "totlshareemail", "contexts": contexts, "parentId": parent, "icons":{"16": "images/IconEmail.png","32": "images/IconEmail@2x.png"}});
    chrome.contextMenus.create({"title": "", "type":"separator", "id": "totlsepartorshare", "contexts": contexts, "parentId": parent});
    var child2 = chrome.contextMenus.create({"title": sharemenusendatweet, "id": "totlsharetwitter", "contexts": contexts, "parentId": parent, "icons":{"16": "images/IconTwitter.png","32": "images/IconTwitter@2x.png"}});
    var child3 = chrome.contextMenus.create({"title": sharemenupostonfacebook, "id": "totlsharefacebook", "contexts": contexts, "parentId": parent, "icons":{"16": "images/IconFacebook.png","32": "images/IconFacebook@2x.png"}});
}
catch(e){
    // catch web browsers that do NOT show the icon
    // Google Chrome
    var parent = chrome.contextMenus.create({"title": sharemenusharetitle, "id": "totlsharemenu", "contexts": contexts});
    var child1 = chrome.contextMenus.create({"title": sharemenutellafriend, "id": "totlshareemail", "contexts": contexts, "parentId": parent});
    chrome.contextMenus.create({"title": "", "type":"separator", "id": "totlsepartorshare", "contexts": contexts, "parentId": parent});
    var child2 = chrome.contextMenus.create({"title": sharemenusendatweet, "id": "totlsharetwitter", "contexts": contexts, "parentId": parent});
    var child3 = chrome.contextMenus.create({"title": sharemenupostonfacebook, "id": "totlsharefacebook", "contexts": contexts, "parentId": parent});
}

chrome.contextMenus.create({"title": "", "type":"separator", "id": "totlsepartor", "contexts": contexts});
try{
    // try show web browsers that do support "icons"
    // Firefox, Opera, Microsoft Edge
    chrome.contextMenus.create({"title": sharemenusubscribetitle, "type":"normal", "id": "totlsubscribe", "contexts":contexts, "icons":{"16": "images/IconYouTube.png","32": "images/IconYouTube@2x.png"}});
}
catch(e){
    // catch web browsers that do NOT show the icon
    // Google Chrome
    chrome.contextMenus.create({"title": sharemenusubscribetitle, "type":"normal", "id": "totlsubscribe", "contexts":contexts});
}

chrome.contextMenus.onClicked.addListener(onClickHandler);

chrome.storage.sync.get(['contextmenus','steps'], function(items){
    if(items['steps']){steps = items.steps;if(steps == null)steps = 10;}
    if(items['contextmenus'] == true){checkcontextmenus();}
});

// context menu for page and video
var menupage = null;
var contextmenuadded = false;
var contextarraypage = [];
var contextdefault = "100";
var book = [];

var contextzoomin = null;
var contextzoomout = null;
var contextzoomreset = null;

function checkcontextmenus(){
    //---
    chrome.storage.sync.get(['allzoomvalue','screenzoom','defaultallscreen','defaultsinglescreen','contexta','contextb'], function(items){
        if(items['allzoomvalue']){allzoomvalue = items.allzoomvalue;if(allzoomvalue == null)allzoomvalue = 1;}
        if(items['screenzoom']){screenzoom = items.screenzoom;}
        if(items['defaultallscreen']){defaultallscreen = items.defaultallscreen;if(defaultallscreen == null)defaultallscreen = true;}
        if(items['defaultsinglescreen']){defaultsinglescreen = items.defaultsinglescreen;if(defaultsinglescreen == null)defaultsinglescreen = false;}
        if(items['contexta']){contexta = items.contexta;if(contexta == null)contexta = true;}
        if(items['contextb']){contextb = items.contextb;if(contextb == null)contextb = false;}

        contextdefault = allzoomvalue*100;//get the default zoom value for that screen

        var currentscreen = screen.width+"x"+screen.height;

        if(defaultallscreen == true){} // no change
        else if(defaultsinglescreen == true){
            screenzoom = JSON.parse(screenzoom);
            var satbbuf = [];
            var domain;
            for(domain in screenzoom)
                satbbuf.push(domain);
                satbbuf.sort();
                var i;
                var l =  satbbuf.length;
                for(i = 0; i < l; i++){
                if(satbbuf[i] == currentscreen){
                    contextdefault = screenzoom[satbbuf[i]];
                }
                }
        }
        //---
    
        if(contextmenuadded == false){
        contextmenuadded = true;
        var contexts = ["page","selection","link","editable","image","audio","video"];
        var pagetitle = chrome.i18n.getMessage("name");
    
        if(contexta == true){
            book = Array();
    
            var k;
            for(k = 100; k <= 200; k = k + +steps){
                // skip the first value -> 100 
                if(k != 100){
                    book.push(k);
                }
            }
    
            var j;
            for(j = 100; j >= 10; j= j - steps){
                book.push(j);
            }

            // if the default zoom value is inside, then do nothing
            // else add this value in the context menu
            var mySet = new Set(book);
            var hascont = mySet.has(parseInt(contextdefault, 10)); // true
            if(hascont){}else{
                book.push(contextdefault);
            }
    
            book.sort(function(a, b){return b - a});
    
            var i;
            var l = book.length;
            for(i = 0; i < l; i++){
                if(contextdefault && contextdefault == book[i]){
                    menupage = chrome.contextMenus.create({"type":"radio", "checked" : true, "id": "zoompage"+book[i]+"", "title": "Zoom: "+ book[i] + "%", "contexts":contexts});
                }else{
                    menupage = chrome.contextMenus.create({"type":"radio","id": "zoompage"+book[i]+"","title": "Zoom: "+ book[i] + "%", "contexts":contexts});
                } 
            }
            contextarraypage.push(menupage);
        }
        else if(contextb == true){
            var titlezoomin = chrome.i18n.getMessage("titlezoomin");
            var titlezoomout = chrome.i18n.getMessage("titlezoomout");
            var titlezoomreset = chrome.i18n.getMessage("titlezoomreset");
            contextzoomin = chrome.contextMenus.create({"title": titlezoomin, "type":"normal", "id": "ctzoomin", "contexts":contexts});
            contextzoomout = chrome.contextMenus.create({"title": titlezoomout, "type":"normal", "id": "ctzoomout", "contexts":contexts});
            contextzoomreset = chrome.contextMenus.create({"title": titlezoomreset, "type":"normal", "id": "ctzoomreset", "contexts":contexts});
        }
        }

    });

}

function removecontexmenus(){
    // context style b
    if(contextzoomin != null){
        chrome.contextMenus.remove("ctzoomin");
    }
    if(contextzoomout != null){
        chrome.contextMenus.remove("ctzoomout");
    }
    if(contextzoomreset != null){
        chrome.contextMenus.remove("ctzoomreset");
    }
    contextzoomin = null;
    contextzoomout = null;
    contextzoomreset = null;
    // context style a
    var i;
    var l = book.length;
    for(i = 0; i < l; i++){
        menupage = chrome.contextMenus.remove("zoompage"+book[i]+"");
    }
    book = [];
    contextarraypage = [];
    contextmenuadded = false;
}

function refreshcontexmenus(){
    // context style b
    if(contextzoomin != null){
        chrome.contextMenus.remove("ctzoomin");
    }
    if(contextzoomout != null){
        chrome.contextMenus.remove("ctzoomout");
    }
    if(contextzoomreset != null){
        chrome.contextMenus.remove("ctzoomreset");
    }
    contextzoomin = null;
    contextzoomout = null;
    contextzoomreset = null;
    // context style a
    var i;
    var l = book.length;
    for(i = 0; i < l; i++){
        menupage = chrome.contextMenus.remove("zoompage"+book[i]+"");
    }
    book = [];
    contextarraypage = [];
    contextmenuadded = false;
    chrome.storage.sync.get(['contextmenus'], function(items){
        if(items['contextmenus'] == true){checkcontextmenus();}
    });
}

function handleZoomed(zoomChangeInfo){
    //console.log("Tab: " + zoomChangeInfo.tabId + " zoomed");
    //console.log("Old zoom: " + zoomChangeInfo.oldZoomFactor);
    //console.log("New zoom: " + zoomChangeInfo.newZoomFactor);
    chrome.storage.sync.get(['badge','zoomchrome'], function(response){
        badge = response.badge;if(badge == null)badge = false; // default badge false
        zoomchrome = response.zoomchrome;if(zoomchrome == null)zoomchrome = false; // default zoomchrome false
        if(zoomchrome == true){
            if(badge == true){
                // zoom changed
                // set the badge for the browser built-in zoom
                chrome.browserAction.setBadgeText({text:""+Math.round(zoomChangeInfo.newZoomFactor*100)+"", tabId: zoomChangeInfo.tabId });
            }
        }
    });
}
chrome.tabs.onZoomChange.addListener(handleZoomed);

document.addEventListener('DOMContentLoaded', function(){
chrome.storage.sync.get(['zoomdoubleclick','zoomnewsingleclick','zoomsingleclick'], function(response){
zoomdoubleclick = response.zoomdoubleclick;if(zoomdoubleclick == null)zoomdoubleclick = false; // default zoomdoubleclick false
zoomnewsingleclick = response.zoomnewsingleclick;if(zoomnewsingleclick == null)zoomnewsingleclick = false; // default zoomnewsingleclick false
zoomsingleclick = response.zoomsingleclick;if(zoomsingleclick == null)zoomsingleclick = true; // default zoomsingleclick true

if(zoomdoubleclick == true){doubleclickaction();}
else if(zoomnewsingleclick == true){doubleclickaction();}
else if(zoomsingleclick == true){regularaction();}
backgroundrefreshzoom();

});
});

chrome.storage.onChanged.addListener(function(changes, namespace){
    if(changes['steps']){if(changes['steps'].newValue){steps=changes['steps'].newValue;refreshcontexmenus()}}
    if(changes['allzoomvalue']){if(changes['allzoomvalue'].newValue){allzoomvalue=changes['allzoomvalue'].newValue;refreshcontexmenus()}}
    if(changes['contexta']){if(changes['contexta'].newValue == true){contexta=true;contextb=false;refreshcontexmenus()}}
    if(changes['contextb']){if(changes['contextb'].newValue == true){contexta=false;contextb=true;refreshcontexmenus()}}
    if(changes['contextmenus']){if(changes['contextmenus'].newValue == true){checkcontextmenus()}else{removecontexmenus()}}
    if(changes['defaultallscreen']){if(changes['defaultallscreen'].newValue == true){
        defaultallscreen=changes['defaultallscreen'].newValue;
        defaultsinglescreen=false;
        refreshcontexmenus();
        }
    }
    if(changes['defaultsinglescreen']){if(changes['defaultsinglescreen'].newValue == true){
        defaultsinglescreen=changes['defaultsinglescreen'].newValue;
        defaultallscreen=false;
        refreshcontexmenus();
        }
    }
    if(changes['badge']){
        if(changes['badge'].newValue == true){chrome.browserAction.setBadgeText({text:"100"});chrome.browserAction.setBadgeBackgroundColor({color:lightcolor})}
        else{chrome.browserAction.setBadgeText({text:""});}
    }
    if(changes['lightcolor']){
        if(changes['lightcolor'].newValue){chrome.browserAction.setBadgeBackgroundColor({color:changes['lightcolor'].newValue})}
    }
    if(changes['zoomdoubleclick']){if(changes['zoomdoubleclick'].newValue == true){zoomsingleclick = false;zoomnewsingleclick = false;zoomdoubleclick = true;doubleclickaction();backgroundrefreshzoom();}}
    if(changes['zoomnewsingleclick']){if(changes['zoomnewsingleclick'].newValue == true){zoomsingleclick = false;zoomnewsingleclick = true;zoomdoubleclick = false;doubleclickaction();backgroundrefreshzoom();}}
    if(changes['zoomsingleclick']){if(changes['zoomsingleclick'].newValue == true){zoomsingleclick = true;zoomnewsingleclick = false;zoomdoubleclick = false;regularaction();backgroundrefreshzoom();}}

    if(changes['zoommousescroll']){
        if(changes['zoommousescroll'].newValue == true){
            calladdscroll();
        }else{
            callremovescroll();
        }
    }

    if(changes['zoommousebuttonleft']){
        if(changes['zoommousebuttonleft'].newValue == true){
            callmousedirection();
        }
    }

    if(changes['zoommousebuttonright']){
        if(changes['zoommousebuttonright'].newValue == true){
            callmousedirection();
        }
    }

    if(changes['zoommousescrollup']){
        if(changes['zoommousescrollup'].newValue == true){
            callmousedirection();
        }
    }

    if(changes['zoommousescrolldown']){
        if(changes['zoommousescrolldown'].newValue == true){
            callmousedirection();
        }
    }
});

function calladdscroll(){
    chrome.tabs.query({}, function(tabs){
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id,{text: 'addscroll' });
        }
    });
}

function callremovescroll(){
    chrome.tabs.query({}, function(tabs){
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id,{text: 'removescroll' });
        }
    });
}

function callmousedirection(){
    chrome.tabs.query({}, function(tabs){
        for (var i=0; i<tabs.length; ++i) {
            chrome.tabs.sendMessage(tabs[i].id,{text: 'mousedirection' });
        }
    });
}

chrome.runtime.setUninstallURL(linkuninstall);

// convert from the chrome.local to chrome.sync
chrome.storage.local.get(['firstRun','version'], function(chromeset){
    // if yes, it use the chrome.local setting
    if(chromeset["firstRun"] == "false"){
        // move all settings from the local to sync
        if(chromeset["firstRun"] == "false"){chrome.storage.sync.set({"firstRun": false});}
        if(chromeset["version"] == "2.1"){chrome.storage.sync.set({"version": "2.1"});}
          
        // when done, clear the local
        chrome.storage.local.clear();
    }else{
        // already done converting the 'firstrun' (from chrome.local to chrome.sync) to false
        // or no firstrun found in chrome.local (empty value), then do the 'welcome page'
        initwelcome();
    }
});

function initwelcome(){
chrome.storage.sync.get(['firstRun'], function(chromeset){
if((chromeset["firstRun"]!="false") && (chromeset["firstRun"]!=false)){
  chrome.tabs.create({url: linkwelcomepage});
  var crrinstall = new Date().getTime();
  chrome.storage.sync.set({"firstRun": false, "version": "2.1", "firstDate": crrinstall});  
}
});
}