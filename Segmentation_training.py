from __future__ import print_function
import os
import datetime
import numpy as np
from keras.models import Model
from keras.layers import Input, concatenate, Conv2D, MaxPooling2D, Conv2DTranspose, AveragePooling2D, Dropout, \
    BatchNormalization
from keras.optimizers import Adam
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.callbacks import ModelCheckpoint
from keras import backend as K
from keras.layers.advanced_activations import LeakyReLU, ReLU
import cv2

PIXEL = 1024
BATCH_SIZE = 3
lr = 0.001
EPOCH = 1
X_CHANNEL = 3  # 训练样本的通道数
Y_CHANNEL = 3  # 标签图片的通道数
X_NUM = 1800  #

pathX = 'F:\\psx\\2\\'
pathY = 'F:\\psx\\4\\'


def generator(pathX, pathY, batch_size):
    while 1:
        X_train_files = os.listdir(pathX)
        Y_train_files = os.listdir(pathY)
        a = (np.arange(0, X_NUM))
        #cnt = 0
        X = []
        Y = []
        for i in range(batch_size):
            index = np.random.choice(a)
            img = cv2.imread(pathX + X_train_files[index], 1)
            #img = img / 255  # normalization
            img = np.array(img).reshape(PIXEL, PIXEL, X_CHANNEL)
            X.append(img)
            img1 = cv2.imread(pathY + Y_train_files[index], 1)
            #img1 = img1 / 255  # normalization
            img1 = np.array(img1).reshape(PIXEL, PIXEL, Y_CHANNEL)
            Y.append(img1)
            #cnt += 1

        X = np.array(X)
        Y = np.array(Y)
        yield X, Y
        X = []
        Y = []


inputs = Input((PIXEL, PIXEL, 3))
conv1 = Conv2D(8, 3, activation='relu', padding='same', kernel_initializer='he_normal')(inputs)
pool1 = AveragePooling2D(pool_size=(2, 2))(conv1)  # 16

conv2 = BatchNormalization(momentum=0.99)(pool1)
conv2 = Conv2D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
conv2 = BatchNormalization(momentum=0.99)(conv2)
conv2 = Conv2D(32, 1, activation='relu', padding='same', kernel_initializer='he_normal')(conv2)
conv2 = Dropout(0.02)(conv2)
pool2 = AveragePooling2D(pool_size=(2, 2))(conv2)  # 8

conv3 = BatchNormalization(momentum=0.99)(pool2)
conv3 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
conv3 = BatchNormalization(momentum=0.99)(conv3)
conv3 = Conv2D(32, 1, activation='relu', padding='same', kernel_initializer='he_normal')(conv3)
conv3 = Dropout(0.02)(conv3)
pool3 = AveragePooling2D(pool_size=(2, 2))(conv3)  # 4

conv4 = BatchNormalization(momentum=0.99)(pool3)
conv4 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
conv4 = BatchNormalization(momentum=0.99)(conv4)
conv4 = Conv2D(32, 1, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
conv4 = Dropout(0.02)(conv4)
pool4 = AveragePooling2D(pool_size=(2, 2))(conv4)

conv5 = BatchNormalization(momentum=0.99)(pool4)
conv5 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
conv5 = BatchNormalization(momentum=0.99)(conv5)
conv5 = Conv2D(32, 1, activation='relu', padding='same', kernel_initializer='he_normal')(conv5)
conv5 = Dropout(0.02)(conv5)
pool4 = AveragePooling2D(pool_size=(2, 2))(conv4)
# conv5 = Conv2D(35, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv4)
# drop4 = Dropout(0.02)(conv5)
pool4 = AveragePooling2D(pool_size=(2, 2))(pool3)  # 2
pool5 = AveragePooling2D(pool_size=(2, 2))(pool4)  # 1

conv6 = BatchNormalization(momentum=0.99)(pool5)
conv6 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)

conv7 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv6)
up7 = (UpSampling2D(size=(2, 2))(conv7))  # 2
conv7 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(up7)
merge7 = concatenate([pool4, conv7], axis=3)

conv8 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge7)
up8 = (UpSampling2D(size=(2, 2))(conv8))  # 4
conv8 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(up8)
merge8 = concatenate([pool3, conv8], axis=3)

conv9 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge8)
up9 = (UpSampling2D(size=(2, 2))(conv9))  # 8
conv9 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(up9)
merge9 = concatenate([pool2, conv9], axis=3)

conv10 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(merge9)
up10 = (UpSampling2D(size=(2, 2))(conv10))  # 16
conv10 = Conv2D(32, 3, activation='relu', padding='same', kernel_initializer='he_normal')(up10)

conv11 = Conv2D(16, 3, activation='relu', padding='same', kernel_initializer='he_normal')(conv10)
up11 = (UpSampling2D(size=(2, 2))(conv11))  # 32
conv11 = Conv2D(8, 3, activation='relu', padding='same', kernel_initializer='he_normal')(up11)

conv12 = Conv2D(3, 1, activation='relu', padding='same', kernel_initializer='he_normal')(conv11)

model = Model(input=inputs, output=conv12)
model.compile(optimizer=Adam(lr=1e-3), loss='mse', metrics=['accuracy'])

history = model.fit_generator(generator(pathX, pathY, BATCH_SIZE),
                              steps_per_epoch=600, nb_epoch=EPOCH)

end_time = datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')
model.save(r'F:\psx\segmentation\V1_828.h5')

mae = np.array((history.history['loss']))
np.save(r'F:\psx\segmentation\V1_828.npy', mae)