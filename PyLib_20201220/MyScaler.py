# 説明変数のスケーリングを個別に行う実装
from sklearn.preprocessing import StandardScaler
import numpy as np
from Util import getColIndex

class scaler:
    def __init__(self):
        ret = {}
    def do(self,_X_train,_X_test):
        return
    def convDecorr(self,_X_train = np.array([[]]),_X_test = np.array([[]])):
        ##  無相関化を行うための一連の処理
        cov = np.cov(_X_train, rowvar=0)        # 分散・共分散を求める
        _, S = np.linalg.eig(cov)               # 分散共分散行列の固有ベクトルを用いて
        decorrTrain = np.dot(S.T, _X_train.T).T #データを無相関化
        decorrTest  = np.dot(S.T, _X_test.T).T  #データを無相関化

        return [decorrTrain,decorrTest]

    def convStd(self,_X_train,_X_test):
        mean = _X_train.mean()
        std  = _X_train.std()
        X_train = ( _X_train - mean ) / std
        X_test  = ( _X_test  - mean ) / std
        return [X_train,X_test]
    def convMinMax(self,_X_train,_X_test):
        min   = _X_train.min()
        scale = _X_train.max() - min
        X_train = ( _X_train - min ) / scale
        X_test  = ( _X_test  - min ) / scale
        return [X_train,X_test]
    
    def bottom2Zero(self,_X_train,_X_test):
        min   = _X_train.min()
        X_train = _X_train - min
        X_test  = _X_test  - min
        return [X_train,X_test]
        

class scaleOnlyLarge(scaler):
    def __init__(self,_large = 1):
        self.large = _large
        
    def do(self,_X_train,_X_test):
        for i in range(_X_train.shape[1]):
            if abs(_X_train[:,i].mean()) + _X_train[:,i].std()  > self.large:
                _X_train[:,i],_X_test[:,i] = self.convStd(_X_train[:,i],_X_test[:,i])

        ret = []
        ret.append(_X_train)
        ret.append(_X_test)
        return ret

class scaleOtherThanDummy(scaler):
    # ダミー変数を処理する事を回避するため、0か1のデータを避けてスケーリング
    def do(self,_X_train,_X_test):
        for i in range(_X_train.shape[1]):
            uniqueKey = np.unique(_X_train[:,i])
            if ((uniqueKey == 0) + (uniqueKey == 1)).min() == False:
                _X_train[:,i],_X_test[:,i] = self.convStd(_X_train[:,i],_X_test[:,i])

        ret = []
        ret.append(_X_train)
        ret.append(_X_test)
        return ret

class scaleOrder(scaler):
    def __init__(self,_stdOrder = None,_mmOrder = [],_bottom2ZeroOrder = [], _decorrOrder = [[]]):
        self.stdOrder         = _stdOrder
        self.mmOrder          = _mmOrder
        self.bottom2ZeroOrder = _bottom2ZeroOrder
        if ( _decorrOrder != None ) & ( len(_decorrOrder) >= 1 ):
            if len(_decorrOrder[0]) >= 2:
                self.decorrOrder = _decorrOrder
            else:
                self.decorrOrder = None
        else:
            self.decorrOrder = None
            
    def do(self,_X_train,_X_test):
        
        if self.decorrOrder != None:
            for od in self.decorrOrder:
                _X_train[:,od],_X_test[:,od] = self.convDecorr(_X_train[:,od],_X_test[:,od])
        
        loopIndexs = []
        if self.stdOrder != None:
            loopIndexs = self.stdOrder
        else:
            loopIndexs = range(_X_train.shape[1])
        
        for i in loopIndexs:
            uniqueKey = np.unique(_X_train[:,i])
            if ((uniqueKey == 0) + (uniqueKey == 1)).min() == False:
                _X_train[:,i],_X_test[:,i] = self.convStd(_X_train[:,i],_X_test[:,i])
                
        if self.mmOrder != None:
            for i in self.mmOrder:
                uniqueKey = np.unique(_X_train[:,i])
                if ((uniqueKey == 0) + (uniqueKey == 1)).min() == False:
                    _X_train[:,i],_X_test[:,i] = self.convMinMax(_X_train[:,i],_X_test[:,i])
        
        if self.bottom2ZeroOrder != None:
            for i in self.bottom2ZeroOrder:
                uniqueKey = np.unique(_X_train[:,i])
                if ((uniqueKey == 0) + (uniqueKey == 1)).min() == False:
                    _X_train[:,i],_X_test[:,i] = self.bottom2Zero(_X_train[:,i],_X_test[:,i])

        return [_X_train,_X_test]
    
class scalerImage(scaler):
    def __init__(self):
        return
    def do(self,_X_train,_X_test):
        _X_train = _X_train / 255.0
        _X_test  = _X_test  / 255.0
        _X_train = _X_train.astype('float64')
        _X_test  = _X_test.astype('float64')
        return [_X_train,_X_test]