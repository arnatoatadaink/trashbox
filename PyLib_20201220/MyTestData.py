# # データに合わせたテスト実行クラスの実装
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display         import display
from Util import isDict,isList,isTupleOrList,isFunction,isKeyArgsFunction,hasArgFunction,isNone,fetchNNDatas
import tensorflow as tf

import re,math,gc
from Count import counter as countobj
from MyLayers import MyReshapeLayer

# TODO
# TestOrder系にデータの件数についてチェックし、エラー警告する機能を追加したい

def toArray(_data):
    if _data is not None:
        if len(_data) > 0:
            return np.array(_data)
    return None

class test:
    NUMERIC_LABEL   = 0
    CATEGORIE_LABEL = 1
    def __init__(self):
        self.columns  = {"y":[""],"X":[""]}
        self.Datas   = {
                         "X_train":[],
                         "y_train":[],
                         "X_test" :[],
                         "y_test" :[],
                       }
        self.Random  = -1
        self.Split   = -1
        
    def setRandom(self,_random):
        self.Random = _random
        
    def getRandom(self):
        return self.Random
        
    # X,y に関する名称出力
    def getColumnsName(self,_y,_X):
        if type(_y) == pd.Series:
            ycolumns = [_y.name]
        elif type(_y) == pd.DataFrame:
            ycolumns = list(_y.columns)
        else:
            ycolumns = list(range(_y.shape[len(_y.shape)-1]))
            
        if type(_X) == pd.Series:
            Xcolumns = [_X.name]
        elif type(_X) == pd.DataFrame:
            Xcolumns = list(_X.columns)
        else:
            print("unRef type as : {}".format(type(_X)))
        self.columns = {"y":list(ycolumns),"X":Xcolumns}
        
        return self.columns

    def getIONameOrder(self):
        return self.getIONameOrderImple(self.Datas)
        
    # Datas に関する名称出力
    def getIONameOrderImple(self,_datas):
        inputDataNames  = {}
        outputDataNames = {}
        for key in _datas.keys():
            if re.search("_train$",key) is not None:
                key = re.sub("_train$","",key)
                if   re.match("X|input" ,key) is not None:
                    inputDataNames[key]  = len(inputDataNames)
                elif re.match("y|output",key) is not None:
                    outputDataNames[key] = len(outputDataNames)
        return (inputDataNames,outputDataNames)
        
    def getDataProperty(_datas,_prefix,_propertyfunc):
        ret = {}
        for key in _datas.keys():
            if _datas[key] is None:
                continue
            if re.search("_train$",key) is not None:
                if re.match(_prefix,key) is not None:
                    setKey = re.sub("_train$","",key)
                    ret[setKey] = _propertyfunc(_datas[key])
        
        if len(ret.keys()) == 1:
            for values in ret.values():
                ret = values
        elif len(ret.keys()) == 0:
            ret = None
            
        return ret
    
    def getShape(_data):
        return _data.shape[1:]
    
    def getType(_data):
        if   _data.dtype == np.float32:
            return "float32"
        elif _data.dtype == np.float16:
            return "float16"
        else:
            return None

    def getLabelType(_data):
        values     = np.unique(_data)
        otherLabel = len(values) - np.in1d(values,[0,1]).sum()
        # データに0、1以外を含む場合、決定問題として数値ラベル
        # データに0、1のみを含む場合、分類問題として属性ラベル
        if otherLabel > 0:
            return test.NUMERIC_LABEL
        else:
            return test.CATEGORIE_LABEL
    
    def getInputShape(self):
        return self.getInputShapeImple(self.Datas)

    def getInputShapeImple(self,_datas):
        return test.getDataProperty(_datas,"(X|input)_",test.getShape)
    
    def getInputType(self):
        return self.getInputTypeImple(self.Datas)
    
    def getInputTypeImple(self,_datas):
        return test.getDataProperty(_datas,"(X|input)_",test.getType)

    def getOutputShape(self):
        return self.getOutputShapeImple(self.Datas)
    
    def getOutputShapeImple(self,_datas):
        return test.getDataProperty(_datas,"(y|output)_",test.getShape)
    
    def getOutputLabelType(self):
        return self.getOutputLabelTypeImple(self.Datas)
    
    def getOutputLabelTypeImple(self,_datas):
        return test.getDataProperty(_datas,"(y|output)_",test.getLabelType)

    def setSplit(self,_split):
        self.Split = _split
    
    def getSplit(self):
        return self.Split
    
    def do(self,_model,modelKick):
        return {"loss_train":0,"loss_test":0,
                "y_train":[],"y_test":[],
                "y_pred_train":[],"y_pred_test":[]}
    
    def scaling(self,_X_train,_X_test):
        ret = []
        scaler = StandardScaler()
        scaler.fit(_X_train)
        ret.append(scaler.transform(_X_train))
        if _X_test is not None:
            ret.append(scaler.transform(_X_test))
        else:
            ret.append(None)
        return ret
    
    def getViewSet(self):
        ret = []
        ret_df = pd.DataFrame(self.Datas["y_train"],columns=self.columns["y"])
        ret_df[self.columns["X"]] = pd.DataFrame(self.Datas["X_train"])
        ret.append(ret_df)
        ret_df = pd.DataFrame(self.Datas["y_test"],columns=self.columns["y"])
        ret_df[self.columns["X"]] = pd.DataFrame(self.Datas["X_test"])
        ret.append(ret_df)
        return ret

    def plot(self,_colorRange=[0x003300,0xEE00EE]):
        # 標準化
        viewSet = self.getViewSet()

        colorset    = np.round(np.linspace(_colorRange[0],_colorRange[1],len(viewSet)))
        color_codes = {}
        cnt         = 0
        for color in colorset:
            colorValue       = (int(color//0x10000),int(color//0x100%0x100),int(color%0x100))
            color_codes[cnt] = ('#%02X%02X%02X' % (colorValue[0],colorValue[1],colorValue[2]))
            cnt += 1

        colorIndexs = []
        cnt = 0
        first = True
        for view in viewSet:
            colorIndexs += [cnt] * len(view)
            cnt += 1
            if first == True:
                first = False
                viewALL = view
            else:
                viewALL = viewALL.append(view)

        colors = [color_codes[x] for x in colorIndexs]
        display(viewALL.describe())
        display(viewALL.info())
                               
        pd.plotting.scatter_matrix(viewALL, figsize=(12,12),color=colors)
        plt.show()
        sns.heatmap(viewALL.corr())
        plt.show()
        
    def appendColumns(self,_columns):
        cnt = 0
        for key in _columns:
            if key not in self.columns["X"]:
                cnt += 1
                self.columns["X"].append(key)
        if cnt > 0:
            trainSize = self.Datas["X_train"].shape[0]
            self.Datas["X_train"] = np.concatenate((self.Datas["X_train"],np.zeros(trainSize * cnt).reshape(trainSize,cnt)),axis=1)
            testSize  = self.Datas["X_test"].shape[0]
            self.Datas["X_test"]  = np.concatenate((self.Datas["X_test"] ,np.zeros(testSize  * cnt).reshape(testSize ,cnt)),axis=1)

    def updateColumns(self,_columns,_trainValues,_testValues):
        index = getColIndex(None,_column,self.columns["X"])
        self.Datas["X_train"][:,index] = _trainValues.reshape(-1,len(_column))
        self.Datas["X_test"][:,index]  = _testValues.reshape(-1,len(_column))
        
    def resetColumns(self,_columns):
        index = getColIndex(None,_columns,self.columns["X"])
        self.Datas["X_train"][:,index] = 0
        self.Datas["X_test"][:,index]  = 0

class holdOutTest(test):
    def __init__(self,_X,_y,_random,scaler=None,_isSuffle=True,_train={"X":[],"y":[]},_test={"X":[],"y":[]}):
        super(holdOutTest,self).__init__()
        self.setRandom(_random)
        self.columns = self.getColumnsName(_y,_X)
        datas = train_test_split(np.array(_X), np.array(_y), test_size=0.2,shuffle=_isSuffle,random_state = _random)
        self.Datas = {}
        self.Datas["X_train"] = datas[0]
        self.Datas["X_test"]  = datas[1]
        self.Datas["y_train"] = datas[2]
        self.Datas["y_test"]  = datas[3]

        X_train = toArray(_train["X"])
        X_test  = toArray(_test["X"])
        y_train = toArray(_train["y"])
        y_test  = toArray(_test["y"])
        if X_train is not None:
            self.Datas["X_train"] = np.concatenate((self.Datas["X_train"],X_train))
        if y_train is not None:
            self.Datas["y_train"] = np.concatenate((self.Datas["y_train"],y_train))
        if X_test  is not None:
            self.Datas["X_test"]  = np.concatenate((self.Datas["X_test"],X_test))
        if y_test  is not None:
            self.Datas["y_test"]  = np.concatenate((self.Datas["y_test"],y_test))
        
        if scaler == None:
            self.Datas["X_train"],self.Datas["X_test"] = self.scaling(self.Datas["X_train"],self.Datas["X_test"])
        else:
            self.Datas["X_train"],self.Datas["X_test"] = scaler.do(self.Datas["X_train"],self.Datas["X_test"])
        
    def do(self,_model,modelKick):
        return modelKick(_model,**self.Datas)

class kFoldTest(test):
    def __init__(self,_X,_y,_split,_random,scaler=None,_isSuffle=True,_train={"X":[],"y":[]},_test={"X":[],"y":[]}):
        super(kFoldTest,self).__init__()
        self.setRandom(_random)
        self.setSplit(_split)
        self.columns     = self.getColumnsName(_y,_X)

        self.split       = _split
        splitter         = KFold(n_splits=_split, shuffle=_isSuffle, random_state=_random)
        self.split_idx   = []
        
        self.Datas_K     = []

        self.y_train_all = None
        self.y_test_all  = None
        
        X       = toArray(_X)
        X_train = toArray(_train["X"])
        X_test  = toArray(_test["X"])
        y       = toArray(_y)
        y_train = toArray(_train["y"])
        y_test  = toArray(_test["y"])
        
        First = True
        for train_idx, test_idx in splitter.split(X,y):

            self.split_idx.append(train_idx)

            X_train_k, y_train_k = X[train_idx], y[train_idx] #学習用データ
            X_test_k, y_test_k   = X[test_idx] , y[test_idx]  #テスト用データ
            
            # 固定データ
            if X_train is not None:
                X_train_k = np.concatenate((X_train_k,X_train))
            if y_train is not None:
                y_train_k = np.concatenate((y_train_k,y_train))
            if X_test is not None:
                X_test_k  = np.concatenate((X_test_k,X_test))
            if y_test is not None:
                y_test_k  = np.concatenate((y_test_k,y_test))

            # 予測結果評価グラフ用データ
            if self.y_train_all is not None:
                self.y_train_all = np.concatenate((self.y_train_all,y_train_k),axis=0)
                self.y_test_all  = np.concatenate((self.y_test_all ,y_test_k),axis=0)
            else:
                self.y_train_all = y_train_k
                self.y_test_all  = y_test_k

            if scaler == None:
                X_train_k,X_test_k = self.scaling(X_train_k,X_test_k)
            else:
                X_train_k,X_test_k = scaler.do(X_train_k,X_test_k)

            for i in range(_split):
                self.Datas_K.append({
                        "X_train":X_train_k,
                        "y_train":y_train_k,
                        "X_test" :X_test_k,
                        "y_test" :y_test_k 
                      })

        self.y_train_all_size = len(self.y_train_all)
        self.y_test_all_size  = len(self.y_test_all)
        
    def getIONameOrder(self):
        return self.getIONameOrderImple(self.Datas_K[0])
        
    def getInputShape(self):
        return self.getInputShapeImple(self.Datas_K[0])
    
    def getInputType(self):
        return self.getInputTypeImple(self.Datas_K[0])
    
    def getOutputShape(self):
        return self.getOutputShapeImple(self.Datas_K[0])

    def getOutputLabelType(self):
        return self.getOutputLabelTypeImple(self.Datas_K[0])
    
    def getViewSet(self):
        ret = []
        for i in range(self.split):
            y_test = self.Datas_K[i]["y_test"]
            X_test = self.Datas_K[i]["X_test"]
            ret_df = pd.DataFrame(y_test,columns=self.columns["y"])
            ret_df[self.columns["X"]] = pd.DataFrame(X_test)
            ret.append(ret_df)
        return ret
                               
    def do(self,_model,modelKick):
        loss_test_sum  = 0
        loss_train_sum = 0
        y_pred_train = np.ones_like(self.y_train_all)
        y_pred_test  = np.ones_like(self.y_test_all)
        countTrain = 0
        countTest  = 0
        countTrain_Last = 0
        countTest_Last  = 0
        for i in range(self.split):
            testResult = modelKick(_model,**self.Datas_K[i])
            loss_test_sum  += testResult["loss_test"]
            loss_train_sum += testResult["loss_train"]
            countTrain = len(testResult["y_pred_train"])
            countTest  = len(testResult["y_pred_test"])
            y_pred_train[countTrain_Last:(countTrain_Last+countTrain)] = testResult["y_pred_train"]
            y_pred_test[countTest_Last:(countTest_Last+countTest)]     = testResult["y_pred_test"]
            countTrain_Last += countTrain
            countTest_Last  += countTest
        
        loss_test  = loss_test_sum / self.split
        loss_train = loss_train_sum / self.split

        return {"loss_train":loss_train,"loss_test":loss_test,
                 "y_train":self.y_train_all,"y_test":self.y_test_all,
                 "y_pred_train":y_pred_train,"y_pred_test":y_pred_test}

    def appendColumns(self,_columns):
        cnt = 0
        for key in _columns:
            if key not in self.columns["X"]:
                cnt += 1
                self.columns["X"].append(key)
        if cnt > 0:
            for i in range(self.split):
                trainSize = self.Datas_K[i]["X_train"].shape[0]
                self.Datas_K[i]["X_train"] = np.concatenate((self.Datas_K[i]["X_train"],
                                                             np.zeros(trainSize * cnt).reshape(trainSize,cnt)),axis=1)
                testSize  = self.Datas_K[i]["X_test"].shape[0]
                self.Datas_K[i]["X_test"]  = np.concatenate((self.Datas_K[i]["X_test"] ,
                                                             np.zeros(testSize  * cnt).reshape(testSize ,cnt)),axis=1)

    def updateColumns(self,_columns,_trainValues,_testValues):
        index = getColIndex(None,_columns,self.columns["X"])
        countTrain = 0
        countTest  = 0
        countTrain_Last = 0
        countTest_Last  = 0
        for i in range(self.split):
            countTrain = self.Datas_K[i]["X_train"].shape[0]
            countTest  = self.Datas_K[i]["X_test"].shape[0]
            self.Datas_K[i]["X_train"][:,index] = _trainValues[countTrain_Last:(countTrain_Last+countTrain)].reshape(-1,len(_columns))
            self.Datas_K[i]["X_test"][:,index]  = _testValues[countTest_Last:(countTest_Last+countTest)].reshape(-1,len(_columns))
            countTrain_Last += countTrain
            countTest_Last  += countTest

    def resetColumns(self,_columns):
        index = getColIndex(None,_columns,self.columns["X"])
        for i in range(self.split):
            self.Datas_K[i]["X_train"][:,index] = 0
            self.Datas_K[i]["X_test"][:,index]  = 0
        
class testOrder(test):
    def __init__(self,_X_train,_y_train,_X_test,_y_test,_random,scaler=None):
        super(testOrder,self).__init__()
        self.setRandom(_random)
        self.columns = self.getColumnsName(_y_train,_X_train)
        self.Datas = {}
        self.Datas["X_train"] = toArray(_X_train)
        self.Datas["X_test"]  = toArray(_X_test)
        self.Datas["y_train"] = toArray(_y_train)
        self.Datas["y_test"]  = toArray(_y_test)

        if scaler == None:
            self.Datas["X_train"],self.Datas["X_test"] = self.scaling(self.Datas["X_train"],self.Datas["X_test"])
        else:
            self.Datas["X_train"],self.Datas["X_test"] = scaler.do(self.Datas["X_train"],self.Datas["X_test"])
            
    def addData(self,_name,_train,_test):
        self.Datas["{}_train".format(_name)] = _train
        self.Datas["{}_test".format(_name)]  = _test
        
    def expandData(self,_name,_function_train,_function_test = None):
        if _function_train is None:
            print("function_train is not Defined")
            return
        if not isFunction(_function_train):
            print("argment type error need function_train call")
            return
        if not isKeyArgsFunction(_function_train):
            print("argment detail error need keyargs function_train")
            return
        
        if _function_test is None:
            function_test = _function_train
        else:
            function_test = _function_test
            if not isFunction(_function_test):
                print("argment type error need function_test call")
                return
            if not isKeyArgsFunction(_function_test):
                print("argment detail error need keyargs function_t")
                return
        
        self.Datas["{}_train".format(_name)] = _function_train(**self.Datas)
        self.Datas["{}_test".format(_name)]  = function_test(**self.Datas)

    def do(self,_model,modelKick):
        return modelKick(_model,**self.Datas)
            
# TODO：Generatorの出力データの数を１：Nにするか１：１にするかでクラスを拡張する
# ＨＤＤからデータを取り込むクラスを実装する、データの取り込み先を定義する
class testOnHDD(testOrder):
    
    # TODO
    # include set を取り込み
    # 初期配置データとして2件読み込む
    # 別途、拡張セットとしてexpandDataと同等の実装を行う
    def __init__(self,
                 _inclist_X_train  = [],
                 _inclist_y_train  = [],
                 _inclist_X_test   = [],
                 _inclist_y_test   = [],
                 _incfunc_X_train  = None,
                 _incfunc_y_train  = None,
                 _incfunc_X_test   = None,
                 _incfunc_y_test   = None,
                 _Xonly            = False, # XのFunctionから複数データ展開する場合に使用
                 _batch_size_train = 3,
                 _batch_size_test  = None,
                 _trainShuffle     = False,
                 _testShuffle      = True,
                 _breakCount       = -1,
                 _callGC           = True,
                 _random           = 1234,
                 _useGenerator     = True
                ):
        super(testOnHDD,self).__init__()

        self.callGC = _callGC
        self.useGenerator = _useGenerator
        
        # データ管理リスト
        # データ生成関数リストとデータ源泉マップのリレーション情報
        # ステップ件数
        # 総件数（データ管理リストが源泉）
            
        self.train_size = len(_inclist_X_train)
        if self.train_size <= 0:
            print("data not found:X_train")
            return
        elif not _Xonly and self.train_size != len(_inclist_y_train):
            print("data size mismatch:y_train")
            return
        
        self.test_size  = len(_inclist_X_test)
        if self.test_size <= 0:
            print("data not found:X_test")
            return
        elif not _Xonly and self.test_size != len(_inclist_y_test):
            print("data size mismatch:y_test")
            return
        
        self.testShuffle  = _testShuffle
        self.trainShuffle = _trainShuffle
        self.Random       = _random
        
        self.breakCount = _breakCount
        self.size = {"train":self.train_size,"test":self.test_size}
        self.batchSize = {}
        self.batchSize["train"] = _batch_size_train
        if isNone(_batch_size_test):
            self.batchSize["test"] = _batch_size_train
        else:
            self.batchSize["test"] = _batch_size_test
        self.trainCount = math.ceil(self.train_size/self.batchSize["train"])
        self.testCount  = math.ceil(self.test_size /self.batchSize["test"])
        self.readDatas = {
            "train":{"_controller":{"next":0,"stepCount":self.trainCount}},
            "test" :{"_controller":{"next":0,"stepCount":self.testCount }}
        }
        self.expandFunctions = {"train":{},"test":{}}

        self.Datas = {}
        
        self.addReadDatas("X",_inclist_X_train,_inclist_X_test,_incfunc_X_train,_incfunc_X_test)
        if not _Xonly:
            self.addReadDatas("y",_inclist_y_train,_inclist_y_test,_incfunc_y_train,_incfunc_y_test)
        
        uncompletes = ""
        for checkname in ["X_train","X_test","y_train","y_test"]:
            if self.Datas.get(checkname) is None:
                uncompletes = uncompletes + " " + checkname + " "
                
        if uncompletes != "":
            print("read function error, data uncompleted ,need item below [{}]".format(uncompletes))
            return

        self.columns = self.getColumnsName(self.Datas["y_train"],self.Datas["X_train"])
        
    def addData(self,_name = None,_train = None,_test = None):
        print("please call addReadDatas")
        
    def addReadDatas(self,_name,_inclist_train,_inclist_test,_function_train,_function_test = None):
        if _inclist_train is not None:
            if len(_inclist_train) < self.train_size:
                print("include list train is short")
                return
                
        if _inclist_test  is not None:
            if len(_inclist_test ) < self.test_size:
                print("include list test is short")
                return
            
        function_train = _function_train
        if function_train is None:
            print("function_train is not Defined")
            return
        if not isFunction(function_train):
            print("argment type error need function_train call")
            return
        if not hasArgFunction(function_train):
            print("argment error need has arg function_train")
            return

        if _function_test is None:
            function_test = _function_train
        else:
            function_test = _function_test
            if not isFunction(function_test):
                print("argment type error need function_test call")
                return
            if not hasArgFunction(function_test):
                print("argment error need has arg function_test")
                return

        # リスト型は整数値リストによる一括索引抽出ができないため、直接並び替える
        if self.trainShuffle:
            np.random.seed(self.Random)
            np.random.shuffle(_inclist_train)
        if self.testShuffle:
            np.random.seed(self.Random)
            np.random.shuffle(_inclist_test)
            
        setFunc = {"train":function_train,"test":function_test}
        setDict = {"train":_inclist_train,"test":_inclist_test}
        
        for topKey in self.readDatas:
            self.readDatas[topKey][_name] = {"function":setFunc[topKey],"list":setDict[topKey]}
        self.loadNext("train",_name,_preload=True)
        self.loadNext("test" ,_name,_preload=True)
        
    def expandData(self,_name = None,_function = None):
        print("call addExpandFunctions")
        self.addExpandFunctions(_name,_function)
        
    def addExpandFunctions(self,_name,_function_train,_function_test = None):
        function_train = _function_train
        if function_train is None:
            print("function_train is not Defined")
            return
        if not isFunction(function_train):
            print("argment type error need function_train call")
            return
        if not isKeyArgsFunction(function_train):
            print("argment detail error need keyargs function_train")
            return

        if _function_test is None:
            function_test = _function_train
        else:
            function_test = _function_test
            if not isFunction(function_test):
                print("argment type error need function_test call")
                return
            if not isKeyArgsFunction(function_test):
                print("argment detail error need keyargs function_test")
                return
        
        funcs = {"train":function_train,"test":function_test}
        for topKey in self.expandFunctions.keys():
            self.expandFunctions[topKey][_name] = funcs[topKey]
        self.expandNext("train",_name)
        self.expandNext("test" ,_name)
            
    # 外部指定されたデータを読み込み
    # 読み込まれたデータから追加拡張データを作成
    # 次のデータが存在する場合はTrue
    def getNext(self,_topKey = "train",_dataName = None,_preload = False):
        ret = self.loadNext(_topKey,_dataName,_preload)
        self.expandNext(_topKey,_dataName)
        return ret

    # 外部指定されたデータを読み込み
    # 次のデータが存在する場合はTrue
    def loadNext(self,_topKey = "train",_dataName = None,_preload = False):
        if _topKey not in self.readDatas.keys():
            print("argments error topKey mismatch")
            return

        topKey      = _topKey
        readDatas   = self.readDatas[topKey]
        controlData = readDatas["_controller"]
        nextBatch   = controlData["next"]
        stepCount   = controlData["stepCount"]
        batchSize   = self.batchSize[topKey]
        if not _preload:
            controlData["next"] = ( nextBatch + 1 ) % stepCount
            
        under =       nextBatch       * batchSize
        over  = min(( nextBatch + 1 ) * batchSize , self.size[topKey] )

        for key in readDatas:
            if _dataName is not None and \
               key != _dataName or \
               key == "_controller":
                continue
            readData = readDatas[key]
            
            if readData["list"] is not None:
                setList = readData["list"][under:over]
            else:
                setList = None
                
            loadDatas = readData["function"](setList)
            if not isDict(loadDatas):
                self.Datas["{}_{}".format(key,topKey)] = loadDatas
            else:
                for loadkey in loadDatas.keys():
                    self.Datas["{}_{}".format(loadkey,topKey)] = loadDatas[loadkey]
            
        # データの末尾を知らせる
        return controlData["next"] != 0

    # 既存データを元に拡張する
    def expandNext(self,_topKey = "train",_dataName = None):
        if _topKey not in self.expandFunctions.keys():
            print("argments error topKey mismatch")
            return
        
        topKey          = _topKey
        expandFunctions = self.expandFunctions[_topKey]
        
        setDict = {}
        for key in self.Datas.keys():
            if re.search("_{}$".format(topKey),key) is not None:
                setKey          = re.sub("_{}$".format(topKey),"",key)
                setDict[setKey] = self.Datas[key]
        # 対応するデータがない場合は処理しない
        if len(setDict) == 0:
            return
            
        for key in expandFunctions:
            if _dataName is not None and \
               key != _dataName:
                continue

            expandFunction = expandFunctions[key]
            expandDatas    = expandFunction(**setDict)
            
            if not isDict(expandDatas):
                self.Datas["{}_{}".format(key,topKey)] = expandDatas
            else:
                for expandkey in retDatas.key():
                    self.Datas["{}_{}".format(expandkey,topKey)] = expandDatas[expandkey]
                
#     # batchSize をCurryで取るか非常に悩む
#     def makeGenerator(self,_inputNames,_outputNames,_suffix,_preload,_batchSize):
#         yieldWork = {}
#         self.getNext(_suffix,_preload = _preload)
#         X = fetchNNDatas(self.Datas,_inputNames ,"_{}".format(_suffix))
#         y = fetchNNDatas(self.Datas,_outputNames,"_{}".format(_suffix))
#         if _preload:
#             while True:
#                 yield X,y
#         else:
#             tmpDict = {"X":X,"y":y}
#             for key,value in tmpDict.items():
#                 workName = "retBase_{}".format(key)
#                 if isList(value):
#                     yieldWork[workName] = []
#                     for i in range(len(value)):
#                         yieldWork[workName].append(np.empty((_batchSize,)+value[i].shape[1:],dtype = value[i].dtype))
#                 else:
#                     yieldWork[workName] = np.empty((_batchSize,)+value.shape[1:],dtype = value.dtype)

#             usedCount = 0
            
#             while True:
#                 outCount = 0
#                 # 出力長NHWCを調べて、NのサイズをbatchSizeに強制する
#                 # X,yについて出力データの種類を確認し
#                 # それぞれについて割り当て領域を設定する
#                 while True:
#                     # Xの既存データサイズをチェック
#                     if isList(X):
#                         readedDataSize = X[0].shape[0]
#                     else:
#                         readedDataSize = X.shape[0]
                        
#                     # 使用済のデータ件数をチェックし、余剰データがある場合割り当て
#                     lowIndex  = 0
#                     highIndex = 0
#                     if usedCount < readedDataSize:
#                         lowIndex  = outCount
#                         highIndex = readedDataSize - usedCount + outCount
#                         if highIndex > _batchSize:
#                             highIndex = _batchSize
#                         # 出力データ件数更新
#                         outCount = highIndex
#                         # 使用済みデータ件数更新
#                         lowReadIndex  = usedCount
#                         highReadIndex = lowReadIndex + highIndex - lowIndex
#                         usedCount     = highReadIndex
#                         # 読み込みデータを出力領域へ割り当て
#                         for key,value in tmpDict.items():
#                             workName = "retBase_{}".format(key)
#                             if isList(value):
#                                 for i in range(len(value)):
#                                     yieldWork[workName][i][lowIndex:highIndex] = value[i][lowReadIndex:highReadIndex]
#                             else:
#                                 yieldWork[workName][lowIndex:highIndex] = value[lowReadIndex:highReadIndex]
#                     # 出力データの件数が不足している場合
#                     if outCount < _batchSize:
#                         if readedDataSize != usedCount:
#                             print("program logic error [ readedDataSize != usedCount AND outCount < _batchSize ]")
#                             break
#                         # 追加データの読み込みを実施
#                         usedCount = 0
#                         self.getNext(_suffix,_preload = _preload)
#                         X = fetchNNDatas(self.Datas,_inputNames ,"_{}".format(_suffix))
#                         y = fetchNNDatas(self.Datas,_outputNames,"_{}".format(_suffix))
#                         tmpDict = {"X":X,"y":y}
                    
#                     # データ件数充足時
#                     elif outCount == _batchSize:
#                         break
#                     else:
#                         print("program logic error")
#                         break

#                 yield yieldWork["retBase_X"],yieldWork["retBase_y"]

    def do(self,_model,modelKick):
        return self.doSelfGenerate(_model,modelKick)
#         if modelKickGenerator is None or not self.useGenerator:
#             return self.doSelfGenerate(_model,modelKick)
#         else:
#             self.getNext("test",_preload = True)
#             inputNames     = _model.input_names
#             outputNames    = _model.output_names
#             trainGenerator = self.makeGenerator(inputNames,outputNames,"train",False,_batchSize)
# #             testGenerator  = self.makeGenerator(inputNames,outputNames,"test" ,True)
# #             return modelKickGenerator(_model,trainGenerator,self.breakCount,testGenerator,1,**self.Datas)
#             return modelKickGenerator(_model,trainGenerator,self.breakCount,None,None,**self.Datas)
    
    def doSelfGenerate(self,_model,modelKick):
        
        # TODO
        # 全データあるいはランダムに選択したBatchを処理する
        # 訓練の分割数が多くなるため学習率や取得データはここで再設定する
        
        # テストデータの更新はどうするか？
        # 既存のキックでは訓練とテストを同時実行する構成としていたため扱いに際はなかった
        # テストデータはランダムサンプリングにするか？
        # 訓練とテストの両方をランダムサンプリングにすることも検討したい        
        # →　インスタンス生成時にTestの索引をShuffleすることとする
        self.getNext("test",_preload = True)

        ret = {}
        
        def setLosses(_losses1):
            return _losses1

        def updateLosses(_losses1,_losses2):
            return _losses1 + _losses2

        def averageLosses(_losses,_count):
            return _losses / _count

        # trainの呼び出し回数はbreakCountかtrainCountによって設定
        if self.breakCount >= 1 and self.breakCount < self.trainCount:
            callCount = self.breakCount
        else:
            callCount = self.trainCount
            
        count = countobj(callCount)
        
#         while hasNext:
        for i in range(callCount):
            if self.trainCount >= 2:
                if self.callGC:
                    keys = list(self.Datas.keys())
                    for key in keys:
                        if re.search("_train$",key) is not None:
                            del(self.Datas[key])
                    gc.collect()
                hasNext     = self.getNext("train")
            trainDatas = {}
            for key in self.Datas:
                if re.search("_train$",key) is not None:
                    trainDatas[key] = self.Datas[key]
            trainResult = modelKick(_model,**trainDatas)
            if i != 0:
                del(trainResult["history"])
                ret["loss_train"] = updateLosses(ret["loss_train"],trainResult["loss_train"])
            else:
                ret.update(trainResult)
                ret["loss_train"] = setLosses(ret["loss_train"])

            count.call()
            
        del(count)
        ret["loss_train"] = averageLosses(ret["loss_train"],callCount)

        testDatas = {}
        for key in self.Datas:
            if re.search("_test$",key) is not None:
                testDatas[key] = self.Datas[key]
        testResult = modelKick(_model,**testDatas)
        ret.update(testResult)
        ret["loss_test"] = setLosses(ret["loss_test"])
        return ret

class testSequence(test):
    def __init__(self,
                 _inclist_X_train:list = None,
                 _inclist_y_train:list = None,
                 _inclist_X_test:list  = None,
                 _inclist_y_test:list  = None,
                 _mapfunc_train        = None,
                 _mapfunc_test         = None,
                 _name_order           = ("X","y"),
                 _eval_size            = -1,
                 _random               = 1234
                ):
        super(testSequence,self).__init__()
        
        self.setRandom(_random)
        self.Datas = {}
        
        def makeDataset(_inclist_X,_inclist_y,_map_func):
            if _inclist_y is not None:
                setItem = (_inclist_X,_inclist_y)
            else:
                setItem = _inclist_X
            retdataset = tf.data.Dataset.from_tensor_slices(setItem)
            if _map_func is not None:
                retdataset = retdataset.map(_map_func)
            return retdataset
        
        def expandSamples(_dataset,_eval_size,_suffix:str = ""):
            ret     = {}
            dataset = _dataset.batch(_eval_size)
            npit    = dataset.as_numpy_iterator()
            npit    = npit.next()
            if npit is not None:
                if isTupleOrList(npit):
                    for i in range(len(_name_order)):
                        if isTupleOrList(_name_order[i]):
                            for key,value in zip(_name_order[i],npit[i]):
                                ret["{}_{}".format(key,_suffix)] = value
                        else:
                            ret["{}_{}".format(_name_order[i],_suffix)] = npit[i]
                            
                else:
                    ret["X_{}".format(_suffix)] = npit
                    ret["y_{}".format(_suffix)] = None
                    
                for key,value in ret.items():
                    if len(value.shape) == 1:
                        if np.unique(np.isnan(value)).sum() == 1:
                            ret[key] = None
                    
            return ret
        
        self.Datas["dataset_train"] = makeDataset(_inclist_X_train,_inclist_y_train,_mapfunc_train).repeat(1)
        self.Datas["dataset_test"]  = makeDataset(_inclist_X_test ,_inclist_y_test ,_mapfunc_test).repeat(1)
        
        if _eval_size == -1:
            train_eval_size = len(_inclist_X_train)
            test_eval_size  = len(_inclist_X_test)
        else:
            train_eval_size = _eval_size
            test_eval_size  = _eval_size
        
        self.Datas.update(expandSamples(self.Datas["dataset_train"],train_eval_size,"train"))
        self.Datas.update(expandSamples(self.Datas["dataset_test"] ,test_eval_size ,"test" ))

        self.columns = self.getColumnsName(self.Datas["y_train"],self.Datas["X_train"])
        
    def do(self,_model,modelKick):
        return modelKick(_model,**self.Datas)

def makeCNNImageTest(_baseClass):
    class CNNImageTestImple(_baseClass):

        def getColumnsName(self,_y,_X):
            if type(_y) == pd.Series:
                ycolumns = [_y.name]
            elif type(_y) == pd.DataFrame:
                ycolumns = list(_y.columns)
            elif _y is not None:
                ycolumns = list(range(_y.shape[len(_y.shape)-1]))
            else:
                ycolumns = []
            self.columns = {"y":ycolumns,"X":[]}
            return self.columns

        def scaling(self,_X_train,_X_test):
            ret = []
            _X_train = _X_train.astype("float32")
            _X_train = _X_train / 255.0
            if _X_test is not None:
                _X_test  = _X_test.astype("float32")
                _X_test  = _X_test  / 255.0
            ret.append(_X_train)
            ret.append(_X_test)
            return ret
        
        def getViewSet(self):
            ret = pd.DataFrame()
            return ret

        def plot(self):
            # 標準化
            viewSet = self.getViewSet()
            # 未実装
            # plt.show()
            
        def appendColumns(self,_columns):
            return
        def updateColumns(self,_columns,_trainValues,_testValues):
            return
        def resetColumns(self,_columns):
            return
        
    return CNNImageTestImple

CNNKFoldTest    = makeCNNImageTest(kFoldTest)
CNNHoldOutTest  = makeCNNImageTest(holdOutTest)
CNNTestOrder    = makeCNNImageTest(testOrder)
CNNTestOnHDD    = makeCNNImageTest(testOnHDD)
CNNTestSequence = makeCNNImageTest(testSequence)



def makeCNNim2im(_baseClass):
    class CNNim2imImple(_baseClass):
        def getColumnsName(self,_y,_X):
            self.columns = {"y":[],"X":[]}
            return self.columns
    return CNNim2imImple

CNNTestOrderim2im    = makeCNNim2im(CNNTestOrder)
CNNTestOnHDDim2im    = makeCNNim2im(CNNTestOnHDD)
CNNTestSequenceim2im = makeCNNim2im(testSequence)

# def makeIICImageTest(_baseClass,_cropScale = 7/8,_segmentation = False):
#     baseCNNImageTest = makeCNNImageTest(_baseClass)
#     class IICImageTestImple(baseCNNImageTest):
        
#         def concatEvenBatch(x,x2,_isBuiltIn = False):
#             shapes  = tf.shape(x ).numpy().tolist()
#             shapes2 = tf.shape(x2).numpy().tolist()
#             if shapes != shapes2:
#                 return x
            
#             x  = tf.expand_dims(x ,1)
#             x2 = tf.expand_dims(x2,1)
#             x  = tf.concat([x,x2],1)
            
#             if not _isBuiltIn:
#                 x = tf.reshape(x,[-1,1]+shapes[1:])
#             else:
#                 x = MyReshapeLayer([1]+shapes[1:])
#             x = tf.squeeze(x,1)
#             return x
        
#         def iicExtiontion(x):
#             shapes = tf.shape(x)
#             if len(shapes) != 4:
#                 return x
#             N,C      = shapes[0],shapes[-1]
#             HW       = shapes[1:-1]
            
#             if not _segmentation:
#                 cropHW   = tf.cast(tf.cast(HW,tf.float32) * _cropScale,shapes.dtype)
#                 cropsize = [N,cropHW[0],cropHW[1],C]
#                 padtoHW  = HW
#                 xp = tf.image.random_crop(x, cropsize)
#                 xp = tf.image.resize_image_with_pad(xp, *padtoHW)
#             else:
#                 cropsize = shapes
#                 xp = x
            
#             noise = tf.random.normal(mean=1., stddev=0.1, shape=tuple(cropsize[1:]))
#             xp = tf.clip_by_value(xp * noise, 0, 1)

#             if not _segmentation:
#                 xp = tf.image.random_flip_left_right(xp)
#                 # xp = tf.image.random_flip_up_down(xp)

#                 # Rotation
#                 # nrot = tf.round(tf.random.uniform(shape=(1,), minval=0, maxval=4))
#                 # xp = tf.image.rot90(xp, k=tf.squeeze(tf.cast(nrot, tf.int32)))

#             xp = tf.image.random_brightness(xp, 0.1)
#             xp = tf.image.random_hue(xp, 0.1)

#             return xp
        
# #         def initExtention(self):
# #             for key in self.Datas:
# #                 if re.match("X|input",key) is not None:
# #                     x  = self.Datas[key]
# #                     x2 = iicExtention(x)
# #                     x  = concatEvenBatch(x,x2,False)
# #                     self.Datas[key] = x
                    
#         # BuildInExtentionをmakeModel中に差し込む
#         def builtInExtention(x):
#             x2 = iicExtention(x)
#             x  = concatEvenBatch(x,x2,True)
#             return x
                    
#         # ジェネレータ系にどのように干渉するか検討が必要
#         # バッチへ送るときに処理する？
#         # 　リアルタイムにノイズが付加されるので施行ごとに違うデータで検証出来て良い
#         # 　二週目以降ノイズパターンが異なるので汎化性能向上が期待できる
#         # 　ノイズパターンを切り替えて処理しやすそう
#         # 　データフロー上に配置して埋め込むことが出来そう
#         # 　こちらの場合、どこで干渉する？
#         # 生成時点で処理する？
#         # 　高速
#         # 　仕込み易いため既存のフレームワークに乗せることができる
#         # 　偶数奇数でデータを分ければ偶数batchで処理することで通常のFitでロスを処理できる
#         # 　こちらの場合、Init上で干渉する
#     return IICImageTestImple


def scaleOne(_X = None):
    if _X is None:
        return None
    X_recip = np.array(_X)
    averageValue = 1 / np.average(_X,axis=(1,2))
    for i in range(len(averageValue)):
        X_recip[i] = _X[i] * averageValue[i]
    return X_recip
