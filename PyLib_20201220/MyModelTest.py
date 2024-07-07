from sklearn.metrics   import mean_squared_error
from sklearn.ensemble  import AdaBoostRegressor,AdaBoostClassifier
from sklearn.pipeline  import Pipeline
import re
from MyNeuralNetworkTF import makeNNModel as makeNNModelDefault
from sklearn.metrics       import log_loss
from Util import getArgments,isDict,isList,isFunction,fetchNNDatas,isTupleOrList
import tensorflow as tf
import gc
import copy

class modelTest:
    # ロス関数
    def __init__(self,_test,_model,_lossFunction,_evalFunction=None,_boosting=None,**_hyperParams):
        
        self.getRandomSeed = self.makeGetRandomSeed(_test)
        
        self.test         = _test
        self.isList       = False
        self.isDict       = False
        self.boosting     = _boosting
        self.model        = None
        self.inputParams  = {}
        self.lossFunction = _lossFunction
        self.evalFunction = _evalFunction

        if "random_state" not in _hyperParams:
            _hyperParams["random_state"]       = self.getRandomSeed()
            
        if self.boosting is not None:
            _hyperParams["boost_random_state"] = _hyperParams["random_state"]

        self.setModels(_model,**_hyperParams)
    
    # 乱数未指定版の為に乱数シード指定関数を設ける
    def makeGetRandomSeed(self,_test):
        def getRandomSeedImple():
            return _test.getRandom()
        return getRandomSeedImple
    
    # パイプを考慮したモデルの設定
    def setModels(self,_model,**_hyperParams):

        model = _model
        if type(model) == type({}):
            self.isDict = True
            keyNames    = model.keys()
            model       = list(model.items())
            def getStepName(i):
                return keyNames[i]
        else:
            def getStepName(i):
                return "{}".format(i)
        
        if type(model) == type([]):
            self.isPipe = True
        else:
            model = list(_model)

        stepsArray = []
        
        for i in range(len(model)):
            modelItem = model[i]
            argNames   = getArgment(modelItem)

            inputArgs  = {}
            tempArgs   = {}
            stepName  = getStepName(i)

            if self.isDict:
                prefix = "{}_".format(stepName)
            else:
                prefix = ""

            for argName in argNames:
                checkKey = "{}{}".format(prefix,argName)
                if checkKey in _hyperParams:
                    inputArgs[argName] = _hyperParams[checkKey]
                    tempArgs[checkKey] = _hyperParams[checkKey]

            self.inputParams.update(tempArgs)
            stepsArray.append((stepName,modelItem(**inputArgs)))

        if self.isPipe:
            self.model = Pipeline(steps=stepsArray)
        else:
            self.model = stepsArray[0][1]
            
        if self.boosting is not None:

            argNames   = getArgment(self.boosting)

            inputArgs  = {}
            tempArgs   = {}
            prefix     = "boost_"

            for argName in argNames:
                
                if argName == "base_estimator":
                    inputArgs[argName] = self.model
                    continue
                
                checkKey = "{}{}".format(prefix,argName)
                if checkKey in _hyperParams:
                    inputArgs[argName] = _hyperParams[checkKey]
                    tempArgs[checkKey] = _hyperParams[checkKey]

            self.inputParams.update(tempArgs)
            self.model = self.boosting(**inputArgs)
            
    def getTrainedParameters(self):
        
        if self.boosting is not None:
            model = self.model.base_estimator
        else:
            model = self.model
            
        if type(model) == Pipeline:
            return self.getParams2ModelList(model)
        else:
            return self.getParams2Model(model)

    def getParams2ModelList(self,_model,_prefix = "",_suffix = ""):
        ret = {}
        ret.update(self.getParams2Model(_model,_prefix,_suffix))
        for stepName,model in _model.steps:
            if self.isDict:
                ret.update(self.getParams2Model(model,stepName,_suffix))
            else:
                ret.update(self.getParams2Model(model,_prefix,_suffix))
        return ret

    def getParams2Model(self,_model,_prefix = "",_suffix = ""):
        ret = {}

        if _prefix != "":
            prefix = "{}_".format(_prefix)
        else:
            prefix = ""
            
        if _suffix != "":
            suffix = "_{}".format(_suffix)
        else:
            suffix = ""
        
        for valueKey,key in [["coef_","wait"],["intercept_","bias"],["feature_importances_","impotances"]]:
            if ( valueKey in _model.__dict__ ):
                ret["{}{}{}".format(prefix,key,suffix)] = _model.__dict__[valueKey]
            
        return ret
    
    def modelKick(self,_model,X_train,y_train,X_test,y_test,**_dataArgs):
        ret = {}
        _model.fit(X_train, y_train)
        
        y_pred_train = _model.predict(X_train)
        loss_train   = self.lossFunction(y_train, y_pred_train)
        y_pred_test  = _model.predict(X_test)
        loss_test    = self.lossFunction(y_test,  y_pred_test)
        
        ret.update({"loss_train"  :loss_train,
                    "loss_test"   :loss_test,
                    "y_train"     :y_train,
                    "y_test"      :y_test,
                    "y_pred_train":y_pred_train,
                    "y_pred_test" :y_pred_test})
        
        if self.evalFunction is not None:
            eval_train   = self.evalFunction(y_train, y_pred_train)
            eval_test    = self.evalFunction(y_test,  y_pred_test)
            ret.update({"eval_train":eval_train,
                        "eval_test" :eval_test})
        return ret
        
    # モデルの実行
    def do(self,_suffix = ""):
        loss_ret = self.test.do(self.model,self.modelKick)
        ret = {}
        ret.update(self.inputParams)
        ret.update(self.getTrainedParameters())
        ret.update(loss_ret)
        return ret    

