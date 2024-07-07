import tensorflow as tf
import numpy      as np
import re
import math
from tensorflow.keras.activations import sigmoid,linear,selu,relu,softmax,elu
from tensorflow.keras.layers      import Conv2D,BatchNormalization

activations = {
    "sigmoid":sigmoid,
    "linear":linear,
    "selu":selu,
    "relu":relu,
    "softmax":softmax,
}

if   tf.keras.backend.floatx() == 'float16':
    np_default_floatx = np.float16
    tf_default_floatx = tf.float16
elif tf.keras.backend.floatx() == 'float32':
    np_default_floatx = np.float32
    tf_default_floatx = tf.float32
else:
    np_default_floatx = np.float64
    tf_default_floatx = tf.float32
    
if re.match("2.1",tf.__version__) is not None:
    resize_image_with_pad = tf.image.resize_with_crop_or_pad
else:
    resize_image_with_pad = tf.image.resize_image_with_pad

# def rotate_fn(image):
#     return ndimage.rotate(image, np.random.uniform(-30, 30), reshape=False)

# def tf_rotate(x):
#     rotated = tf.py_function(rotate_fn,[x],[x.dtype])
#     return rotated[0]

class MyReshapeLayer(tf.keras.layers.Layer):
    def __init__(self,shape):
        super(MyReshapeLayer,self).__init__()
        self.shape_base = shape
        self.shape = tf.constant([-1]+list(shape),dtype=tf.int32)
    def build(self,input_shape):
        return
    def call(self,input):
        return tf.reshape(input,self.shape)
    def get_config(self):
        config = super(MyReshapeLayer,self).get_config()
        config.update({
            "shape":self.shape_base
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
# class MyBatchTileLayer(tf.keras.layers.Layer):
#     def __init__(self,obj):
#         super(MyBatchTileLayer,self).__init__()
#         self.const = tf.constant([1,1,1],dtype=tf.int32)
#         self.obj = obj
#     def build(self,input_shape):
#         return 
#     def call(self,input):
#         return tf.tile(self.obj,tf.concat((tf.shape(input)[:1],self.const),axis=0))
    
class MyEvenAndOddConcat(tf.keras.layers.Layer):
    # 入力レイヤーのチャネルを半分にして偶奇バッチに並べ替える
    def __init__(self):
        super(MyEvenAndOddConcat,self).__init__()
    def build(self,input_shape):
        if len(input_shape) != 4 or input_shape[-1]%2 != 0:
            def conv(x):
                return x
        else:
            sep = int(input_shape[-1]//2)
            N   = tf.constant([-1] ,dtype=tf.int32)
            C   = tf.constant([sep],dtype=tf.int32)
            reshape = tf.concat([N,input_shape[1:-1],C],axis=0)
            def conv(x,training = None):
                x2 = x[:,:,:,sep:]
                x  = x[:,:,:,:sep]
                if training:
                    x  = tf.expand_dims(x ,1)
                    x2 = tf.expand_dims(x2,1)
                    x  = tf.concat([x,x2],1)
                    x  = tf.reshape(x,reshape)
                return x
        self.conv = conv
        return 
    def call(self,input,training = None):
        x = input
        x = self.conv(x,training)
        return x
    def get_config(self):
        config = super(MyEvenAndOddConcat,self).get_config()
        config.update({
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
class MyIICExtentionLayer(tf.keras.layers.Layer):
    def __init__(self,cropScale = 7/8,segmentation = False,textimage = False,data_format = "NHWC"):
        super(MyIICExtentionLayer,self).__init__()
        self.cropScale    = cropScale
        self.segmentation = segmentation
        self.textimage    = textimage
        self.data_format  = data_format
        
    def get_config(self):
        config = super(MyIICExtentionLayer,self).get_config()
        config.update({
            "cropScale"   :self.cropScale,
            "segmentation":self.segmentation,
            "textimage"   :self.textimage,
            "data_format" :self.data_format,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
            
    def build(self,input_shape):
        self.shape       = input_shape
        self.resizeshape = tf.concat((tf.constant([-1],dtype=tf.int32),self.shape[1:]),axis=0)
        shape            = self.shape
        if self.data_format == "NHWC":
            N,H,W,C      = shape
        else:
            N,C,H,W      = shape
        cropH   = tf.cast(tf.cast(H,tf.float32) * self.cropScale,tf.int32)
        cropW   = tf.cast(tf.cast(W,tf.float32) * self.cropScale,tf.int32)
        if self.data_format == "NHWC":
            cropsize = [cropH,cropW,C]
        else:
            cropsize = [C,cropH,cropW]
        padtoH  = H
        padtoW  = W
        
        
        def cropfunc(x):
            batch = tf.shape(x)[0]
            x = tf.image.random_crop(x,[batch]+cropsize)
            x = resize_image_with_pad(x, padtoH,padtoW)
            return x
        
        def noisefunc(x):
            # jpeg quality はdataset.map向けの前処理関数
#             x = tf.image.random_jpeg_quality(x, 0, 100)
            for i in range(2):
                x = (1-x) * tf.random.normal(
                    mean=1.,
                    stddev=0.1,
                    shape=tuple(shape[1:]),
                    dtype=x.dtype)
            x = tf.clip_by_value(x, 0, 1)
            return x
        
        def rotatefunc(x):
            # investigating
            return x
        
        def distortionfunc(x):
            # investigating
            return x
        
        # un use
        def rotate90func(x):
            nrot = tf.round(tf.random.uniform(shape=(1,), minval=0, maxval=4))
            x    = tf.image.rot90(x, k=tf.squeeze(tf.cast(nrot, tf.int32)))
            return x
        
        def colorchangefunc(x):
            x = tf.image.random_brightness(x, 0.1)
            x = tf.image.random_hue(x, 0.1)
            x = tf.image.random_saturation(x,0,2)
            return x
        
        def horizontalflip(x):
            x = tf.image.random_flip_left_right(x)
            return x
        
        # un use
        def verticalflip(x):
            x = tf.image.random_flip_up_down(x)
            return x
                
        if len(shape) != 4:
            funcs = []
        elif len(shape) == 4:
            funcs = []
            if not self.segmentation:
                funcs.append(cropfunc)
            funcs.append(noisefunc)
            funcs.append(rotatefunc)
            funcs.append(distortionfunc)
            if not self.segmentation and not self.textimage:
                funcs.append(horizontalflip)
            if C != 1:
                funcs.append(colorchangefunc)

        @tf.function
        def iicExtention(x): # TODO 一次元、三次元情報にたいするノイズ付加処理は別途拡張する
            for func in funcs:
                x = func(x)
            return x
        self.iicExtention = iicExtention
        return 
    
    def call(self,input,training = None):
        x  = input
        if training:
            shape = tf.shape(x)
            x2 = self.iicExtention(x)

            x  = tf.expand_dims(x ,1)
            x2 = tf.expand_dims(x2,1)
            x  = tf.concat([x,x2],1)
            x  = tf.reshape(x,self.resizeshape)
        return x

class MyRemoveIICLayer(tf.keras.layers.Layer):
    def __init__(self):
        super(MyRemoveIICLayer,self).__init__()
        return
    def build(self,input_shape):
        return 
    
    def call(self,input,training = None):
        if training:
            return input[::2]
        else:
            return input
    def get_config(self):
        config = super(MyRemoveIICLayer,self).get_config()
        config.update({})
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
## 参考資料
# def makeDense(units,input_dim):
#     w_init = tf.random_normal_initializer()
#     w = tf.Variable(
#         initial_value=w_init(shape=(input_dim, units), dtype="float32"),
#         trainable=True,
#     )
#     b_init = tf.zeros_initializer()
#     b = tf.Variable(
#         initial_value=b_init(shape=(units,), dtype="float32"), trainable=True
#     )
#     @tf.functions
#     def denseImple(inputs):
#         return tf.matmul(inputs, w) + b
#     return denseImple

# # 内部関数にしてしまうとモデル側から変数が見えなくなる
# class Linear(tf.keras.layers.Layer):
#     def __init__(self, units=32):
#         super(Linear, self).__init__()
#         self.units = units
#     def build(self,input_shape):
#         self.dense = makeDense(self.units,input_shape[-1])
#     def call(self, inputs):
#         return self.dense(inputs)

# # クラス上に配置して直接使用する場合は見える
# class Linear2(tf.keras.layers.Layer):
#     def __init__(self, units=32):
#         super(Linear2, self).__init__()
#         self.dense = tf.keras.layers.Dense(units)
#     def build(self,input_shape):
#         return
#     def call(self, inputs):
#         return self.dense(inputs)

# # クラス上で標準レイヤーを使用する場合は見える
# class Linear3(tf.keras.layers.Layer):
#     def __init__(self, units=32):
#         super(Linear3, self).__init__()
#         self.units = units
#     def build(self,input_shape):
#         input_dim=input_shape[-1]
#         units = self.units
#         w_init = tf.random_normal_initializer()
#         self.w = tf.Variable(
#             initial_value=w_init(shape=(input_dim, units), dtype="float32"),
#             trainable=True,
#         )
#         b_init = tf.zeros_initializer()
#         self.b = tf.Variable(
#             initial_value=b_init(shape=(units,), dtype="float32"), trainable=True
#         )

#     def call(self, inputs):
#         return tf.matmul(inputs, self.w) + self.b


# # TODO Utilを拡張レイヤーとしてクラス化
# from LayerUtil import serialTile,channelTile
# from LayerUtil import makeIdentityFilter
# from LayerUtil import makePositionMap,getPadSize,makeReflectPadding,makeUnfold


class serialTile(tf.keras.layers.Layer):
    def __init__(self, t):
        super(serialTile, self).__init__()
        self.t = t
    def build(self,input_shape):
        self.tileshape = [1]*len(input_shape)+[self.t]
        self.tileshape = tf.constant(self.tileshape,dtype=tf.int32)
        self.outshape  = tf.concat([[-1],input_shape[1:-1],[input_shape[-1]*self.t]],axis=0)
        self.outshape  = tf.constant(self.outshape,dtype=tf.int32)
        return
    def call(self, inputs):
        x = inputs
        x = tf.expand_dims(x,-1)
        x = tf.tile(x,self.tileshape)
        x = tf.reshape(x,self.outshape)
        return x
    def get_config(self):
        config = super(serialTile,self).get_config()
        config.update({
            "t":self.t,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)

class channelTile(tf.keras.layers.Layer):
    def __init__(self,t):
        super(channelTile, self).__init__()
        self.t = t
        return
    def build(self,input_shape):
        self.tileshape = [1]*(len(input_shape)-1)+[self.t]
        self.tileshape = tf.constant(self.tileshape,dtype=tf.int32)
        return
    def call(self,inputs):
        x = inputs
        x = tf.tile(x,self.tileshape)
        return x
    def get_config(self):
        config = super(channelTile,self).get_config()
        config.update({
            "t"   :self.t,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
# padding：kernel_sizeが1を超える処理に向けて使う
class refpad(tf.keras.layers.Layer):
    def __init__(self,_kernel_size,_dilations,_data_format="NHWC"):
        super(refpad, self).__init__()
        self.dilations   = _dilations
        self.kernel_size = _kernel_size
        
        D = _dilations
        K = _kernel_size
        DK = (D*(K-1)+1)
        pad_size = [DK//2-((DK+1)%2),DK//2]
        self.pad_max  = max(pad_size[0],pad_size[1])
        self.data_format = _data_format
        if self.data_format == "NHWC":
            self.pad_value = [[0,0],pad_size,pad_size,[0,0]]
        else:
            self.pad_value = [[0,0],[0,0],pad_size,pad_size]
            
        return
    
    def get_config(self):
        config = super(refpad,self).get_config()
        config.update({
            "_kernel_size":self.kernel_size,
            "_dilations"  :self.dilations,
            "_data_format":self.data_format,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
    def build(self,input_shape):
        if self.data_format == "NHWC":
            size      = list(input_shape[1:3])
        else:
            size      = list(input_shape[2:4])
            
        if size[0] > self.pad_max and size[1] > self.pad_max:
            self.mode = "REFLECT"
        else:
            self.mode = "CONSTANT"
        return
    
    def call(self,inputs):
        x = inputs
        x = tf.pad(x,self.pad_value,mode=self.mode)
        return x
    
# padding：kernel_sizeが1を超える処理に向けて使う
class zeropad(tf.keras.layers.Layer):
    def __init__(self,_kernel_size,_dilations,_data_format="NHWC"):
        super(zeropad, self).__init__()
        self.dilations   = _dilations
        self.kernel_size = _kernel_size
        
        D = _dilations
        K = _kernel_size
        DK = (D*(K-1)+1)
        pad_size = [DK//2-((DK+1)%2),DK//2]
        self.pad_max  = max(pad_size[0],pad_size[1])
        self.data_format = _data_format
        if self.data_format == "NHWC":
            self.pad_value = [[0,0],pad_size,pad_size,[0,0]]
        else:
            self.pad_value = [[0,0],[0,0],pad_size,pad_size]
            
        return
    def get_config(self):
        config = super(zeropad,self).get_config()
        config.update({
            "_kernel_size":self.kernel_size,
            "_dilations"  :self.dilations,
            "_data_format":self.data_format,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
    def call(self,inputs):
        x = inputs
        x = tf.pad(x,self.pad_value,mode="CONSTANT")
        return x
    
class unfold(tf.keras.layers.Layer):
    def __init__(self,_kernel_size,_strides,_dilations,_data_format = "NHWC",_padding = "VALID"):
        super(unfold, self).__init__()
        
        if _data_format == "NHWC":
            def setHW(_value):
                return [1,_value,_value,1]
        else:
            def setHW(_value):
                return [1,1,_value,_value]
            
        self.kernel_size_shape = setHW(_kernel_size)
        self.strides_shape     = setHW(_strides)
        self.dilations_shape   = setHW(_dilations)
        
        self.kernel_size = _kernel_size
        self.strides     = _strides
        self.dilations   = _dilations
        self.data_format = _data_format
        self.padding     = _padding
        
    def get_config(self):
        config = super(unfold,self).get_config()
        config.update({
            "_kernel_size":self.kernel_size,
            "_strides"    :self.strides,
            "_dilations"  :self.dilations,
            "_data_format":self.data_format,
            "_padding"    :self.padding,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
    def build(self,input_shape):
        return
    def call(self,inputs,training):
        x = inputs
        x = tf.image.extract_patches(x,self.kernel_size_shape,self.strides_shape,self.dilations_shape,padding=self.padding)
        return x

class depthwise_patches(tf.keras.layers.Layer):
    def __init__(self,_kernel_size,_strides,_dilations,_data_format = "NHWC",_padding = "VALID"):
        super(depthwise_patches, self).__init__()
        
        if _data_format == "NHWC":
            def setHW(_value):
                return [1,_value,_value,1]
        else:
            def setHW(_value):
                return [1,1,_value,_value]
            
        self.kernel_size_shape = setHW(_kernel_size)
        self.strides_shape     = setHW(_strides)
        self.dilations_shape   = setHW(_dilations)
        
        self.kernel_size = _kernel_size
        self.strides     = _strides
        self.dilations   = _dilations
        self.data_format = _data_format
        self.padding     = _padding
        
    def get_config(self):
        config = super(depthwise_patches,self).get_config()
        config.update({
            "_kernel_size":self.kernel_size,
            "_strides"    :self.strides,
            "_dilations"  :self.dilations,
            "_data_format":self.data_format,
            "_padding"    :self.padding,
        })
        return config
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
    def build(self,input_shape):
        if self.data_format == "NHWC":
            strides   = [1,self.strides  ,self.strides,1]
            dilations = [self.dilations,self.dilations]
            getstrides = lambda x:x[:,::self.strides,::self.strides,:]
            C = input_shape[-1]
        else:
            strides   = [1,1,self.strides,self.strides]
            dilations = [self.dilations,self.dilations]
            getstrides = lambda x:x[:,:,::self.strides,::self.strides]
            C = input_shape[1]
        channelTile_xi = channelTile(self.kernel_size**2)
        f              = makeIdentityFilter(self.kernel_size,C,mode="kc")
        if (self.strides-1)*(self.dilations-1) == 0:
            xi2xj = lambda xi:tf.nn.depthwise_conv2d(xi,f,strides,self.padding,self.data_format,dilations)
        else:
            def xi2xj(xi):
                xj = tf.nn.depthwise_conv2d(xi,f,[1,1,1,1],self.padding,self.data_format,dilations)
                xj = getstrides(xj)
                return xj2

        def depthwise_patches_func(x):
            xi = channelTile_xi(x)
            xj = xi2xj(xi)
            return xj
        self.depthwise_patches = depthwise_patches_func
        
        return
    def call(self,inputs,training):
        x = inputs
        x = self.depthwise_patches(x)
        return x

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

# def getPadSize(_kernel_size,_dilations):
#     dilated_kernel_size = (_dilations*(_kernel_size-1)+1)
#     return [dilated_kernel_size//2,dilated_kernel_size//2-(dilated_kernel_size%2==0)]

# # padding：kernel_sizeが1を超える処理に向けて使う
# def makeReflectPadding(_kernel_size,_dilations,_data_format="NHWC"):
#     pad_size = getPadSize(_kernel_size,_dilations)
#     pad_max  = max(pad_size[0],pad_size[1])
#     if _data_format == "NHWC":
#         pad_value = [[0,0],pad_size,pad_size,[0,0]]
#         def getsize(x):
#             size = list(x.shape[1:3])
#             return min(size[0],size[1])
#     else:
#         pad_value = [[0,0],[0,0],pad_size,pad_size]
#         def getsize(x):
#             size = list(x.shape[2:4])
#             return min(size[0],size[1])

#     def reflectPaddingImple(x):
#         if getsize(x) > pad_max:
#             return tf.pad(x,pad_value,mode="REFLECT")
#         else:
#             return tf.pad(x,pad_value,mode="CONSTANT")
#     return reflectPaddingImple

# # Patchwiseの畳み込み
# def makeUnfold(_kernel_size,_stride,_dilation,_dataformat = "NHWC"):
#     if _dataformat == "NHWC":
#         def setHW(_value):
#             return [1,_value,_value,1]
#     else:
#         def setHW(_value):
#             return [1,1,_value,_value]

#     def unfoldImple(x):
#         return tf.image.extract_patches(x,setHW(_kernel_size),setHW(_stride),setHW(_dilation),padding='VALID')
#     return unfoldImple

# %%time
# def patches_native(x,K,stride = 1,dilation = 1):
#     x = tf.image.extract_patches(x,[1,K,K,1],[1,stride,stride,1],[1,dilation,dilation,1],"SAME")
#     x = tf.reshape(x,[-1,C,K**2])
#     return x
# display(patches_native(x,K))

def makeIdentityFilter(kernel_size,channel_size,mode="kc"):
    if mode == "kc": # kernel ** 2 , channelの順序で展開
        idarray = tf.eye(kernel_size**2,dtype=tf_default_floatx)
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
        idarray = tf.tile(idarray,[1,1,1,channel_size])
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
    else: # channel , kernel ** 2の順序で展開
        idarray = tf.eye(kernel_size**2,dtype=tf_default_floatx)
        idarray = tf.reshape(idarray,[1,kernel_size,kernel_size,-1])
        idarray = tf.tile(idarray,[1,1,1,channel_size])
        idarray = tf.reshape(idarray,[kernel_size,kernel_size,-1,1])
    return idarray
    
# Vitではなく畳み込みAttention
PAIRWISE  = 0
PATCHWISE = 1

class MyCNNSelfAttentionBaseModule(tf.keras.Model):
    # Pairwiseで個別に分配したチャネルと突き合わせる為のデータを複製
    # dataformatを変更する場合、dimと複製するCの位置を再確認する必要あり


    def __init__(self,
                 _relation_size,
                 _out_filter_size,
                 _kernel_size        = 3,
                 _strides            = 1,
                 _dilations          = 1,
                 _activation         = None,
                 _kernel_initializer = None,
                 _kernel_regularizer = None,
                 _data_format        = "NHWC"):
        
        super(MyCNNSelfAttentionBaseModule,self).__init__()
        self.relation_size      = _relation_size
        self.out_filter_size    = _out_filter_size
        self.kernel_size        = _kernel_size
        self.strides            = _strides
        self.dilations          = _dilations
        self.activation         = _activation
        self.kernel_initializer = _kernel_initializer
        self.kernel_regularizer = _kernel_regularizer
        self.data_format        = _data_format
        
        # point conv で regとinitが必要
        if self.activation is None:
            activation = "relu"
        else:
            activation = self.activation
            
        convParam = {"kernel_initializer":self.kernel_initializer,
                     "kernel_regularizer":self.kernel_regularizer }
        
        self.base_conv1      = Conv2D(self.relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv2      = Conv2D(self.relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv3      = Conv2D(self.out_filter_size,(1,1),activation="linear",**convParam)

        share_size           = min(8,int(math.floor(math.sqrt(self.out_filter_size))))
        self.attention_nrom1 = BatchNormalization()
        self.attention_conv1 = Conv2D(self.out_filter_size//share_size,(1,1),activation=activation,**convParam)
        self.attention_nrom2 = BatchNormalization()
        self.attention_conv2 = Conv2D(self.out_filter_size            ,(1,1),activation=activation,**convParam)
        
    def samodule(self,_inputLayer):
        return _inputLayer
    def patches_ax(self,_inputLayer):
        return _inputLayer
    def usefunction(self,x,y):
        return 

    def build(self,input_shapes):
        
        if self.data_format == "NHWC":
            strides   = [1,self.strides,self.strides,1]
            dilations = [self.dilations,self.dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,self.strides,self.strides]
            dilations = [self.dilations,self.dilations]
            c,h,w     = input_shapes[1:]

        zeropad_x3  = zeropad(self.kernel_size,self.dilations)
        x2xj_x3     = depthwise_patches(self.kernel_size,self.strides,self.dilations,self.data_format)

        reshape_xj3 = MyReshapeLayer([h*w//self.strides**2,self.kernel_size**2,self.out_filter_size])
        reshape_abx = MyReshapeLayer([h//self.strides,w//self.strides,self.out_filter_size])
        
        def SALayerImple(_inputLayer):

            x   = _inputLayer
            x3  = self.base_conv3(x)
            x3  = zeropad_x3(x3)
            xj3 = x2xj_x3(x3)
            xj3 = reshape_xj3(xj3)

            ax  = self.samodule(x)
            ax  = self.attention_nrom1(ax)
            ax  = self.attention_conv1(ax)
            ax  = self.attention_nrom2(ax)
            ax  = self.attention_conv2(ax)
            ax  = self.patches_ax(ax)
            aw  = tf.nn.softmax(ax)
            
            abx = tf.multiply(aw,xj3)
            abx = tf.reduce_sum(abx,-2)
            abx = reshape_abx(abx)
            return abx
        self.SALayerImple = SALayerImple

    def call(self,inputs):
        x = inputs
        x = self.SALayerImple(x)
        return x
    
    def get_config(self):
        config = super(MyCNNSelfAttentionBaseModule,self).get_config()
        config.update({
            "_relation_size"        :self.relation_size,
            "_out_filter_size"      :self.out_filter_size,
            "_kernel_size"          :self.kernel_size,
            "_strides"              :self.strides,
            "_dilations"            :self.dilations,
            "_activation"           :self.activation,
            "_kernel_initializer"   :self.kernel_initializer,
            "_kernel_regularizer"   :self.kernel_regularizer,
            "_data_format"          :self.data_format,
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)
    
class MyCNNSelfAttentionPatchWiseModule(MyCNNSelfAttentionBaseModule):
    def usefunction(self,x,y):
        return tf.concat([x,y],-1)
    
    def build(self,input_shapes):
        super(MyCNNSelfAttentionPatchWiseModule,self).build(input_shapes)
        
        if self.data_format == "NHWC":
            strides   = [1,self.strides,self.strides,1]
            dilations = [self.dilations,self.dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,self.strides,self.strides]
            dilations = [self.dilations,self.dilations]
            c,h,w     = input_shapes[1:]

        if self.strides != 1:
            strides_x1 = unfold(1,self.strides,self.dilations)
        else:
            strides_x1 = lambda x:x
        reshape_x1  = MyReshapeLayer([h*w//self.strides**2,1,self.relation_size])

        refpad_x2   = refpad(self.kernel_size,self.dilations)
        unfold_x2   = unfold(self.kernel_size,self.strides,self.dilations)
        reshape_xj2 = MyReshapeLayer([h*w//self.strides**2,1,self.kernel_size**2*self.relation_size])
        
        def patchwiseModule(_x):

            x1  = self.base_conv1(_x)
            x1  = strides_x1(x1)
            x1  = reshape_x1(x1)

            x2  = self.base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = unfold_x2(x2)
            xj2 = reshape_xj2(xj2)

            ax  = self.usefunction(x1,xj2)

            return ax

        self.samodule = patchwiseModule
        
        serialTile_ax = serialTile(self.kernel_size**2)
        reshape_ax    = MyReshapeLayer([h*w//self.strides**2,self.kernel_size**2,self.out_filter_size])
        def patches_ax(ax):
            ax = serialTile_ax(ax)
            ax = reshape_ax(ax)
            return ax
        self.patches_ax = patches_ax
        
        return
            
    @classmethod
    def from_config(cls, config):
        return cls(**config)

    
class MyCNNSelfAttentionPairWiseModule(MyCNNSelfAttentionBaseModule):
    def usefunction(self,x,y):
        return tf.subtract(x,y)
    
    def build(self,input_shapes):
        super(MyCNNSelfAttentionPairWiseModule,self).build(input_shapes)
        
        convParam = {
            "kernel_initializer":self.kernel_initializer,
            "kernel_regularizer":self.kernel_regularizer,
        }
        
        if self.data_format == "NHWC":
            strides   = [1,self.strides,self.strides,1]
            dilations = [self.dilations,self.dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,self.strides,self.strides]
            dilations = [self.dilations,self.dilations]
            c,h,w     = input_shapes[1:]

        serialTile_xi1 = serialTile(self.kernel_size**2)
        if self.strides > 1:
            strides_xi1    = unfold(1,self.strides,1,self.data_format)
        else:
            strides_xi1    = lambda x:x

        refpad_xi2     = refpad(self.kernel_size,self.dilations)
        xi2xj          = depthwise_patches(self.kernel_size,self.strides,self.dilations,self.data_format)

        reshape_ax     = MyReshapeLayer([h*w//self.strides**2,
                                         self.kernel_size**2,self.relation_size])

        # TODO self.pcにすると一応学習するようだが、i/oに繋がりが見えず動作不詳
        # 全てSelfでつなげる必要があるか？
        pc             = Conv2D(2,(1,1),activation="linear",**convParam)
        po_raw          = makePositionMap(w,h)
        if self.strides != 1:
            strides_poi = unfold(1,self.strides,1,self.data_format)
        else:
            strides_poi = lambda x:x
        channelTile_poi = channelTile(self.kernel_size**2)

        refpad_poj      = refpad(self.kernel_size,self.dilations)
        po2poj          = depthwise_patches(self.kernel_size,self.strides,self.dilations,self.data_format)
        kcsplit_po      = MyReshapeLayer([h*w//self.strides**2,self.kernel_size**2,2])
        
        def pairwiseModule(_x):

            # xi の生成 [ n , h , w , c*k**2 ]
            x1  = self.base_conv1(_x)
            xi1 = serialTile_xi1(x1)
            xi1 = strides_xi1(xi1)

            # xj の生成 [ n , h , w , k**2*c ]
            x2  = self.base_conv2(_x)
            xi2 = refpad_xi2(x2)
            xj2 = xi2xj(xi2)
            
            # xiとxjのペアを加工 [ n , h , w , c*k**2 ]
            ax  = self.usefunction(xi1,xj2)
            
            # 座標組み込みの為に変形 [ n , h*w , k**2 , c ]
            ax  = reshape_ax(ax)
            
            # 座標コード の生成 [ 1 , h , w , k**2 , 2 ]
            po  = pc(po_raw)
            poi = strides_poi(po)
            poi = channelTile_poi(poi)
            
            poj = refpad_poj(po)
            poj = po2poj(poj)
            
            po  = tf.subtract(poi,poj)
            po  = kcsplit_po(po)
            # [ 1 , h , w , k**2*2 ]となっているため、axに合わせて nを増やす [ n , h , w , k**2*2 ]
            n   = tf.shape(ax)[0]
            po  = tf.tile(po,[n,1,1,1])

            axp = tf.concat([ax,po],axis=-1)
            return axp

        self.samodule   = pairwiseModule
            
    @classmethod
    def from_config(cls, config):
        return cls(**config)
        
class MyCNNSelfAttentionModule(tf.keras.Model):
    # Pairwiseで個別に分配したチャネルと突き合わせる為のデータを複製
    # dataformatを変更する場合、dimと複製するCの位置を再確認する必要あり


    def __init__(self,
                 _relation_size,
                 _out_filter_size,
                 _kernel_size        = 3,
                 _strides            = 1,
                 _dilations          = 1,
                 _satype             = PATCHWISE,
                 _function           = None,
                 _activation         = None,
                 _kernel_initializer = None,
                 _kernel_regularizer = None,
                 _data_format        = "NHWC"):
        
        super(MyCNNSelfAttentionModule,self).__init__()
        self.relation_size      = _relation_size
        self.out_filter_size    = _out_filter_size
        self.kernel_size        = _kernel_size
        self.strides            = _strides
        self.dilations          = _dilations
        self.satype             = _satype
        self.function           = _function
        self.activation         = _activation
        self.kernel_initializer = _kernel_initializer
        self.kernel_regularizer = _kernel_regularizer
        self.data_format        = _data_format
        
        # point conv で regとinitが必要
        if _activation is None:
            activation = "relu"
        else:
            activation = _activation
            
        convParam = {"kernel_initializer":_kernel_initializer,
                     "kernel_regularizer":_kernel_regularizer }
        
        self.base_conv1      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv2      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv3      = Conv2D(_out_filter_size,(1,1),activation="linear",**convParam)
        if _satype == PAIRWISE:
            self.pc          = Conv2D(2,(1,1),activation="linear",**convParam)

        share_size           = min(8,int(math.floor(math.sqrt(_out_filter_size))))
        self.attention_nrom1 = BatchNormalization()
        self.attention_conv1 = Conv2D(_out_filter_size//share_size,(1,1),activation=activation,**convParam)
        self.attention_nrom2 = BatchNormalization()
        self.attention_conv2 = Conv2D(_out_filter_size            ,(1,1),activation=activation,**convParam)

    def build(self,input_shapes):
        _relation_size      = self.relation_size
        _out_filter_size    = self.out_filter_size
        _kernel_size        = self.kernel_size
        _strides            = self.strides
        _dilations          = self.dilations
        _satype             = self.satype
        _function           = self.function
        _activation         = self.activation
        _kernel_initializer = self.kernel_initializer
        _kernel_regularizer = self.kernel_regularizer
        _data_format        = self.data_format
        
        
        if _data_format == "NHWC":
            strides   = [1,_strides,_strides,1]
            dilations = [_dilations,_dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,_strides,_strides]
            dilations = [_dilations,_dilations]
            c,h,w     = input_shapes[1:]

        if _function is None:
            if _satype == PAIRWISE:
                usefunction = lambda x,y:tf.subtract(x,y)
            else:
                usefunction = lambda x,y:tf.concat([x,y],-1)
        else:
            usefunction = _function

        
        if _satype == PAIRWISE:
            serialTile_xi1 = serialTile(_kernel_size**2)
            if _strides > 1:
                strides_xi1    = unfold(1,_strides,1,_data_format)
            else:
                strides_xi1    = lambda x:x
                
            refpad_xi2     = refpad(_kernel_size,_dilations)
            channelTile_x2 = channelTile(_kernel_size**2)
            f2             = makeIdentityFilter(_kernel_size,_relation_size,mode="kc")
            if (_strides-1)*(_dilations-1) == 0:
                xi2xj = lambda xi2:tf.nn.depthwise_conv2d(xi2,f2,strides,"VALID",_data_format,dilations)
            else:
                unfold_xj2 = unfold(1,_strides,1,_data_format)
                def xi2xj(xi2):
                    xj2 = tf.nn.depthwise_conv2d(xi2,f2,[1,1,1,1],"VALID",_data_format,dilations)
                    xj2 = unfold_xj2(xj2)
                    return xj2
                
            reshape_ax     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_relation_size])
            
            po             = makePositionMap(w,h)
            channelTile_po = channelTile(_kernel_size**2)
            
            pf             = makeIdentityFilter(_kernel_size,2,mode="kc")
            refpad_poj     = refpad(_kernel_size,_dilations)
            def poipoj(poi):
                poj = refpad_poj(poi)
                poj = tf.nn.depthwise_conv2d(poj,pf,[1,1,1,1],"VALID",_data_format,dilations)
                return poj
                
            if _strides != 1:
                strides_po = unfold(1,_strides,1,_data_format)
            else:
                strides_po = lambda x:x
            kcsplit_po     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,2])
        
        def pairwiseModule(_x):

            # xi の生成 [ n , h , w , c*k**2 ]
            x1  = self.base_conv1(_x)
            xi1 = serialTile_xi1(x1)
            xi1 = strides_xi1(xi1)

            # xj の生成 [ n , h , w , k**2*c ]
            x2  = self.base_conv2(_x)
            xi2 = channelTile_x2(x2)
            xi2 = refpad_xi2(xi2)
            xj2 = xi2xj(xi2)
            
            # xiとxjのペアを加工 [ n , h , w , c*k**2 ]
            ax  = _usefunction(xi1,xj2)
            
            # 座標組み込みの為に変形 [ n , h*w , k**2 , c ]
            ax  = rehape_ax(ax)
            
            # 座標コード の生成 [ 1 , h , w , k**2 , 2 ]
            po  = self.pc(po)
            poi = channelTile_po(po)
            poj = poipoj(poi)
            po  = tf.subtract(poi,poj)
            # [ 1 , h , w , k**2*2 ]となっているため、axに合わせて nを増やす [ n , h , w , k**2*2 ]
            po  = MyBatchTileLayer(po)(ax)
            po  = strides_po(po)
            po  = kcsplit_po(po)

            axp = tf.concat([ax,po],axis=-1)
            return axp

        if _satype == PATCHWISE:
            if _strides != 1:
                strides_x1 = unfold(1,_strides,_dilations)
            else:
                strides_x1 = lambda x:x
            reshape_x1  = MyReshapeLayer([h*w//_strides**2,1,_relation_size])
                
            refpad_x2   = refpad(_kernel_size,_dilations)
            unfold_x2   = unfold(_kernel_size,_strides,_dilations)
            reshape_xj2 = MyReshapeLayer([h*w//_strides**2,1,_kernel_size**2*_relation_size])
                
        def patchwiseModule(_x):

            x1  = self.base_conv1(_x)
            x1  = strides_x1(x1)
            x1  = reshape_x1(x1)

            x2  = self.base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = unfold_x2(x2)
            xj2 = reshape_xj2(xj2)

            ax  = usefunction(x1,xj2)

            return ax

        if _satype == PATCHWISE:
            samodule      = patchwiseModule
            serialTile_ax = serialTile(_kernel_size**2)
            reshape_ax    = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
            def patches_ax(ax):
                ax = serialTile_ax(ax)
                ax = reshape_ax(ax)
                return ax
        else:
            samodule   = pairwiseModule
            patches_ax = lambda x:x

        zeropad_x3  = zeropad(_kernel_size,_dilations)
        x2xj_x3     = depthwise_patches(_kernel_size,_strides,_dilations,_data_format)

        reshape_xj3 = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
        reshape_abx = MyReshapeLayer([h//_strides,w//_strides,_out_filter_size])
        
        def SALayerImple(_inputLayer):

            x   = _inputLayer
            x3  = self.base_conv3(x)
            x3  = zeropad_x3(x3)
            xj3 = x2xj_x3(x3)
            xj3 = reshape_xj3(xj3)

            ax  = samodule(x)
            ax  = self.attention_nrom1(ax)
            ax  = self.attention_conv1(ax)
            ax  = self.attention_nrom2(ax)
            ax  = self.attention_conv2(ax)
            ax  = patches_ax(ax)
            aw  = tf.nn.softmax(ax)
            
            abx = tf.multiply(aw,xj3)
            abx = tf.reduce_sum(abx,-2)
            abx = reshape_abx(abx)
            return abx
        self.SALayerImple = SALayerImple

    def call(self,inputs):
        x = inputs
        x = self.SALayerImple(x)
        return x
    
    def get_config(self):
        config = super(MyCNNSelfAttentionModule,self).get_config()
        config.update({
            "_relation_size"        :self.relation_size,
            "_out_filter_size"      :self.out_filter_size,
            "_kernel_size"          :self.kernel_size,
            "_strides"              :self.strides,
            "_dilations"            :self.dilations,
            "_satype"               :self.satype,
            "_function"             :self.function,
            "_activation"           :self.activation,
            "_kernel_initializer"   :self.kernel_initializer,
            "_kernel_regularizer"   :self.kernel_regularizer,
            "_data_format"          :self.data_format,
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)

class MyCNNSelfAttentionModule2(tf.keras.Model):
    # Pairwiseで個別に分配したチャネルと突き合わせる為のデータを複製
    # dataformatを変更する場合、dimと複製するCの位置を再確認する必要あり


    def __init__(self,
                 _relation_size,
                 _out_filter_size,
                 _kernel_size        = 3,
                 _strides            = 1,
                 _dilations          = 1,
                 _satype             = PATCHWISE,
                 _function           = None,
                 _activation         = None,
                 _kernel_initializer = None,
                 _kernel_regularizer = None,
                 _data_format        = "NHWC"):
        
        super(MyCNNSelfAttentionModule2,self).__init__()
        self.relation_size      = _relation_size
        self.out_filter_size    = _out_filter_size
        self.kernel_size        = _kernel_size
        self.strides            = _strides
        self.dilations          = _dilations
        self.satype             = _satype
        self.function           = _function
        self.activation         = _activation
        self.kernel_initializer = _kernel_initializer
        self.kernel_regularizer = _kernel_regularizer
        self.data_format        = _data_format
        
        # point conv で regとinitが必要
        if _activation is None:
            activation = "relu"
        else:
            activation = _activation
            
        convParam = {"kernel_initializer":_kernel_initializer,
                     "kernel_regularizer":_kernel_regularizer }
        
        self.base_conv1      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv2      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
        self.base_conv3      = Conv2D(_out_filter_size,(1,1),activation="linear",**convParam)
        if _satype == PAIRWISE:
            self.pc          = Conv2D(2,(1,1),activation="linear",**convParam)

        share_size           = min(8,int(math.floor(math.sqrt(_out_filter_size))))
        self.attention_nrom1 = BatchNormalization()
        self.attention_conv1 = Conv2D(_out_filter_size//share_size,(1,1),activation=activation,**convParam)
        self.attention_nrom2 = BatchNormalization()
        self.attention_conv2 = Conv2D(_out_filter_size            ,(1,1),activation=activation,**convParam)

    def build(self,input_shapes):
        _relation_size      = self.relation_size
        _out_filter_size    = self.out_filter_size
        _kernel_size        = self.kernel_size
        _strides            = self.strides
        _dilations          = self.dilations
        _satype             = self.satype
        _function           = self.function
        _activation         = self.activation
        _kernel_initializer = self.kernel_initializer
        _kernel_regularizer = self.kernel_regularizer
        _data_format        = self.data_format
        
        
        if _data_format == "NHWC":
            strides   = [1,_strides,_strides,1]
            dilations = [_dilations,_dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,_strides,_strides]
            dilations = [_dilations,_dilations]
            c,h,w     = input_shapes[1:]

        if _function is None:
            if _satype == PAIRWISE:
                usefunction = lambda x,y:tf.subtract(x,y)
            else:
                usefunction = lambda x,y:tf.concat([x,y],-1)
        else:
            usefunction = _function

        
        if _satype == PAIRWISE:
            serialTile_xi1 = serialTile(_kernel_size**2)
            if _strides > 1:
                strides_xi1    = unfold(1,_strides,1,_data_format)
            else:
                strides_xi1    = lambda x:x
                
            refpad_x2      = refpad(_kernel_size,_dilations)
            xixj_x2        = depthwise_patches(_kernel_size,_strides,_dilations,_data_format)
                
            reshape_ax     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_relation_size])
            
            self.po        = makePositionMap(w,h)
            
#             channelTile_po = channelTile(_kernel_size**2)
#             refpad_po      = refpad(_kernel_size,_dilations)
#             po2poj         = depthwise_patches(_kernel_size,1,_dilations,_data_format)
            
            
            channelTile_poi = channelTile(_kernel_size**2)
            refpad_poj      = refpad(_kernel_size,_dilations)
            pf              = makeIdentityFilter(_kernel_size,2,mode="kc")
            unfold_poj      = lambda poj:tf.nn.depthwise_conv2d(poj,pf,[1,1,1,1],"VALID",_data_format,dilations)
            
            
            strides_po     = unfold(1,_strides,1,_data_format)
            kcsplit_po     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,2])
        
        def pairwiseModule(_x):

            # xi の生成 [ n , h , w , c*k**2 ]
            x1  = self.base_conv1(_x)
            xi1 = serialTile_xi1(x1)
            xi1 = strides_xi1(xi1)

            # xj の生成 [ n , h , w , k**2*c ]
            x2  = self.base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = xixj_x2(x2)
            
            # xiとxjのペアを加工 [ n , h , w , c*k**2 ]
            ax  = usefunction(xi1,xj2)
            
            # 座標組み込みの為に変形 [ n , h*w , k**2 , c ]
            ax  = reshape_ax(ax)
            
            # 座標コード の生成 [ 1 , h , w , k**2 , 2 ]
            po  = self.pc(self.po)
            poi = channelTile_poi(po)
            poj = refpad_poj(poi)
            poj = unfold_poj(poj)
            po  = tf.subtract(poi,poj)
            # [ 1 , h , w , k**2*2 ]となっているため、axに合わせて nを増やす [ n , h , w , k**2*2 ]
            n   = tf.shape(ax)[0]
            po  = tf.tile(po,[n,1,1,1])
            po  = strides_po(po)
            po  = kcsplit_po(po)

            axp = tf.concat([ax,po],axis=-1)
            return axp

        if _satype == PATCHWISE:
            if _strides != 1:
                strides_x1 = unfold(1,_strides,_dilations)
            else:
                strides_x1 = lambda x:x
            reshape_x1  = MyReshapeLayer([h*w//_strides**2,1,_relation_size])
                
            refpad_x2   = refpad(_kernel_size,_dilations)
            unfold_x2   = unfold(_kernel_size,_strides,_dilations)
            reshape_xj2 = MyReshapeLayer([h*w//_strides**2,1,_kernel_size**2*_relation_size])
                
        def patchwiseModule(_x):

            x1  = self.base_conv1(_x)
            x1  = strides_x1(x1)
            x1  = reshape_x1(x1)

            x2  = self.base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = unfold_x2(x2)
            xj2 = reshape_xj2(xj2)

            ax  = usefunction(x1,xj2)

            return ax

        if _satype == PATCHWISE:
            samodule      = patchwiseModule
            serialTile_ax = serialTile(_kernel_size**2)
            reshape_ax    = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
            def patches_ax(ax):
                ax = serialTile_ax(ax)
                ax = reshape_ax(ax)
                return ax
        else:
            samodule   = pairwiseModule
            patches_ax = lambda x:x

        zeropad_x3  = zeropad(_kernel_size,_dilations)
        x2xj_x3     = depthwise_patches(_kernel_size,_strides,_dilations,_data_format)

        reshape_xj3 = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
        reshape_abx = MyReshapeLayer([h//_strides,w//_strides,_out_filter_size])
        
        def SALayerImple(_inputLayer):

            x   = _inputLayer
            x3  = self.base_conv3(x)
            x3  = zeropad_x3(x3)
            xj3 = x2xj_x3(x3)
            xj3 = reshape_xj3(xj3)

            ax  = samodule(x)
            ax  = self.attention_nrom1(ax)
            ax  = self.attention_conv1(ax)
            ax  = self.attention_nrom2(ax)
            ax  = self.attention_conv2(ax)
            ax  = patches_ax(ax)
            aw  = tf.nn.softmax(ax)
            
            abx = tf.multiply(aw,xj3)
            abx = tf.reduce_sum(abx,-2)
            abx = reshape_abx(abx)
            return abx
        self.SALayerImple = SALayerImple

    def call(self,inputs):
        x = inputs
        x = self.SALayerImple(x)
        return x
    
    def get_config(self):
        config = super(MyCNNSelfAttentionModule2,self).get_config()
        config.update({
            "_relation_size"        :self.relation_size,
            "_out_filter_size"      :self.out_filter_size,
            "_kernel_size"          :self.kernel_size,
            "_strides"              :self.strides,
            "_dilations"            :self.dilations,
            "_satype"               :self.satype,
            "_function"             :self.function,
            "_activation"           :self.activation,
            "_kernel_initializer"   :self.kernel_initializer,
            "_kernel_regularizer"   :self.kernel_regularizer,
            "_data_format"          :self.data_format,
        })
        return config
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)

    
def MyCNNSelfAttentionLayer(
    # Pairwiseで個別に分配したチャネルと突き合わせる為のデータを複製
    # dataformatを変更する場合、dimと複製するCの位置を再確認する必要あり


    
                 _relation_size,
                 _out_filter_size,
                 _kernel_size        = 3,
                 _strides            = 1,
                 _dilations          = 1,
                 _satype             = PATCHWISE,
                 _function           = None,
                 _activation         = None,
                 _kernel_initializer = None,
                 _kernel_regularizer = None,
                 _data_format        = "NHWC"):
    
    # point conv で regとinitが必要
    if _activation is None:
        activation = "relu"
    else:
        activation = _activation
        
    convParam = {"kernel_initializer":_kernel_initializer,
                 "kernel_regularizer":_kernel_regularizer }
    
    base_conv1      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
    base_conv2      = Conv2D(_relation_size  ,(1,1),activation="linear",**convParam)
    base_conv3      = Conv2D(_out_filter_size,(1,1),activation="linear",**convParam)
    if _satype == PAIRWISE:
        pc          = Conv2D(2,(1,1),activation="linear",**convParam)

    share_size      = min(8,int(math.floor(math.sqrt(_out_filter_size))))
    attention_nrom1 = BatchNormalization()
    attention_conv1 = Conv2D(_out_filter_size//share_size,(1,1),activation=activation,**convParam)
    attention_nrom2 = BatchNormalization()
    attention_conv2 = Conv2D(_out_filter_size            ,(1,1),activation=activation,**convParam)
    
    def SALayerImple(_inputLayer):
        
        input_shapes = list(_inputLayer.shape)
    
        if _data_format == "NHWC":
            strides   = [1,_strides,_strides,1]
            dilations = [_dilations,_dilations]
            h,w,c     = input_shapes[1:]
        else:
            strides   = [1,1,_strides,_strides]
            dilations = [_dilations,_dilations]
            c,h,w     = input_shapes[1:]

        if _function is None:
            if _satype == PAIRWISE:
                usefunction = lambda x,y:tf.subtract(x,y)
            else:
                usefunction = lambda x,y:tf.concat([x,y],-1)
        else:
            usefunction = _function


        if _satype == PAIRWISE:
            serialTile_xi1 = serialTile(_kernel_size**2)
            if _strides > 1:
                strides_xi1    = unfold(1,_strides,1,_data_format)
            else:
                strides_xi1    = lambda x:x

            refpad_x2      = refpad(_kernel_size,_dilations)
            xixj_x2        = depthwise_patches(_kernel_size,_strides,_dilations,_data_format)

            reshape_ax     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_relation_size])

            pobase        = makePositionMap(w,h)

    #             channelTile_po = channelTile(_kernel_size**2)
    #             refpad_po      = refpad(_kernel_size,_dilations)
    #             po2poj         = depthwise_patches(_kernel_size,1,_dilations,_data_format)


            channelTile_poi = channelTile(_kernel_size**2)
            refpad_poj      = refpad(_kernel_size,_dilations)
            pf              = makeIdentityFilter(_kernel_size,2,mode="kc")
            unfold_poj      = lambda poj:tf.nn.depthwise_conv2d(poj,pf,[1,1,1,1],"VALID",_data_format,dilations)


            strides_po     = unfold(1,_strides,1,_data_format)
            kcsplit_po     = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,2])

        def pairwiseModule(_x):

            # xi の生成 [ n , h , w , c*k**2 ]
            x1  = base_conv1(_x)
            xi1 = serialTile_xi1(x1)
            xi1 = strides_xi1(xi1)

            # xj の生成 [ n , h , w , k**2*c ]
            x2  = base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = xixj_x2(x2)

            # xiとxjのペアを加工 [ n , h , w , c*k**2 ]
            ax  = usefunction(xi1,xj2)

            # 座標組み込みの為に変形 [ n , h*w , k**2 , c ]
            ax  = reshape_ax(ax)

            # 座標コード の生成 [ 1 , h , w , k**2 , 2 ]
            po  = pc(pobase)
            poi = channelTile_poi(po)
            poj = refpad_poj(poi)
            poj = unfold_poj(poj)
            po  = tf.subtract(poi,poj)
            # [ 1 , h , w , k**2*2 ]となっているため、axに合わせて nを増やす [ n , h , w , k**2*2 ]
            n   = tf.shape(ax)[0]
            po  = tf.tile(po,[n,1,1,1],name="batchtile")
            po  = strides_po(po)
            po  = kcsplit_po(po)

            axp = tf.concat([ax,po],axis=-1)
            return axp

        if _satype == PATCHWISE:
            if _strides != 1:
                strides_x1 = unfold(1,_strides,_dilations)
            else:
                strides_x1 = lambda x:x
            reshape_x1  = MyReshapeLayer([h*w//_strides**2,1,_relation_size])

            refpad_x2   = refpad(_kernel_size,_dilations)
            unfold_x2   = unfold(_kernel_size,_strides,_dilations)
            reshape_xj2 = MyReshapeLayer([h*w//_strides**2,1,_kernel_size**2*_relation_size])

        def patchwiseModule(_x):

            x1  = base_conv1(_x)
            x1  = strides_x1(x1)
            x1  = reshape_x1(x1)

            x2  = base_conv2(_x)
            x2  = refpad_x2(x2)
            xj2 = unfold_x2(x2)
            xj2 = reshape_xj2(xj2)

            ax  = usefunction(x1,xj2)

            return ax

        if _satype == PATCHWISE:
            samodule      = patchwiseModule
            serialTile_ax = serialTile(_kernel_size**2)
            reshape_ax    = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
            def patches_ax(ax):
                ax = serialTile_ax(ax)
                ax = reshape_ax(ax)
                return ax
        else:
            samodule   = pairwiseModule
            patches_ax = lambda x:x

        zeropad_x3  = zeropad(_kernel_size,_dilations)
        x2xj_x3     = depthwise_patches(_kernel_size,_strides,_dilations,_data_format)

        reshape_xj3 = MyReshapeLayer([h*w//_strides**2,_kernel_size**2,_out_filter_size])
        reshape_abx = MyReshapeLayer([h//_strides,w//_strides,_out_filter_size])


        x   = _inputLayer
        x3  = base_conv3(x)
        x3  = zeropad_x3(x3)
        xj3 = x2xj_x3(x3)
        xj3 = reshape_xj3(xj3)

        ax  = samodule(x)
        ax  = attention_nrom1(ax)
        ax  = attention_conv1(ax)
        ax  = attention_nrom2(ax)
        ax  = attention_conv2(ax)
        ax  = patches_ax(ax)
        aw  = tf.nn.softmax(ax)

        abx = tf.multiply(aw,xj3)
        abx = tf.reduce_sum(abx,-2)
        abx = reshape_abx(abx)
        return abx
    return SALayerImple
