# 損失
from sklearn.metrics       import mean_squared_error
# 各モデル
from sklearn.linear_model  import Lasso   as L1,  Ridge   as L2,  ElasticNet   as EN,  LinearRegression   as Line
from sklearn.linear_model  import LassoCV as L1CV,RidgeCV as L2CV,ElasticNetCV as ENCV
from sklearn.ensemble      import RandomForestRegressor
from sklearn.tree          import DecisionTreeRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline      import Pipeline
from MyModelTest           import modelTest,modelTestNorand,modelTestNN,modelTestStack
from MyNeuralNetwokTF      import makeNNModel as makeNNModelDefault

from Util import isTupleOrList

def makeRegTest(_testObject,_loss,_useAdaBoost = False):
    if isTupleOrList(_testObject):
        def testObject():
            ret = []
            for obj in testObject:
                ret.append(obj())
            return ret
    else:
        testObject = _testObject
    if not _useAdaboost:
        def regTestImple(_test,_hyperParam,_label = ""):
            return modelTest(_test,testObject(),_loss,**_hyperParam).do(_label)
    else:
        def regTestImple(_test,_hyperParam,_label = ""):
            return modelTest(_test,testObject(),_loss,**_hyperParam).doAdaBoostReg(_label)
    return regTestImple

# 線形回帰
linearRegTest     = makeRegTest(Line,mean_squared_error)
LineRegTest       = makeRegTest(Line,mean_squared_error)
LassoRegTest      = makeRegTest(L1,mean_squared_error)
RidgeRegTest      = makeRegTest(L2,mean_squared_error)
ElasticNetRegTest = makeRegTest(EN,mean_squared_error)
DTRegTest         = makeRegTest(DecisionTreeRegressor,mean_squared_error)
RFRegTest         = makeRegTest(RandomForestRegressor,mean_squared_error)

PolynominalLineRegTest = makeRegTest([PolynomialFeatures,Line],mean_squared_error)
PolynominalL1RegTest   = makeRegTest([PolynomialFeatures,L1],mean_squared_error)
PolynominalL2RegTest   = makeRegTest([PolynomialFeatures,L2],mean_squared_error)
PolynominalENRegTest   = makeRegTest([PolynomialFeatures,EN],mean_squared_error)
PolynominalDTRegTest   = makeRegTest([PolynomialFeatures,DecisionTreeRegressor],mean_squared_error)
PolynominalRFRegTest   = makeRegTest([PolynomialFeatures,RandomForestRegressor],mean_squared_error)

AdaPolynominalLineRegTest = makeRegTest([PolynomialFeatures,Line],mean_squared_error)
AdaPolynominalL1RegTest   = makeRegTest([PolynomialFeatures,L1],mean_squared_error)
AdaPolynominalL2RegTest   = makeRegTest([PolynomialFeatures,L2],mean_squared_error)
AdaPolynominalENRegTest   = makeRegTest([PolynomialFeatures,EN],mean_squared_error)
AdaPolynominalDTRegTest   = makeRegTest([PolynomialFeatures,DecisionTreeRegressor],mean_squared_error)
AdaPolynominalRFRegTest   = makeRegTest([PolynomialFeatures,RandomForestRegressor],mean_squared_error)
AdaL1RegTest              = makeRegTest(L1,mean_squared_error)
AdaL2RegTest              = makeRegTest(L2,mean_squared_error)
AdaENRegTest              = makeRegTest(EN,mean_squared_error)
AdaDTRegTest              = makeRegTest(DecisionTreeRegressor,mean_squared_error)
AdaRFRegTest              = makeRegTest(RandomForestRegressor,mean_squared_error)

def NNRegTest(_test,_model = makeNNModelDefault,_label = "",_lossFunction = mean_squared_error,**_hyperParam):
    param = copy.copy(_hyperParam)
    param["IONameOrder"]     = _test.getIONameOrder()
    param["inputShape"]      = _test.getInputShape()
    param["inputType"]       = _test.getInputType()
    param["outputShape"]     = _test.getOutputShape()
    param["outputLabelType"] = _test.getOutputLabelType()
    
    # モデルはモデルのテスト生成時にコンパイルする
    # モデル自体と学習結果を、それぞれ戻り値として取る
    return modelTestNN(_test,_model,_lossFunction,**param).do(param,_label)

def makeStackTest(*testFuncs:list):
    def stackTestImple(_test,**_hyperParam):
        return modelTestStack(_test,testFuncs).do(**_hyperParam)
    return stackTestImple

stackL1RFRegTest      = makeStackTest(LassoRegTest,RFRegTest)
stackL1DTRegTest      = makeStackTest(LassoRegTest,DTRegTest)
stackDTL1RegTest      = makeStackTest(DTRegTest,LassoRegTest)
stackAdaDTL1RegTest   = makeStackTest(AdaDTRegTest,AdaL1RegTest)
stackENRFRegTest      = makeStackTest(ElasticNetRegTest,RFRegTest)
stackENDTRegTest      = makeStackTest(ElasticNetRegTest,DTRegTest)
stackL1RFNNRegTest    = makeStackTest(LassoRegTest,RFRegTest,NNRegTest)
stackL1DTNNRegTest    = makeStackTest(LassoRegTest,DTRegTest,NNRegTest)
stackDTL1NNRegTest    = makeStackTest(DTRegTest,LassoRegTest,NNRegTest)
stackAdaDTL1NNRegTest = makeStackTest(AdbDTRegTest,AdbL1RegTest,NNRegTest)
stackENRFNNRegTest    = makeStackTest(ElasticNetRegTest,RFRegTest,NNRegTest)
stackENDTNNRegTest    = makeStackTest(elasticNetRegTest,DTRegTest,NNRegTest)
