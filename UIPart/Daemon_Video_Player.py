import threading
import time
import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import tensorflow as tf

class Video_Player(QObject):
    predictSignal = pyqtSignal()
    def __init__(self,Qlabel,path = 0):
        super(Video_Player, self).__init__()
        self._lock = threading.Lock()
        self.Qlabel = Qlabel
        self.cap = None
        self.is_img_thread_run = True
        self.path = path
        self.is_dector_run = False
        self.template = None
    def updatetemplate(self):
        image = self.get_image()
        self.template = tf.image.resize(tf.convert_to_tensor(image, dtype=tf.uint8), [8, 8])
    def open_cv(self):

        self.cap = cv2.VideoCapture(self.path)
        if self.path == 0:
            self.updatetemplate()
        if not self.cap.isOpened():
            return False
        else:
            self.__start_thread()
            return True
    def get_image(self):
        return next(self.image_generator())

    def image_generator(self):
        with self._lock:
            ret, image = self.cap.read()
        if ret != False:
            image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            yield image
        else:
            if self.is_img_thread_run:
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.path)
                else:
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.path)

    def toggle_playmode(self,path=0):
        self.path = path
        self.destroy()
        self.open_cv()

    def load_image(self,ima):
        width = ima.shape[1]
        height = ima.shape[0]
        q_image = QImage(ima.data, width, height, width * 3, QImage.Format_RGB888)
        n_width = q_image.width()
        n_height = q_image.height()
        if n_width / 470 >= n_height / 320:
            ratio = n_width / 470
        else:
            ratio = n_height / 320
        new_width = n_width / ratio
        new_height = n_height / ratio
        new_img = q_image.scaled(int(new_width), int(new_height), Qt.KeepAspectRatio)
        return QPixmap.fromImage(new_img)
    def detect(self,image):
        image = tf.image.resize(tf.convert_to_tensor(image, dtype=tf.uint8), [8,8])
        p = tf.image.psnr(self.template,image,max_val=255).numpy()
        if p < 20:
            self.predictSignal.emit()
            self.is_dector_run = False
    def video_player(self):
        while self.is_img_thread_run:
            try:
                ima = next(self.image_generator())
                self.Qlabel.setPixmap(self.load_image(ima))
                if self.is_dector_run:
                    if not type(ima) == "NoneType":
                        self.detect(ima)
            except Exception as e:
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.path)
                else:
                    self.cap.release()
                    self.cap = cv2.VideoCapture(self.path)
            time.sleep(0.05)
    def __start_thread(self):
        self.is_img_thread_run = True
        t = threading.Thread(target=self.video_player)
        t.start()

    def destroy(self):
        self.is_img_thread_run  = False
        time.sleep(0.2)
        if not self.cap ==None:
            self.cap.release()
