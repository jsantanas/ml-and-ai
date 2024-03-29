'''
This U-Net model based on residual nets was created under the architecture proposed 
in the paper "Segmenting nailfold capillaries using an improved U-Net network".
'''

import tensorflow as tf
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tensorflow.keras.optimizers as opts
import tensorflow.keras.regularizers as regs
import numpy as np
import os

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input,InputLayer,Conv2D,Conv2DTranspose,\
                                    MaxPooling2D,BatchNormalization,Dropout,\
                                    Dense,CenterCrop,Layer,Concatenate,\
                                    Activation
from tensorflow.keras.callbacks import ModelCheckpoint,EarlyStopping,ReduceLROnPlateau,Callback

# Residual block
def ResNet(input):
  r1 = Conv2D(input.shape[3],(3,3),padding='same')(input)
  r1 = BatchNormalization()(r1)
  r1 = Activation('relu')(r1)
  r2 = Conv2D(input.shape[3],(3,3),padding='same')(r1)
  r2 = BatchNormalization()(r2)
  r2 = Activation('relu')(r2)
  out = input + r2
  return out

# Encoder model
def cmodel(input_layer,num_filters):
  cm1 = ResNet(input_layer)
  cm1 = Conv2D(num_filters,(3,3),activation='relu',padding='same')(cm1)
  cm2 = ResNet(cm1)
  cm2 = Conv2D(num_filters,(3,3),activation='relu',padding='same')(cm2)
  out = MaxPooling2D((2,2))(cm2)
  return out,cm2

# Decoder model
def emodel(input_layer,concat_layer,num_filters):
  em1 = Conv2DTranspose(num_filters,(2,2),(2,2),padding='same')(input_layer)
  em2 = tf.concat([concat_layer,em1],3)
  em3 = ResNet(em2)
  em3 = Conv2D(num_filters,(3,3),activation='relu',padding='same')(em3)
  em4 = ResNet(em3)
  out = Conv2D(num_filters,(3,3),activation='relu',padding='same')(em4)
  return out

# U-Net
# Encoder
in_layer = Input((256,256,3))
x,t0 = cmodel(in_layer,64)
x,t1 = cmodel(x,128)
x,t2 = cmodel(x,256)
x,t3 = cmodel(x,512)
x = Conv2D(1024,(3,3),activation='relu',padding='same')(x)
x = Conv2D(1024,(3,3),activation='relu',padding='same')(x)

# Decoder
x = emodel(x,t3,512)
x = emodel(x,t2,256)
x = emodel(x,t1,128)
x = emodel(x,t0,64)
out_layer = Conv2D(1,(1,1),activation='sigmoid',padding='same')(x)  #switch back filters to 2

unet = Model(inputs=in_layer,outputs=out_layer)
unet.summary()
