from tensorflow              import keras


import re,os,random as rn
from tensorflow.keras                  import Sequential,backend,Model
from tensorflow.keras.layers           import Dense, Dropout, Input, Conv2D
from tensorflow.keras.layers           import Activation, LeakyReLU
from tensorflow.keras.regularizers     import Regularizer,l1
from tensorflow.keras.optimizers       import SGD,RMSprop
from tensorflow.keras.optimizers       import Adagrad, Adadelta, Adam
from Util                              import isTupleOrList,isDict,isNone,isList,isFunction,getTimeStamp
from MyTestData                        import test
import numpy as np
import tensorflow as tf


numlabel = test.NUMERIC_LABEL
catlabel = test.CATEGORIE_LABEL

if isNone(globals().get("randomValue")):
    from Util import randomValue

kernelRand    = keras.initializers.RandomNormal(seed=randomValue)

def convLayer(layer):
    layerValue = layer

    if "kernel_initializer" in layerValue.__dict__:
        layerValue.kernel_initializer = kernelRand
    elif "seed" in layerValue.__dict__:
        layerValue.seed = randomValue
    return layerValue

def makeRegularizer(_l1Alpha=0.001,_l2Alpha=0.001):
    if _l1Alpha * _l2Alpha != 0:
        kreg = keras.regularizers.l1_l2(_l1Alpha,_l2Alpha)
    elif _l1Alpha + _l2Alpha == 0:
        kreg = None
    elif _l1Alpha == 0:
        kreg = keras.regularizers.l2(_l2Alpha)
    else:
        kreg = keras.regularizers.l1(_l1Alpha)
    return kreg

def saveModel(_model,_filePath,*args,**keyargs):
    import time
    timeStamp = time.localtime()
    timeStamp = "{:0>4}{:0>2}{:0>2}_{:0>2}{:0>2}{:0>2}".format(
                    timeStamp.tm_year,
                    timeStamp.tm_mon,
                    timeStamp.tm_mday,
                    timeStamp.tm_hour,
                    timeStamp.tm_min,
                    timeStamp.tm_sec)
    _model.save("{}_{}".format(_filePath,timeStamp),*args,**keyargs)
    
def loadModel(_filePath,_compile = False,_customObjects = None):
    loadact = LeakyReLU(0.001)
    loadact.__name__ = "leaky_re_lu"
    _customObjects.update({"leaky_re_lu":loadact,"leaky_re_lu_2":loadact})
    fitedModel = keras.models.load_model(_filePath,
                                         custom_objects=_customObjects,
                                         compile=_compile)
    return fitedModel
    
def saveModelWeight(_model,_filePath,_addname = ""):
    def printFile(_fileOut):
        def printImple(_text):
            print(_text,file=_fileOut)
        return printImple
    
    timeStamp = getTimeStamp()
    if _addname != "":
        filePath = _filePath + "_{}".format(_addname)
    else:
        filePath = _filePath
    _model.save_weights("{}_{}.hd5".format(filePath,timeStamp))
    f = open("{}_{}_summary.txt".format(filePath,timeStamp),"w")
    _model.summary(print_fn=printFile(f),line_length=180)
    f.close()
    
def modelReCompile(_model,_losses = {},_rates = {},_optimizer = None,_metrics = None):
    outputSize = len(_model.output_names)
    losses     = _model.loss
    lossWeight = _model.loss_weights
    
    for i in range(outputSize):
        key = _model.output_names[i]
        if _losses.get(key):
            losses[i]     = _losses[key]
        if _rates.get(key):
            lossWeight[i] = _rates[key]
    
    if _optimizer is not None:
        optimizer = _optimizer
    else:
        optimizer = _model.optimizer
    
    _model.compile(loss         = losses,
                   loss_weights = lossWeight,
                   optimizer    = optimizer,
                   metrics      = _metrics)
    return _model
    
