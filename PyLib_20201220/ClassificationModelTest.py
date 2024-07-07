# 損失関数にはクロスエントロピーを使用する
from sklearn.metrics       import log_loss
# 各モデル
from sklearn.ensemble      import RandomForestClassifier
from sklearn.tree          import DecisionTreeClassifier
from sklearn.preprocessing import PolynomialFeatures
from MyModelTest           import modelTest,modelTestNorand,modelTestNN,modelTestStack
from MyNeuralNetworkTF     import makeNNModel as makeNNModelDefault
# ,modelTestNNImg,
from Util                  import isTupleOrList

import copy,numpy as np

# log_lossは内部的にロジスティック回帰にもなるため、log_loss一択で良い
# # 2値分類と多項分類の分離
# def checkClassifierLossFunction(_test)
#     if len(_test.columns["y"]) == 1:
#         return sigmoid
#     else:
#         return log_loss

def makeClsTest(_testObject,_loss,_useAdaBoost = False):
    if isTupleOrList(_testObject):
        def testObject():
            ret = []
            for obj in testObject:
                ret.append(obj())
            return ret
    else:
        testObject = _testObject
    if not _useAdaBoost:
        def clsTestImple(_test,_hyperParam,_label = ""):
            return modelTest(_test,testObject(),_loss,**_hyperParam).do(_label)
    else:
        def clsTestImple(_test,_hyperParam,_label = ""):
            return modelTest(_test,testObject(),_loss,**_hyperParam).doAdaBoostCls(_label)
    return clsTestImple

DTClsTest               =  makeClsTest(DecisionTreeClassifier,log_loss)
RFClsTest               =  makeClsTest(RandomForestClassifier,log_loss)
PolynominalDTClsTest    =  makeClsTest([PolynomialFeatures,DecisionTreeClassifier],log_loss)
PolynominalRFClsTest    =  makeClsTest([PolynomialFeatures,RandomForestClassifier],log_loss)
AdaPolynominalDTClsTest =  makeClsTest([PolynomialFeatures,DecisionTreeClassifier],log_loss,True)
AdaPolynominalRFClsTest =  makeClsTest([PolynomialFeatures,RandomForestClassifier],log_loss,True)
AdaDTClsTest            =  makeClsTest(DecisionTreeClassifier,log_loss,True)
AdaRFClsTest            =  makeClsTest(RandomForestClassifier,log_loss,True)

# コンパイルから実行まで同時に実施する処理
# 事前コンパイル済のモデル、訓練済のモデルはHyperParameterを通して継承する
def NNClsTest(_test,_hyperParam,_label = "",_lossFunction = log_loss,_makeNNModel = makeNNModelDefault):
    param = copy.copy(_hyperParam)
    param["IONameOrder"]     = _test.getIONameOrder()
    param["inputShape"]      = _test.getInputShape()
    param["outputShape"]     = _test.getOutputShape()
    param["outputLabelType"] = _test.getOutputLabelType()
    return modelTestNN(_test,_makeNNModel,_lossFunction,**param).do(_label)

# NNモデルを事前コンパイルするための関数、ModelTestのpyにも同一の関数NNMakeが存在する
def getNNClsObj(_test,_hyperParam,_lossFunction = log_loss,_makeNNModel = makeNNModelDefault):
    param = copy.copy(_hyperParam)
    param["IONameOrder"]     = _test.getIONameOrder()
    param["inputShape"]      = _test.getInputShape()
    param["inputType"]       = _test.getInputType()
    param["outputShape"]     = _test.getOutputShape()
    param["outputLabelType"] = _test.getOutputLabelType()
    return modelTestNN(_test,_makeNNModel,_lossFunction,**param)

# NNモデルを事前コンパイルするための関数
def getNNClsModel(_test,_hyperParam,_lossFunction = log_loss,_makeNNModel = makeNNModelDefault):
    return getNNClsObj(_test,_hyperParam,_lossFunction,_makeNNModel).model

def makeStackTest(*testFuncs:list):
    def stackTestImple(_test,**_hyperParam):
        return modelTestStack(_test,testFuncs).do(**_hyperParam)
    return stackTestImple

stackRFNNClsTest    = makeStackTest(RFClsTest,NNClsTest)
stackDTNNClsTest    = makeStackTest(DTClsTest,NNClsTest)
stackAdaDTNNClsTest = makeStackTest(AdaDTClsTest,NNClsTest)
