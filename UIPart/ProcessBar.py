import sys
import threading
import math
import time

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget

lock = threading.Lock()
class RoundProgress(QWidget):

    def __init__(self):
        super(RoundProgress, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)  # 去边框
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.persent = 0
        self.color = "#20a53a"
        # self.t = Thread_Updata()
        # self.t.mysignal.connect(self.parameterUpdateReal)



    def  __parameterUpdateReal(self, p):
        lock.acquire()
        distance = math.floor(p) - math.ceil(self.persent) if p >= self.persent else math.floor(self.persent) - math.ceil(p)
        for i in range(distance):
            if p >= self.persent:
                self.persent+=1
            else:
                self.persent-=1
            self.update()
            time.sleep(0.02)
        lock.release()

    def parameterUpdate(self,p):
        threading.Thread(target=lambda :self.__parameterUpdateReal(p)).start()


    def paintEvent(self, event):
        rotateAngle = 360 * self.persent / 100
        # 绘制准备工作，启用反锯齿
        painter = QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)

        painter.setPen(QtCore.Qt.NoPen)

        painter.setBrush(QBrush(QColor("#cccccc")))
        painter.drawEllipse(3, 3, 100, 100)  # 画外圆

        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.drawEllipse(13, 13, 80, 80)  # 画内圆
        if self.persent>=0 and self.persent<=50:
            color = "#20a53a"
        elif self.persent>50 and self.persent<=80:
            color = "#ff9900"
        else:
            color = "#FF0033"
        self.pen = QPen()
        self.pen.setBrush(QBrush(QColor(color)))  # 设置画刷渐变效果
        self.pen.setWidth(10)
        self.pen.setCapStyle(Qt.RoundCap)
        painter.setPen(self.pen)
        painter.drawArc(QtCore.QRectF(8,8 , 90, 90), (90 - 0) * 16, -rotateAngle * 16)  # 画圆环

        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(QColor("#5481FF"))
        painter.drawText(QtCore.QRectF(4, 4, 98, 98), Qt.AlignCenter, "%d%%" % self.persent)  # 显示进度条当前进度