# for stacking model
# modelTestを複数コントロールする
# modelKick時に実行するのは内部設定された全てのModel
# TODO：Stackの前処理モデルにおいて、表現力の高いモデルで、全データを使用すると
#       Trainのデータに対して過学習の状態になってしまう
#       前処理モデルは精度を下げるかデータを減らすこと
class modelTestStack(modelTest):
    def __init__(self,_test,_testFuncs,_testFuncLabel = None):
        self.testFuncs     = _testFuncs
        if type(_testFuncLabel) == type(None):
            self.testFuncLabel = [""] * len(_testFuncs)
        else:
            self.testFuncLabel = _testFuncLabel
        # testデータにはtestFunc数-1の予測列を追加する
        self.test      = _test
        # 対応する名前の列をチェックして更新
        # 既存の予測値を全て初期化する
        addColumns = []
        for i in range(len(_testFuncs)-1):
            for j in range(len(_test.columns["y"])):
                addColumns.append("y_pred_{}_{}".format(i,j))
        self.test.appendColumns(addColumns)
        self.test.resetColumns(addColumns)
    
    # モデルの実行
    def do(self,**_hyperParam):
        # 各modelTestを実行する
        # 実行結果をTest上のパラメーターに反映して更新し
        # 後続のモデルを実行する
        for i,testFunc,testFuncLabel in zip(range(len(self.testFuncs)),self.testFuncs,self.testFuncLabel):
            ret = testFunc(self.test,_hyperParam,testFuncLabel)
            if i != len(self.testFuncs):
                columns = []
                for j in range(len(_test.columns["y"])):
                    columns += ["y_pred_{}_{}".format(i,j)]
                self.test.updateColumns(columns,ret["y_pred_train"],ret["y_pred_test"])
        return ret
    
class modelTestNorand(modelTest):
    # 乱数不定版
    def makeGetRandomSeed(self,_test):
        def getRandomSeedImple(self):
            return None
        return getRandomSeedImple