def makeNNModelFunc(_l1Alpha=0,_l2Alpha=0,_BuildPrint = False,_summary = False):
            
    kernelReg  = makeRegularizer(_l1Alpha,_l2Alpha)
    
    if _BuildPrint:
        endText = "{}\r".format(" "*30)
        def buildPrint(*args):
            print(*args,end=endText)
        def printOver():
            print(" "*50,end="\r")
    else:
        def buildPrint(*args):
            return None
        printOver = buildPrint
        
    def makeNNModelImple(layers          = None,
                         connects        = None,
                         loss            = None,
                         losses          = None,
                         activator       = None,
                         rate            = 1.,
                         rates           = None,
                         optimizer       = None,
                         inputShape      = None,
                         inputType       = None,
                         outputShape     = None,
                         outputLabelType = None,
                         metrics         = None,
                         loadWeightPath  = None,
                         batchSize       = None,
                         IONameOrder     = None,
                         **_hyperParam):
        
        if layers is None:
            print("no layer")
            return None

        if   not isTupleOrList(layers) and not isDict(layers):
            print("layers type no supported")
            return None
        
        if len(layers) <= 0:
            print("layers no items")
            return None
        
        if isDict(layers) and not isDict(connects):
            print("layers and connects input type un matched")
            return None
        
        if optimizer is None:
            print("optimizer is none")
            return None
                
        # Connection上から見て、不足するLayer分のShapeとTypeがあるかチェックする
        
        # Layerの入力がListの場合
        if isTupleOrList(layers):
            needInputCount  = 1
            needOutputCount = 1
            if not isFunction(layers[0]):
                inputItemCount  = ( re.match("X|input" ,layers[ 0].name) is not None ) * 1
            if not isFunction(layers[-1]):
                outputItemCount = ( re.match("y|output",layers[-1].name) is not None ) * 1
        # Layerの入力がDictの場合
        else:
            needInputCount  = 0
            needOutputCount = 0
            checked = {}
            for key,value in connects.items():
                if isTupleOrList(value):
                    for invalue in value:
                        if checked.get(invalue) is None:
                            needInputCount  += re.match("X|input" ,invalue) is not None
                            checked[invalue] = True
                else:
                    if checked.get(value) is None:
                        needInputCount  += re.match("X|input" ,value) is not None
                        checked[value] = True
                needOutputCount += re.match("y|output",key)   is not None
            inputItemCount  = 0
            outputItemCount = 0
            for value in layers.values():
                if not isFunction(value):
                    inputItemCount  += ( re.match("X|input" ,value.name) is not None )
                    outputItemCount += ( re.match("y|output",value.name) is not None )
                
        if losses is None:
            losses = {}
        if loss is not None and "output" not in losses:
            losses.update({"output":loss})
        lossItemCount = len(losses)
        
        def checkNeedCount(itemCount,needCount,checkItem,label):
            if itemCount < needCount:
                if checkItem is None:
                    return "{} is none".format(label)
                if isDict(checkItem) or isList(checkItem):
                    checkItemCount = len(checkItem)
                else:
                    checkItemCount = 1
                if checkItemCount + itemCount < needCount:
                    return "{} is not enough".format(label)
            return None
        
        checkList = [
            [inputItemCount ,needInputCount ,inputShape      ,"input shape"     ], # for layer
            [inputItemCount ,needInputCount ,inputType       ,"input type"      ], # for layer
            [outputItemCount,needOutputCount,outputShape     ,"output shape"    ], # for output layer
            [outputItemCount,needOutputCount,outputLabelType ,"output labeltype"], # for activation
            [lossItemCount  ,needOutputCount,outputLabelType ,"losses"          ], # for losses
        ]
        for checkItem in checkList:
            errortext = checkNeedCount(*checkItem)
            if errortext is not None:
                print(errortext)
                return None
        
        if   isDict(outputShape) and isDict(outputLabelType):
            for key in outputShape.keys():
                if key not in outputLabelType.keys():
                    print("output shape and labeltype un collect")
                    return None
        elif isDict(outputShape) or isDict(outputLabelType):
            print("output shape and labeltype input type error")
            return None
        
        if isTupleOrList(IONameOrder):
            for order in IONameOrder:
                if not isDict(order):
                    print("I/O Name Order Error")
                    return None
        else:
            print("I/O Name Order Error")
            return None
        
        if len(IONameOrder[0]) != needInputCount:
            print("unfetch [connect input name] and [input name order]")
            return None
        elif len(IONameOrder[1]) != needOutputCount:
            print("unfetch [connect output name] and [output name order]")
            return None
        
        if rate is None:
            rate = 1.
        
        if rates is None:
            rates = {"y":rate}
        elif "y" not in rates:
            rates.update({"y":rate})
            
        if activator is None:
            activator = {}

        os.environ['PYTHONHASHSEED'] = str(randomValue)
        np.random.seed(randomValue)
        rn.seed(randomValue)

        if inputShape is not None:
            if isDict(inputShape):
                inputLayers = {}
                for key in inputShape.keys():
                    if key == "X":
                        setKey = "input"
                    else:
                        setKey = key
                    inputLayers[setKey] = Input(name=key,shape=tuple(inputShape[key]),dtype=inputType[key])
                inputLayer = inputLayers
            else:
                inputLayer = Input(name="X",shape=tuple(inputShape),dtype=inputType)
        else:
            inputLayer = None

        def getOutputSet(_name,_outshape,_outlabel):
            if isTupleOrList(_outshape):
                lastDim = _outshape[-1]
            else:
                lastDim = _outshape

            if   _outlabel == catlabel:
                if lastDim == 1:
                    setLoss      = 'binary_crossentropy'
                    setActivator = 'sigmoid'
                else:
                    # TODO pixel_wise_softmax これについて確認したい、pixel_wise_sigmoidは存在しないか？
                    # dice_coe向けのpixel数を考慮したsoftmaxのことであれば、sigmoidのように単一Classの場合、無視してよい認識
                    # _outshapeの入力次元はHWCかCなので2以上の場合、1d以上のpixelを持つと判断して処理する
