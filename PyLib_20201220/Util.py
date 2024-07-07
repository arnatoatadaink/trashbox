import re,os,math
from inspect     import signature 
from collections import OrderedDict
import time

randomValue = 200
splitSize   = 5
tfmodelArray = []

def isClassOrModule(_object):
    return hasattr(_object,"__dict__")

def isFunction(_value):
    return str(type(_value)) == "<class 'function'>"

# def isDict(_value):
#     return type(_value) == type({}) or type(_value) == type(OrderedDict)
def isDict(_value):
    return type(_value) == type({})

def isTupleOrList(_value):
    return type(_value) == type(()) or type(_value) == type([])

def makeTypeChecker(_type):
    def typeCheckerImple(_value):
        return type(_value) == type(_type)
    return typeCheckerImple

isString = makeTypeChecker("")
isList   = makeTypeChecker([])
isTuple  = makeTypeChecker(())
isInt    = makeTypeChecker(1)
isNone   = makeTypeChecker(None)

def getArgments(_inputValue):
    inputValue = _inputValue
    retValue   = []
    sigParams  = []
    isslice    = False
    if not isFunction(inputValue):
        if "__init__" in vars(inputValue).keys():
            inputValue = inputValue.__init__
            isslice    = True

    if isFunction(inputValue):
        sigParams = signature(inputValue).parameters

        for param in sigParams:
            paramValue  = sigParams[param]
            matchObject = re.match("^\*+",str(paramValue))
            if matchObject is not None:
                pos = matchObject.end()
            else:
                pos = 0
            retValue.append("{}{}".format("*"*pos,param))
        if isslice:
            retValue = retValue[1:]
        
    return retValue

def getCommonParameters(_inputValue,_parameters):
    if not isDict(_parameters):
        return _parameters
    ret      = {}
    argments = getArgments(_inputValue)
    for key in _parameters.keys():
        if key in argments:
            ret.update({key:_parameters[key]})
    return ret
            
def isKeyArgsFunction(_inputValue):
    argments = getArgments(_inputValue)
    if len(argments) > 0:
        if re.match("^\**",argments[-1]) is not None:
            return True
    return False

def hasArgFunction(_inputValue):
    return len(getArgments(_inputValue)) > 0

def getColIndex(_X=None,Names=[""],_colmns=[""]):
    ret  = []
    if _X is not None:
        cols = _X.columns
    else:
        cols = _colmns
    dic  = {}
    cnt = 0
    for col in cols:
        dic[col] = cnt
        cnt += 1
    for name in Names:
        if name in dic:
            ret.append(dic[name])
        else:
            ret.append(-1)
    return ret

def fetchNNDatas(_datas,_targetNames,_dataSuffix):
    ret = []
    for target in _targetNames:

#         target = convLayerName2DataName(target.name)
# #         if   target == "input":
# #             target = "X"
# #         elif target == "output":
# #             target = "y"
        targetName = "{}{}".format(target,_dataSuffix)
        
        if targetName in _datas:
            ret.append(_datas[targetName])
            
    if len(_targetNames) != len(ret):
        print("i/o no fetch")
        return None
    elif len(ret) == 1:
        ret = ret[0]
    return ret

def convLayerName2DataName(_layername):
    return re.sub("(_[0-9]+|)(/.+|)(:[0-9]+|)$","",_layername)


import numpy as np
import matplotlib as plt
from PIL import Image
import glob
def saveImagefromNumpy(_path,_ndarray):
    if _ndarray.shape[2] < 3:
        _ndarray = np.pad(_ndarray,[(0,0),(0,0),(3-_ndarray.shape[2],0)],mode="edge")
    _ndarray = _ndarray.astype(np.uint8)
    pil_img  = Image.fromarray(_ndarray,mode="RGB")
    pil_img.save(_path)