# モデルを継承する都合上Ksplitなどと併用できない
class modelTestNN(modelTest):
    # NNモデルの生成版
    # 実装はパラメーターから復元する
    def setModels(self,_makeNNModel,
                  preCompiledModel = None,fitmodel = None,
                  epochs = 1,
                  batch_size = 32,
                  verbose = 0,
                  predFunction = None,
                  **keyargs):
        
        self.epochs          = epochs
        self.batch_size      = batch_size
        self.verbose         = verbose
        if predFunction is not None:
            self.getPredicts = predFunction
        
        # モデル生成、既存のモデルが存在する場合は、継続使用する
        # 取り込み優先順位
        # １．訓練済モデル
        # ２．事前コンパイル済モデル
        # ３．外部のメイクモデル関数
        # ４．標準のメイクモデル関数
        if fitmodel is not None:
            self.model = fitmodel
        elif preCompiledModel is not None:
            self.model = preCompiledModel
        # 入力されたmodelの値が関数の場合はそれを使用して処理を実行する
        elif isFunction(_makeNNModel):
            self.model = _makeNNModel(**keyargs)
        # 何も設定されていない場合は基本のモデル生成関数を呼び出す
        else:
            self.model =  makeNNModelDefault(**keyargs)
            
        if self.model is None:
            print("model create error")

    def modelKick(self,_model,**_datas):
        
        X_train = fetchNNDatas(_datas,_model.input_names ,"_train")
        X_test  = fetchNNDatas(_datas,_model.input_names ,"_test")
        y_train = fetchNNDatas(_datas,_model.output_names,"_train")
        y_test  = fetchNNDatas(_datas,_model.output_names,"_test")
        
        dataset_train = _datas.get("dataset_train")
        dataset_test  = _datas.get("dataset_test")

        tf.keras.backend.clear_session()
        
        if X_train is not None or dataset_train is not None:
            if dataset_train is None:
                _model.fit(X_train,y_train,
                           batch_size       = self.batch_size,
                           verbose          = self.verbose,
                           epochs           = self.epochs)
            else:
                _model.fit(dataset_train.batch(self.batch_size),
                           verbose          = self.verbose,
                           epochs           = self.epochs)
        
        ret = {"fitmodel":_model}
        results = self.getResult(_model,X_train,y_train)
        for key in results:
            ret.update({"{}_{}".format(key,"train"):results[key]})
        results = self.getResult(_model,X_test ,y_test)
        for key in results:
            ret.update({"{}_{}".format(key,"test"):results[key]})
        return ret
    
    def getResult(self,model,X,y):
        if X is None:
            return {}
        ret = {}
        
        if isTupleOrList(y):
            y_dict = {}
            for i in range(len(model.outputs)):
                key = model.output_names[i]
                y_dict[key] = y[i]
            y = y_dict
        elif not isDict(y):
            y = {"y":y}
        ret.update(y)
        
        preds = self.getPredicts(model,X)
        ret.update(preds)
        
        def setresultprefix(_function,_prefix,_y,_y_pred):
            value = _function(_y, _y_pred)
            if not isDict(value):
                return {_prefix:value}
            else:
                ret = {}
                for key in value:
                    setkey = re.sub("^(output|y)",_prefix,key)
                    ret.update({setkey:value[key]})
                return ret
        ret.update(setresultprefix(self.lossFunction,"loss",y,preds))
        if self.evalFunction is not None:
            ret.update(setresultprefix(self.evalFunction,"eval",y,preds))

        return ret
    
    def getPredicts(self,model,X):
        ret = {"y_pred":None}
        
        y_pred = model.predict(X)

        # outputの戻り値には名前が無いので
        # lossに渡す前に命名する
        if len(model.outputs) >= 2:
            pred_dict = {}

            for i in range(len(model.outputs)):
                key = model.output_names[i]
                pred_dict[key] = y_pred[i]

            y_pred = pred_dict
        if len(model.outputs) <= 1:
            ret.update({"y_pred":y_pred})
        else:
            for key in y_pred.keys():
                ret.update({"{}_pred".format(key):y_pred[key]})
        return ret

def NNMake(_test,_hyperParam,_lossFunction = log_loss,_makeNNModel = makeNNModelDefault):
    param = copy.copy(_hyperParam)
    param["inputShape"]      = _test.getInputShape()
    param["inputType"]       = _test.getInputType()
    param["outputShape"]     = _test.getOutputShape()
    param["outputLabelType"] = _test.getOutputLabelType()
    return modelTestNN(_test,_makeNNModel,_lossFunction,**param).model
