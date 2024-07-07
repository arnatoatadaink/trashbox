import matplotlib.pyplot as plt
import pandas as pd
import numpy  as np
import pandas as pd
import time
import math
from IPython.display         import display
import sys
from Count import counter as countobj
from Util import makeParameterLists,npvoid2dict,getConcatFunc
import re

class Tuning:
    def __init__(self):
        self.result = pd.DataFrame()
        #パラメーターのデータセットは辞書型で扱う
        # {"パラメーター名":係数リスト,"パラメーター名":係数リスト}
        # 汎化誤差、訓練誤差、各実行パラメーターを持つリストを生成する
        # 0＝汎化誤差、1＝訓練誤差、2＝処理時間、3～＝パラメーター
        self.scorebase = {"loss_train":0,"loss_test":0,"time":0}
        
    def setscore(self,param:dict,result:dict,time):
        param["loss_train"] = result["loss_train"]
        param["loss_test"]  = result["loss_test"]
        param["time"]       = time
        
    # 複数の係数をグリッドサーチで検索する場合
    # 最適なパラメーターを計算した後にグラフ化して遷移を見たい
    # 最適なパラメーターにおける横の変化率だけ確認する？
    # また末端の変化率が下降傾向で止まっているデータについて探索が完了していないことを警告する？
    def gridSearch(self,_testData,_testFunc,_paramdict:dict):

        start_all = time.time_ns()

        paramdict = {}
        paramdict.update(self.scorebase)
        paramdict.update(_paramdict)
        paramlist = makeParameterLists(paramdict)

        min_loss    = 100000000000
        min_result  = {}
        bestIndex   = -1
        
        cnt   = countobj(len(paramlist))
        index = -1
        for param in paramlist:
            index += 1
            start  = time.time_ns()
            result = _testFunc(_testData,npvoid2dict(param))
            end    = time.time_ns()
            cnt.call()
            
            self.setscore(param,result,( end - start ) * 1e-9)
            loss_test = result["loss_test"]

            if min_loss> loss_test:
                min_result = result
                min_loss   = loss_test
                bestIndex  = index

        df = pd.pandas.DataFrame(paramlist)

        self.result = min_result
        end_all     = time.time_ns()
        self.result.update({"min_loss":min_loss,
                            "bestIndex":bestIndex,
                            "turnAroundTime":pd.Timedelta(end_all - start_all),
                            "numberOfTrial":len(paramlist),
                            "testResult":df})
        return self.result
    
    def testInfo(self,_label=""):
        print("")
        print("{} 全体所要時間 {}".format(_label,self.result["turnAroundTime"]))
        print("{} 試行回数 {:d}".format(_label,self.result["numberOfTrial"]))
    
    def displayBest(self,_label=""):
        bestIndex = self.result["bestIndex"]
        df  = self.result["testResult"]
        display(df.loc[bestIndex:bestIndex])
        print("{}訓練誤差：{:.3f}".format(_label,df.loc[bestIndex]["loss_train"]))
        print("{}汎化誤差：{:.3f}".format(_label,df.loc[bestIndex]["loss_test"]))
        print("{}処理時間：{}".format(_label,pd.Timedelta(df.loc[bestIndex]["time"])))
        
    def showPredGraph(self,_label="",_Train=True):
        
        y        = [self.result["y_test"]]
        y_pred   = [self.result["y_pred_test"]]
        legend   = ["test"]
        c        = ["b"]
        c_pred   = ["orange"]#[0xFF0000]
        pointCnt = len(self.result["y_test"])
        
        if _Train == True:
            y.append(self.result["y_train"])
            y_pred.append(self.result["y_pred_train"])
            legend.append("train")
            c.append("c")
            c_pred.append("red")#(0xEE7800)
            pointCnt += len(self.result["y_train"])
        
        yZip = zip(y,y_pred,legend,c,c_pred)
        
        xlim_min =  10000000000
        ylim_min =  10000000000
        xlim_max = -10000000000
        ylim_max = -10000000000
        
        for y,y_pred,legLabel,c,c_pred in yZip:
            plt.plot((y.min(),y.max()),(y.min(), y.max()),label="{} base".format(legLabel),color=c)
            plt.scatter(y,y_pred,label="{} pred".format(legLabel),c=c_pred,s=10/math.log10(pointCnt))
            
            xlim_min = min(y.min()     ,xlim_min)
            ylim_min = min(y_pred.min(),ylim_min)
            xlim_max = max(y.max()     ,xlim_max)
            ylim_max = max(y_pred.max(),ylim_max)

        plt.xlim(xlim_min-1, xlim_max+1)
        plt.ylim(ylim_min-1, ylim_max+1)
        plt.xlabel("base")
        plt.ylabel("pred")
        plt.legend()
        plt.show()

    def showGraph(self,_label="",showParam=[],_Train=True):
        bestIndex = self.result["bestIndex"]
        df        = self.result["testResult"].copy()
        df        = self.convertForQuery(df)

        values    = df.loc[bestIndex]
        keys      = list(df.columns[len(self.scorebase):])
        entrys    = zip(keys,list(values)[len(self.scorebase):])
        
        wheres    = []
        getGraphs = {}

        if len(showParam) == 0:
            showParam = keys
            
        for key,value in entrys:
            if type(value) == str:
                pattern = " {} == '{}' "
            else:
                pattern = " {} == {} "
            where = pattern.format(key,value)
            wheres.append(where)

        keyIndexs   = zip(keys,range(len(wheres)))
        concatwheres = getConcatFunc(wheres)

        for key,index in keyIndexs:
            
            if key in showParam:
            
                whereKey = concatwhere(wheres[:index],wheres[index+1:])
                whereKey = "&".join(whereKey)

                if whereKey != "":
                    getGraphs[key] = df.query(whereKey)
                else:
                    getGraphs[key] = df

        self.displayBest(_label)
        for key,graphValue in getGraphs.items():
            
            print("Optimized {}：{}".format(key,values[key]))

            xHyperParam = graphValue[[key]]
            xUnique     = xHyperParam[key].unique()
            if len(xUnique) == 1:
                continue
            elif xUnique.dtype == "object":
                xHyperParam = xHyperParam.copy()
                for i,val in zip(range(len(xUnique)),xUnique):
                    print("{} ＝ {}".format(i,val))
                    xHyperParam.loc[xHyperParam[key]==val] = i
                    
            yTrain = graphValue[["loss_train"]]
            yTest  = graphValue[["loss_test"]]

            plt.figure(figsize=(16,4))
            plt.grid(which='major',color='black',linestyle=':')
            plt.xlabel(key)
            plt.ylabel("loss")
            
            plt.plot(xHyperParam,yTest, label="Test")
            if _Train:
                plt.plot(xHyperParam,yTrain,label="Train")

            plt.legend()
            plt.show()

            print("")        

