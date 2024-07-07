import tensorflow as tf
import numpy      as np
import math

if   tf.keras.backend.floatx() == 'float16':
    np_default_floatx = np.float16
    tf_default_floatx = tf.float16
elif tf.keras.backend.floatx() == 'float32':
    np_default_floatx = np.float32
    tf_default_floatx = tf.float32
else:
    np_default_floatx = np.float64
    tf_default_floatx = tf.float32

# def serialTile(x,t):
#     baseshape = list(x.shape)
#     x = tf.expand_dims(x,-1)
#     x = tf.tile(x,[1 for i in range(len(baseshape))]+[t])
#     x = tf.reshape(x,[-1]+baseshape[1:-1]+[baseshape[-1]*t])
#     return x

def channelTile(x,t):
    baseshape = list(x.shape)
    x = tf.tile(x,[1 for i in range(len(baseshape)-1)]+[t])
    return x

# Pairwiseでy周囲のデータを個別のチャネルに分配するフィルタ、これ自体は固定値
def makeIdentityFilter(kernel_size,channel_size,mode="kc"):
    if mode == "ck": # channel , kernel ** 2の順序で展開
        idarray = tf.eye(kernel_size**2,dtype=tf_default_floatx)
        idarray = tf.reshape(idarray,[1,kernel_size,kernel_size,-1])
        idarray = tf.tile(idarray,[1,1,1,channel_size])
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
    else: # kernel ** 2 , channelの順序で展開
        idarray = tf.eye(kernel_size**2,dtype=tf_default_floatx)
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
        idarray = tf.tile(idarray,[1,1,1,channel_size])
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
    return idarray

# 高さ幅から畳み込み専用のマップを生成する
# サイズの情報以外は定式
def makePositionMap(w_size,h_size):
    h = tf.linspace(-1.0,1.0,h_size)
    h = tf.expand_dims(h,1)
    h = tf.tile(h,[1,w_size])
    h = tf.expand_dims(h,2)
    w = tf.linspace(-1.0,1.0,w_size)
    w = tf.expand_dims(w,0)
    w = tf.tile(w,[h_size,1])
    w = tf.expand_dims(w,2)
    hw = tf.concat([h,w],axis=2)
    hw = tf.expand_dims(hw,0)
    return hw

def getPadSize(_kernel_size,_dilations):
    dilated_kernel_size = (_dilations*(_kernel_size-1)+1)
    return [dilated_kernel_size//2,dilated_kernel_size//2-(dilated_kernel_size%2==0)]

# padding：kernel_sizeが1を超える処理に向けて使う
def makeReflectPadding(_kernel_size,_dilations,_data_format="NHWC"):
    pad_size = getPadSize(_kernel_size,_dilations)
    pad_max  = max(pad_size[0],pad_size[1])
    if _data_format == "NHWC":
        pad_value = [[0,0],pad_size,pad_size,[0,0]]
        def getsize(x):
            size = list(x.shape[1:3])
            return min(size[0],size[1])
    else:
        pad_value = [[0,0],[0,0],pad_size,pad_size]
        def getsize(x):
            size = list(x.shape[2:4])
            return min(size[0],size[1])

    def reflectPaddingImple(x):
        if getsize(x) > pad_max:
            return tf.pad(x,pad_value,mode="REFLECT")
        else:
            return tf.pad(x,pad_value,mode="CONSTANT")
    return reflectPaddingImple

# Patchwiseの畳み込み
def makeUnfold(_kernel_size,_stride,_dilation,_dataformat = "NHWC"):
    if _dataformat == "NHWC":
        def setHW(_value):
            return [1,_value,_value,1]
    else:
        def setHW(_value):
            return [1,1,_value,_value]

    def unfoldImple(x):
        return tf.image.extract_patches(x,setHW(_kernel_size),setHW(_stride),setHW(_dilation),padding='VALID')
    return unfoldImple

