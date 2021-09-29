import threading,serial
import time

import tensorflow as tf
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread, QMutex

lock = QMutex()

class Thread_Predict(QThread):
    appendsignal = pyqtSignal(str)
    def __init__(self,v,serialobj,model,ui):
        super(Thread_Predict, self).__init__()
        self.dict_index_to_label = eval('''{'0':'Battery_Harmful','1':'Brokenceramics_Other','2':'Cans_Recyclable','3':'Cigarettebutts_Other','4':'Drug_Harmful','5':'Fruit_Kitchen','6':'Tile_Other','7':'Vegetables_Kitchen','8':'Walterbottles_Recyclable'}''')
        self.model = model
        self.ui = ui
        self.v = v
        self.serialobj = serialobj

    def run(self):
        time.sleep(2)
        prediction = self.model.predict(self.load_preprocess_img(self.v.get_image()))
        pred_id = np.argmax(prediction)
        lock.lock()
        print(self.dict_index_to_label.get(str(pred_id)))
        self.send(self.dict_index_to_label.get(str(pred_id)))
        lock.unlock()

    def send(self,mes):
        resu = mes.split("_")[1]
        print(resu)
        self.serialobj.write("ST{0:0>2d}{1}".format(len(resu),resu).encode())
        time.sleep(1)
        self.serialobj.write("ST{0:0>2d}{1}".format(len(resu),resu).encode())
        self.appendsignal.emit(mes)


    def load_preprocess_img(self,img_decode):
        height = img_decode.shape[0]
        width = img_decode.shape[1]
        if height > width: img_decode = tf.image.pad_to_bounding_box(img_decode, 0, 1, height, height)
        if height < width: img_decode = tf.image.pad_to_bounding_box(img_decode, 1, 0, width, width)
        # print(img_decode.shape[0],img_decode.shape[1])
        img_decode = tf.image.resize_with_crop_or_pad(img_decode, 299, 299)
        img_decode = tf.cast(img_decode, tf.float32)
        img_decode /= 255
        img_decode = tf.reshape(img_decode, [-1, 299, 299, 3])
        return img_decode