#     def printParam(self,_label="",_lossLabel="二乗",_printCount=3):
#         Xcolumns   = self.result["Xcolumns"]
#         if checkTypeNone(self.result.get("wait")):
#             waitOut    = ""
#             for i in range(len(self.result["wait"])):
#                 waitOut += "　{}の重み：{:.3f}".format(Xcolumns[i],self.result["wait"][i])
#                 if (_printCount-i%_printCount-1) == 0:
#                     print("{}{}".format(_label,waitOut))
#                     waitOut = ""
#             if waitOut != "":
#                 print("{}{}".format(_label,waitOut))
                
#         if checkTypeNone(self.result.get("importances")):
#             importancesOut    = ""
#             for i in range(len(self.result["importances"])):
#                 importancesOut += "　{}の重要度：{:.3f}".format(Xcolumns[i],self.result["importances"][i])
#                 if (_printCount-i%_printCount-1) == 0:
#                     print("{}{}".format(_label,importancesOut))
#                     importancesOut = ""
#             if importancesOut != "":
#                 print("{}{}".format(_label,importancesOut))
                
#         if checkTypeNone(self.result.get("bias")):
#             print("{} バイアス：{:.3f}".format(_label,self.result["bias"]))
#         if checkTypeNone(self.result.get("time")):
#             print("{} テスト所要時間：{}".format(_label,pd.Timedelta(self.result["time"])))
#         if checkTypeNone(self.result.get("loss_train")):
#             print("{} 訓練 {}誤差：{:.3f}".format(_label,_lossLabel,self.result["loss_train"]))
#         if checkTypeNone(self.result.get("loss_test")):
#             print("{} 汎化 {}誤差：{:.3f}".format(_label,_lossLabel,self.result["loss_test"]))
#         if checkTypeNone(self.result.get("alpha")):
#             print("{} 正則化強度：{:.3f}".format(_label,self.result["alpha"]))
#         if checkTypeNone(self.result.get("l1_ratio")):
#             print("{} L1正則化比重：{:.3f}".format(_label,self.result["l1_ratio"]))
#         print("")
        
    def convertForQuery(self,_df):
        for dfname in _df:
            if _df[dfname].dtype == object:
                _df[dfname] = _df[dfname].apply(lambda x : re.sub("'","",str(x)))
        return _df