#                     if isTupleOrList(_outshape) and len(_outshape) >= 2:
#                         setLoss      = 'dice_coe'
#                         setActivator = 'pixel_wise_softmax'
#                     else:
                    setLoss      = 'categorical_crossentropy'
                    setActivator = 'softmax'
            elif _outlabel == numlabel:
                setLoss         = 'mse'
                setActivator    = 'linear'
                
            if _name in activator:
                setActivator = activator[_name]

            if isTupleOrList(_outshape) and len(_outshape) >= 2:
                outputLayer = Conv2D(name               = _name,
                                     filters            = lastDim,
                                     kernel_size        = (1,1),
                                     activation         = setActivator,
                                     kernel_initializer = kernelRand,
                                     kernel_regularizer = kernelReg)
            else:
                outputLayer = Dense(name               = _name,
                                    units              = lastDim,
                                    activation         = setActivator,
                                    kernel_initializer = kernelRand,
                                    kernel_regularizer = kernelReg)
                
            return {"Loss":setLoss,"Layer":outputLayer}
        
        if outputShape is not None:
            if isDict(outputShape):
                outputLayers = {}
                outputlosses = {}
                for key in outputShape.keys():
                    if key == "y":
                        setKey = "output"
                    else:
                        setKey = key
                    outshape = outputShape[key]
                    outlabel = outputLabelType[key]

                    outset = getOutputSet(key,outshape,outlabel)

                    if setKey not in losses:
                        losses.update({setKey:outset["Loss"]})
                    if isDict(layers):
                        if setKey not in layers.keys():
                            outputLayers[setKey] = outset["Layer"]
                outputLayer = outputLayers
                if loss is None and "output" in losses.keys():
                    loss = losses["output"]
            else:
                outset = getOutputSet("y",outputShape,outputLabelType)

                if "output" not in losses:
                    losses.update({"output":outset["Loss"]})
                if loss is None:
                    loss = outset["Loss"]
                outputLayer = outset["Layer"]
        else:
            outputLayer = None
                    
        if type(layers) == type([]):
            # 単一入力、単一結合、単一出力処理
            tfmodel = Sequential()

            # 出力層、画像データとしての出力は検討課題
            if inputLayer is not None:
                layers = [inputLayer] + layers
            if outputLayer is not None:
                layers = layers + [outputLayer]

            for layer in layers:
                layerValue = convLayer(layer)
                tfmodel.add(layerValue)

        elif type(layers) == type({}):
            # 単一入力、複数結合、単一出力処理
            
            # 任意のコネクション形成処理
            # 辞書型の場合として処理
            # 辞書型としてレイヤーに名前を付け
            # レイヤーの名前割り当てを辿って入力値を結合する
            # 命名ルール：[a-zA-Z]+_[0-9]+
            # 入力キー：input
            # 出力結合キー：merge_[0-9]+　レイヤー名ではなく、名称の入力に依存させる
            # 出力キー：output
            if inputLayer is not None:
                if isDict(inputLayer):
                    layers.update(inputLayer)
                else:
                    layers.update({'input':inputLayer})
            
            if outputLayer is not None:
                if isDict(outputLayer):
                    layers.update(outputLayer)
                else:
                    layers.update({'output':outputLayer})
                    
            
            for layerName in layers.keys():
                buildPrint("convLayer {:<30}".format(layerName))
                layers[layerName]      = convLayer(layers[layerName])
                
            buildPrint("convLayer over{}".format(" "*30))

            for layerName,connectLayerNames in connects.items():
                buildPrint("setup connect {:<30}".format(layerName))
                if list == type(connectLayerNames):
                    connectLayer = []
                    shapes = ""
                    for connectLayerName in connectLayerNames:
                        connectLayer = connectLayer + [layers[connectLayerName]]
                        shapes += "{}:{}".format(connectLayerName,list(layers[connectLayerName].get_shape()))
                    buildPrint("concat : {}".format(shapes))
                    connectLayer = keras.layers.concatenate(connectLayer)
                elif str == type(connectLayerNames):
                    connectLayer = layers[connectLayerNames]
                else:
                    print("connectSetError")
                buildPrint("connectSet {:<30}".format(layerName),"inputShape :{}".format(list(connectLayer.get_shape())))
                layers[layerName] = layers[layerName](connectLayer)
                
            buildPrint("connectSet over{}".format(" "*30))

            def checkOutputShape(_layerShape,_outputShape):
                if len(_layerShape) != len(_outputShape):
                    return False
                for i in range(len(_layerShape)):
                    if _layerShape[i] != _outputShape[i]:
                        return False
                return True
            
            if outputShape is not None:
                if not isDict(outputShape):
                    if isDict(layers):
                        createdOutputShape = list(layers["output"].get_shape()[1:])
                    else:
                        createdOutputShape = list(layers[-1].get_shape()[1:])
                    if not checkOutputShape(createdOutputShape,outputShape):
                        print("output shape unmatched : {}".format("output"),
                              "layer tensor shape :{}".format(createdOutputShape),
                              "data shape :{}".format(outputShape))
                        return None
                elif isDict(outputShape):
                    for key in outputShape.keys():
                        if key == "y":
                            setKey = "output"
                        else:
                            setKey = key
                        if setKey not in connects.keys():
                            continue
                        createdOutputShape = list(layers[setKey].get_shape()[1:])
                        if not checkOutputShape(createdOutputShape,outputShape[key]):
                            print("output shape unmatched : {}".format(setKey),
                                  "layer tensor shape :{}".format(createdOutputShape),
                                  "data shape :{}".format(outputShape))
                            return None
                
            inputLayers          = [None] * needInputCount
            outputLayers         = [None] * needOutputCount
            outputLayerNames     = [None] * needOutputCount
            for layerName in layers.keys():
                
                if re.match("(in|out)put",layerName) is None:
                    continue
                    
                if layerName   == "input":
                    checkName = "X"
                elif layerName == "output":
                    checkName = "y"
                else:
                    checkName = layerName
                    
                if   re.match("input",layerName) is not None:
                    isOutput            = False
                    checkOrder          = IONameOrder[0]
                    error_pattern_text1 = "i/o name error need input layer name [input_～]"
                    error_pattern_text2 = "i/o name error haven't input name order"
                elif re.match("output",layerName) is not None:
                    isOutput            = True
                    checkOrder          = IONameOrder[1]
                    error_pattern_text1 = "i/o name error need output layer name [output_～]"
                    error_pattern_text2 = "i/o name error haven't output name order"
                    
                if re.search(checkName,layers[layerName].name) is None:
                    print(error_pattern_text1)
                    return None
                if checkName not in checkOrder:
                    print(error_pattern_text2)
                    return None
                
                orderIndex = checkOrder[checkName]
                if isOutput:
                    outputLayers[orderIndex] = layers[layerName]
                    outputLayerNames[orderIndex] = layerName
                else:
                    inputLayers[orderIndex] = layers[layerName]
            
            tfmodel = Model(inputs=inputLayers,outputs=outputLayers)
            if len(outputLayers) >= 2:
                loss         = []
                loss_weights = []
                for layerName in outputLayerNames:
                    
                    if layerName in losses:
                        lossFunction = losses[layerName]
                    else:
                        print("un set losses")
                        return None
                    loss.append(lossFunction)
                    if layerName not in rates:
                        rate = 1.
                    else:
                        rate = rates[layerName]
                    loss_weights.append(rate)
            else:
                loss_weights = None
            
            if loss is None:
                print("loss create error loss is None")
                return None
            elif isTupleOrList(loss):
                if len(loss) == 0:
                    print("loss create error loss is empty")
                    return None
            
#         optimizer = convParam2Define(optimizer)

        optimizer = tf.train.experimental.enable_mixed_precision_graph_rewrite(optimizer)

        printOver()
        tfmodel.compile(loss = loss,loss_weights = loss_weights, optimizer = optimizer,metrics = metrics)

        if loadWeightPath is not None:
            tfmodel.load_weights(loadWeightPath)
            
        if _summary:
            tfmodel.summary(line_length=133)
            
        return tfmodel
    return makeNNModelImple

makeNNModel = makeNNModelFunc()
