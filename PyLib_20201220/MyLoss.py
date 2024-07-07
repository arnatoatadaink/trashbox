import tensorflow as tf
import sys

def makeIICLossForLocal(lamb0=1.0,lamb1=1.0, EPS=sys.float_info.epsilon):
    if tf.keras.backend.floatx() == 'float32':
        float_limit  = tf.float32.max
    elif tf.keras.backend.floatx() == 'float64':
        float_limit  = tf.float64.max
    else:
        float_limit  = tf.float16.max
        
    def IICLossForLocalImple(z,z_):
        c  = z.shape[-1]
        z = tf.reshape(z, [-1, c, 1])
        z_ = tf.reshape(z_, [-1, 1, c])
        P = tf.math.reduce_sum(z * z_, axis=0)  # 同時確率
        P = (P + tf.transpose(P)) / 2  # 対称化
        P = tf.clip_by_value(P, EPS, float_limit)  # logが発散しないようにバイアス
        P = P / tf.math.reduce_sum(P)  # 規格化

        # 周辺確率
        Pi = tf.math.reduce_sum(P, axis=0)
        Pi = tf.reshape(Pi, [c, 1])
        Pi = tf.tile(Pi, [1,c])
        Pj = tf.math.reduce_sum(P, axis=1)
        Pj = tf.reshape(Pj, [1, c])
        Pj = tf.tile(Pj, [c,1])

        loss = tf.math.reduce_sum(P * ((tf.math.log(Pi)*lamb1 + tf.math.log(Pj)*lamb1) - tf.math.log(P)*lamb0))
        return tf.math.minimum(loss,-EPS)
    return IICLossForLocalImple

def makeIICLoss(lamb0=1.0,lamb1=1.0, EPS=sys.float_info.epsilon):
    if tf.keras.backend.floatx() == 'float32':
        float_limit  = tf.float32.max
    elif tf.keras.backend.floatx() == 'float64':
        float_limit  = tf.float64.max
    else:
        float_limit  = tf.float16.max
        
    def IICLossImple(x:None,z):
        z_ = z[1::2]
        z  = z[ ::2]
        c  = z.shape[-1]
        z = tf.reshape(z, [-1, c, 1])
        z_ = tf.reshape(z_, [-1, 1, c])
        P = tf.math.reduce_sum(z * z_, axis=0)  # 同時確率
        P = (P + tf.transpose(P)) / 2  # 対称化
        P = tf.clip_by_value(P, EPS, float_limit)  # logが発散しないようにバイアス
        P = P / tf.math.reduce_sum(P)  # 規格化

        # 周辺確率
        Pi = tf.math.reduce_sum(P, axis=0)
        Pi = tf.reshape(Pi, [c, 1])
        Pi = tf.tile(Pi, [1,c])
        Pj = tf.math.reduce_sum(P, axis=1)
        Pj = tf.reshape(Pj, [1, c])
        Pj = tf.tile(Pj, [c,1])

        loss = tf.math.reduce_sum(P * ((tf.math.log(Pi)*lamb1 + tf.math.log(Pj)*lamb1) - tf.math.log(P)*lamb0))
        return tf.math.minimum(loss,-EPS)
    return IICLossImple
    
# def makeLabelIICLoss(lamb0=1.0,lamb1=1.0,lamb2=1.0, EPS=sys.float_info.epsilon):
#     if tf.keras.backend.floatx() == 'float32':
#         float_limit  = tf.float32.max
#     elif tf.keras.backend.floatx() == 'float64':
#         float_limit  = tf.float64.max
#     else:
#         float_limit  = tf.float16.max
#     clipval = 1e-5 # 0.01 == 1e-2   0.0000 == 1e-5
#     def LabelIICLossImple(y,z):
#         c  = z.shape[-1]
#         y      = tf.cast(y,dtype=z.dtype)
#         lz     = tf.clip_by_value(z[0::2],clipval,1.0-clipval)
#         lzr    = 1-lz                                    # 正解の予測は値が大きくなれば
#         lzp    = lz  * tf.math.log(lzr)                  # logでマイナスが拡大する
#         lzp    = lzp * y
#         lzp    = tf.math.reduce_sum(lzp)                 # 正解ラベルの分布だけを取り出して集計すれば 0以下のlog_loss
#         labelloss = lzp / tf.math.reduce_sum(y)
        
# #         othery = 1-y
# #         z_ = z[1::2] * othery
# #         z  = z[0::2] * othery
#         z_ = z[1::2]
#         z  = z[0::2]
        
#         z  = tf.reshape(z, [-1, c, 1])
#         z_ = tf.reshape(z_, [-1, 1, c])
#         P  = tf.math.reduce_sum(z * z_, axis=0)  # 同時確率
#         P  = (P + tf.transpose(P)) / 2  # 対称化
#         P  = tf.clip_by_value(P, EPS, float_limit)  # logが発散しないようにバイアス
#         P  = P / tf.math.reduce_sum(P)  # 規格化

#         # 周辺確率
#         Pi = tf.math.reduce_sum(P, axis=0)
#         Pi = tf.reshape(Pi, [c, 1])
#         Pi = tf.tile(Pi, [1,c])
#         Pj = tf.math.reduce_sum(P, axis=1)
#         Pj = tf.reshape(Pj, [1, c])
#         Pj = tf.tile(Pj, [c,1])

#         loss = tf.math.reduce_sum(P * ((tf.math.log(Pi) + tf.math.log(Pj))*lamb1 - tf.math.log(P)*lamb0))
#         loss = loss + labelloss * lamb2
#         return tf.math.minimum(loss,-EPS)
#     return LabelIICLossImple