def makeReadPictures(_Inverse = False,_isGrayScale = False,_setDtype = "float32"):
    if _Inverse:
        def inverseFunc(_images):
            return 255 - _images
    else:
        def inverseFunc(_images):
            return _images
    
    def readPicturesImple(_path,_grayScale = _isGrayScale):
        files = glob.glob(_path)
        pics = None

        for i, file in enumerate(files):

            pic = Image.open(file)
            pic = pic.convert("RGB")
            pic = np.asarray(pic)
            if _grayScale:
                pic = np.average(pic,axis=(2))
                pic = pic.reshape(pic.shape+(1,))
            pic = inverseFunc(pic)
            pic = pic.astype("float32")
            pic = pic.reshape((1,)+pic.shape)
            if pics is not None:
                pics = np.concatenate([pics,pic],axis=0)
            else:
                pics = pic

        return pics
    return readPicturesImple 
readPicturesFloat32 = makeReadPictures(False,False)
readPicturesInt8    = makeReadPictures(False,False,"int8")

import requests,io,re
from PIL import Image

def makeGetUrlImageDomainConstraint(_domain = None):
    checkDomains = []
    if _domain is not None:
        checkDomains.append("http://"+_domain)
        checkDomains.append("https://"+_domain)
    def getUrlImageImple(_requrl):
        callRequest = len(checkDomains) == 0
        for checkDomain in checkDomains:
            if re.match(checkDomain,_requrl) is not None:
                callRequest = True
                break
            
        if not callRequest:
            return None
        
        getItem  = requests.get(_requrl)
        if str(getItem)[-5] != "2":
            return None
        getImage = Image.open(io.BytesIO(getItem.content))
        getItem.close()
        getImage = getImage.convert("RGB")
        getImage = np.asarray(getImage)
        getImage = getImage.astype("float32")
        getImage = getImage.reshape((1,)+getImage.shape)
        return getImage
    return getUrlImageImple

getFlickrImage = makeGetUrlImageDomainConstraint("farm[0-9]{1,2}.staticflickr.com/")
getCocoImage   = makeGetUrlImageDomainConstraint("images.cocodataset.org/")