def makeLabelIICLoss(lamb0=1.0,lamb1=1.0,lamb2=1.0, EPS=sys.float_info.epsilon):
    if tf.keras.backend.floatx() == 'float32':
        float_limit  = tf.float32.max
    elif tf.keras.backend.floatx() == 'float64':
        float_limit  = tf.float64.max
    else:
        float_limit  = tf.float16.max
    clipval = 1e-5 # 0.01 == 1e-2   0.0000 == 1e-5
    def LabelIICLossImple(y,z):
        c  = z.shape[-1]
        y      = tf.cast(y,dtype=z.dtype)
        lz     = tf.clip_by_value(z[0::2],clipval,1.0-clipval)
        lzr    = 1-lz                                    # 正解の予測は値が大きくなれば
        lzp    = lz  * tf.math.log(lzr)                  # logでマイナスが拡大する
        lzp    = lzp * y
        lzp    = tf.math.reduce_sum(lzp)                 # 正解ラベルの分布だけを取り出して集計すれば 0以下のlog_loss
        labelloss = lzp / tf.math.reduce_sum(y)
        
        zbase = z
#         z_ = z[1::2]
#         z  = z[0::2]
        
#         z  = tf.reshape(z, [-1, c, 1])
#         z_ = tf.reshape(z_, [-1, 1, c])
#         P  = tf.math.reduce_sum(z * z_, axis=0)  # 同時確率
#         P  = (P + tf.transpose(P)) / 2  # 対称化
#         P  = tf.clip_by_value(P, EPS, float_limit)  # logが発散しないようにバイアス
#         P  = P / tf.math.reduce_sum(P)  # 規格化

        othery = 1-y
        z  = zbase
        z_ = z[1::2] * othery
        z  = z[0::2] * othery
        z  = tf.reshape(z, [-1, c, 1])
        z_ = tf.reshape(z_, [-1, 1, c])
        Po = tf.math.reduce_sum(z * z_, axis=0)  # 同時確率
        Po = (Po + tf.transpose(Po)) / 2  # 対称化
        Po = tf.clip_by_value(Po, EPS, float_limit)  # logが発散しないようにバイアス
        Po = Po / tf.math.reduce_sum(Po)  # 規格化
        P  = Po
        
        # 周辺確率
        Pi = tf.math.reduce_sum(Po, axis=0)
        Pi = tf.reshape(Pi, [c, 1])
        Pi = tf.tile(Pi, [1,c])
        Pj = tf.math.reduce_sum(Po, axis=1)
        Pj = tf.reshape(Pj, [1, c])
        Pj = tf.tile(Pj, [c,1])

        loss = tf.math.reduce_sum(P * ((tf.math.log(Pi) + tf.math.log(Pj))*lamb1 - tf.math.log(P)*lamb0))
        loss = loss + labelloss * lamb2
        return tf.math.minimum(loss,-EPS)
    return LabelIICLossImple
    
def makeUnderCrossEntropy(EPS=sys.float_info.epsilon):
    clipval = 1e-5 # 0.01 == 1e-2   0.0000 == 1e-5
    def underCrossEntropyImple(y,y_):
        y      = tf.cast(y,dtype=y_.dtype)
        lz     = tf.clip_by_value(y_,0,1.0-clipval)
        lzr    = 1-lz                                    # 正解の予測は値が大きくなれば
        lzp    = lzr * tf.math.log(lzr)                  # logでマイナスが拡大する
        lzp    = lzp * y
        lzp    = tf.math.reduce_sum(lzp)                 # 正解ラベルの分布だけを取り出して集計すれば 0以下のlog_loss
        labelloss = lzp / tf.math.reduce_sum(y)
        return labelloss
    return underCrossEntropyImple

def makeUnderCrossEntropyForIIC(EPS=sys.float_info.epsilon):
    clipval = 1e-5 # 0.01 == 1e-2   0.0000 == 1e-5
    def underCrossEntropyForIICImple(y,y_):
        y      = tf.cast(y,dtype=y_.dtype)
        y_     = y_[::2]
        lz     = tf.clip_by_value(y_,0,1.0-clipval)
        lzr    = 1-lz                                    # 正解の予測は値が大きくなれば
        lzp    = lzr * tf.math.log(lzr)                  # logでマイナスが拡大する
        lzp    = lzp * y
        lzp    = tf.math.reduce_sum(lzp)                 # 正解ラベルの分布だけを取り出して集計すれば 0以下のlog_loss
        labelloss = lzp / tf.math.reduce_sum(y)
        return labelloss
    return underCrossEntropyForIICImple


underCrossEntropy       = makeUnderCrossEntropy()
underCrossEntropyForIIC = makeUnderCrossEntropyForIIC()
IICLoss                 = makeIICLoss()
LabelIICLoss            = makeLabelIICLoss()

def makecrossentropy():
    def crossentropyImple(_yTrue,_yPred,*args,**keyargs):
        return tf.keras.losses.CategoricalCrossentropy()(_yTrue,tf.clip_by_value(_yPred,1e-10,1.0))
    return crossentropyImple
def makecrossentropyforIIC():
    def crossentropyForIICImple(_yTrue,_yPred,*args,**keyargs):
        _yPred = _yPred[::2]
        return tf.keras.losses.CategoricalCrossentropy()(_yTrue,tf.clip_by_value(_yPred,1e-10,1.0))
    return crossentropyForIICImple
crossentropy       = makecrossentropy()
crossentropyforiic = makecrossentropyforIIC()

if __name__ == '__main__':
    tf.enable_eager_execution()

    # 動作テスト
    def pytest():
        return True

    
    if not pytest():
        print("test error")
    