import matplotlib.pyplot as plt
def makeShowImages(_plotScale = 1):
    if _plotScale < 0:
        return None
    elif _plotScale > 15:
        return None
    plotColumns = int(15//_plotScale)
    
    def showImagesImple(_images):

        images = _images #.transpose(0,3,1,2)

        if len(images.shape) == 3:
            images = images.reshape((1,)+images.shape)

        isGrayScale = images.shape[3] == 1
        
        for rowIndex in range(int(math.ceil(images.shape[0]/plotColumns))):
            fig,axs = plt.subplots(1,plotColumns,figsize=(_plotScale,_plotScale))
            for i in range(plotColumns):
                imageIndex = int(rowIndex * plotColumns + i)
                if plotColumns != 1:
                    ax = axs[i]
                else:
                    ax = axs
                if isGrayScale:
                    ax.imshow(images[imageIndex,:,:,0],cmap="gray")
                else:
                    ax.imshow(images[imageIndex,:,:,:])
            axs.axis("off")
        plt.show()

    return showImagesImple


showImages1  = makeShowImages(1)
showImages7  = makeShowImages(7)
showImages15 = makeShowImages(15)


import colour
def makeRGBColour(_length):
    # color使用時
    # 始点と末端で同色が使用されることを回避するため
    # 色配列のサイズ指定を1.1倍する
    N_theta = int(_length * 1.1)
    theta = np.linspace(0, 2*np.pi, N_theta)
    r = 0.2
    u = np.cos(theta)*r + 0.2009
    v = np.sin(theta)*r + 0.4610
    uv = np.dstack((u, v))

    # map -> xy -> XYZ -> sRGB
    xy = colour.Luv_uv_to_xy(uv)
    xyz = colour.xy_to_XYZ(xy)
    rgb = colour.XYZ_to_sRGB(xyz)
    rgb = colour.utilities.normalise_maximum(rgb, axis=-1)
    return rgb.reshape((-1,3))[:_length,:3]

import cv2
def makeRGBOpenCV2(_length):
    # color使用時
    # 始点と末端で同色が使用されることを回避するため
    # 色配列のサイズ指定を1.1倍する
    N_theta = int(_length * 1.1)
    luv = np.zeros((1, N_theta, 3)).astype(np.float32)
    theta = np.linspace(0, 2*np.pi, N_theta)
    luv[:, :, 0] = 80 # L
    luv[:, :, 1] = np.cos(theta)*100 # u
    luv[:, :, 2] = np.sin(theta)*100 # v

    rgb = cv2.cvtColor(luv, cv2.COLOR_Luv2RGB)
    return rgb.reshape(shape=(-1,3))[:_length,:3]

def makeLabel2rgb(_cats,_colorFunction = None,_useDissableLabel = True):
    if _colorFunction is None:
        colorFunction = makeRGBColour
    else:
        colorFunction = _colorFunction
        
    catLength   = len(_cats)
    colorPallet = colorFunction(catLength)
    if _useDissableLabel:
        colorPallet = np.concatenate([np.zeros((1,3)),colorPallet],axis=0)
    
    def label2rgbImple(_labelValue,_sparseLabel = True):
        # 空白のラベルは黒塗りにしたい、Predの場合、空白にならないので機能しない
#         labelValue  = (_labelValue.argmax(axis=-1) + 1) * ( _labelValue.sum(axis=-1) > 0 )
        labelValue  = _labelValue.argmax(axis=-1)
    
        # ラベルの出力件数が少ない場合、色を引き離すために有効ラベルを離れたIDの色に割り当て
        if _sparseLabel:
            uniqueArray = np.unique(labelValue)
            useColor    = np.linspace(0,catLength-1,len(uniqueArray),dtype="uint8")
            uniqueIndex = np.array([0]*len(colorPallet))
            for i in range(len(uniqueArray)):
                uniqueIndex[uniqueArray[i]] = useColor[i]
            labelValue = uniqueIndex[labelValue]
        return colorPallet[labelValue]
    return label2rgbImple

from skimage.color import label2rgb as label2rgbSkImage
def label2rgb(_labelImage):
    if _labelImage.shape[-1] > 1:
        argLabel = _labelImage.argmax(axis=-1)
    else:
        argLabel = _labelImage
    return label2rgbSkImage(argLabel)

def makeShowLabelImages(_showImages):
    def showLabelImagesImple(_labelImages):
        if len(_labelImages.shape) < 3:
            return None
        _showImages(label2rgb(_labelImages))
    return showLabelImagesImple
showLabelImages1  = makeShowLabelImages(showImages1)
showLabelImages7  = makeShowLabelImages(showImages7)
showLabelImages15 = makeShowLabelImages(showImages15)

import matplotlib.pyplot as plt,math,io
from IPython.display import display
from PIL             import Image
# %matplotlib inline

import matplotlib.pyplot as plt,math,io
from PIL import Image
# %matplotlib inline

def makeShowImagesForDisplayHandle(_plotScale = 1,_showHandle = None):
    if _plotScale < 0:
        return None
    elif _plotScale > 15:
        return None
    plotColumns = int(15//_plotScale)
    
    dispHandle = {"id":_showHandle}
        
    def showImagesForDisplayHandleImple(_images,_showHandle2 = None):

        if _showHandle2 is not None:
            dispHandle["id"] = _showHandle2
        if _images is None:
            return dispHandle["id"]
        
        images = _images #.transpose(0,3,1,2)
        

        if len(images.shape) == 3:
            images = images.reshape((1,)+images.shape)

        isGrayScale = images.shape[3] == 1
        
        plotRows = int(math.ceil(images.shape[0]/plotColumns))
        fig,axs = plt.subplots(plotRows,plotColumns,figsize=(_plotScale*plotColumns,_plotScale*plotRows))
        fig.subplots_adjust(0,0,1,1,0.1,0.1)

        if plotRows * plotColumns == 1:
            axs = [[axs]]
        elif plotRows == 1 or plotColumns == 1:
            axs = [axs]
            if plotColumns == 1:
                axs = np.array(axs).transpose(1,0)
            
        for rowIndex in range(plotRows):
            for colIndex in range(plotColumns):
                imageIndex = int(rowIndex * plotColumns + colIndex)
                if imageIndex >= images.shape[0]:
                    image = np.ones((1,1,3))
                else:
                    image = images[imageIndex]
                ax = axs[rowIndex][colIndex]
                if isGrayScale:
                    ax.imshow(image[:,:,0],cmap="gray")
                else:
                    ax.imshow(image[:,:,:])
                ax.axis("off")
            
        sio = io.BytesIO()
        fig.savefig(sio, format=None)
        plt.close(fig)
            
        if dispHandle["id"] is None:
            dispHandle["id"] = display(Image.open(sio),display_id=True)
        else:
            dispHandle["id"].update(Image.open(sio))
            
        return dispHandle["id"]
            
    return showImagesForDisplayHandleImple

# TODO
# showImagesとObjectDisplayの統合
# showImagesの実装もメモリ上へのPng出力を返すようにし、その関数を配置するように扱えばこれに組み込むことが可能
def makeShowObjectsForDisplayHandle(_showHandle = None):
    
    dispHandle = {"id":_showHandle}
        
    def showObjectsForDisplayHandleImple(_objects,_showHandle2 = None):

        if _showHandle2 is not None:
            dispHandle["id"] = _showHandle2
        if _objects is None:
            return dispHandle["id"]
            
        if dispHandle["id"] is None:
            dispHandle["id"] = display(_objects,display_id=True)
        else:
            dispHandle["id"].update(_objects)
            
        return dispHandle["id"]
            
    return showObjectsForDisplayHandleImple

def pyplot2image(plotfunc):
    plt_v = plt
    plt_v = plotfunc(plt_v)
    sio = io.BytesIO()
    plt_v.savefig(sio, format=None)
    plt_v.close()
    return Image.open(sio)

import numpy as np
import copy

def makeParameterLists(_params:dict):
    set_shape = []
    set_desc  = []
    
    for key in _params.keys():
        if type(_params[key]) == list:
            cnt  = len(_params[key])
            if cnt > 0:
                value = _params[key][0]
            else:
                value = 0
        else:
            cnt = 1
            value = _params[key]
        
        value_type = type(value)
        if value_type == int:
            value_type = np.int32
        elif value_type == float:
            value_type = np.float32
        elif value_type == str:
            value_type = np.object
        else:
            value_type = np.object
        
        set_desc.append((key,value_type))
        set_shape.append(cnt)
    ret_value  = np.empty(set_shape,set_desc)

    indices_base = []
    for i in range(len(set_shape)):
        reshapeKey = np.ones(len(set_shape),dtype=np.int8)
        reshapeKey[i] = -1
        setindices = np.arange(set_shape[i]).reshape(*reshapeKey)
        indices_base.append(setindices)
        
    reshapeKey = np.ones(len(set_shape),dtype=np.int8)
    
    key_index = -1
    ret_value_old = copy.copy(ret_value)
    for key in _params.keys():
        key_index += 1
        indices = copy.copy(indices_base)
        
        if type(_params[key]) != list:
            input_items = [_params[key]]
        else:
            input_items = _params[key]
            
        for i in range(len(input_items)):
            indices[key_index] = np.array([i]).reshape(*reshapeKey)
            ret_value[key][tuple(indices)] = input_items[i]
            
    return ret_value.reshape(-1)

def npvoid2dict(param:np.void):
    ret = {}
    for name in paramlist.dtype.names:
        ret[name] = param[name]
    return ret

def getConcatFunc(data):
    if type(data) == list:
        def concatfunc(under,upper):
            return under + upper
    elif type(data) == pd.core.frame.DataFrame:
        def concatfunc(under,upper):
            return pd.concat([under,upper],axis=0)
    else:
        def concatfunc(under,upper):
            return np.concatenate([under,upper],axis=0)
    return concatfunc

def getTimeStamp():
    timeStamp = time.localtime()
    timeStamp = "{:0>4}{:0>2}{:0>2}_{:0>2}{:0>2}{:0>2}".format(
                    timeStamp.tm_year,
                    timeStamp.tm_mon,
                    timeStamp.tm_mday,
                    timeStamp.tm_hour,
                    timeStamp.tm_min,
                    timeStamp.tm_sec)
    return timeStamp
