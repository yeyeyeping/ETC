import os
import sys
import tensorflow as tf
from PyQt5.QtWidgets import QApplication, QMainWindow
from RaspiController.Thread_Predict import Thread_Predict
from SerialPart.SerialManage import DaemonThread
from UIPart.UI_Child import ui_Main
from UIPart.Daemon_Video_Player import Video_Player
count = 0
count_recycle = 0
count_harmful = 0
count_other = 0
count_kitchen = 0
class init():
    def __init__(self,ui,v,videopath):
        self.v =  v
        self.videopath = videopath
        self.ui = ui
        self.daemon = None
        self.v.predictSignal.connect(self.predict)
        self.model = self.loadmodel("./RaspiController/weight/epoch-56-val_acc-0.9621-acc_top3-1.0000-acc_top5-1.0000.h5")
        try:
            self.daemon = DaemonThread()
        except:
            self.ui.textEdit_log.append("串口初始化失败")
        if not self.daemon == None:
            self.daemon.fullLoadRateChange_Signal.connect(self.fullLoadRateChange_slot)
            self.daemon.videoToggle_Signal.connect(self.videoToggle_Signal_slot)
            self.daemon.resultSuccess_Sinal.connect(self.resultSuccess_Sinal_slot)
            if self.daemon.serialobj.is_open:
                self.ui.textEdit_log.append("串口初始化成功")
                self.daemon.start()
        self.garbagetype = ("recycle","other","kitchen","harmful")
    def append_slot(self,s):
        global count
        count+=1
        name = ""
        objname  = s.split("_")[0]
        classname  = s.split("_")[1]
        if classname=="recycle":
            global count_recycle
            count_recycle+=1
            self.ui.label_recyle.setText(str(count_recycle))
            name = "可回收垃圾"
        elif classname=="harmful":
            global count_harmful
            count_harmful+=1
            self.ui.label_harmful.setText(str(count_harmful))
            name = "有害垃圾"
        elif classname=="kitchen":
            global count_kitchen
            count_kitchen+=1
            self.ui.label_kitchen.setText(str(count_kitchen))
            name = "厨余垃圾"
        elif classname=="other":
            global count_other
            count_other+=1
            self.ui.label_other.setText = (str(count_other))
            name = "有害垃圾"
        else:
            return
        label = ""
        if objname == "Battery":
            label = "电池"
        elif objname == "Brokenceramics":
            label = "瓦片"
        elif objname == "Cans":
            label = "易拉罐"
        elif objname == "Cigarettebutts":
            label = "烟头"
        elif objname == "Fruit":
            label = "水果"
        elif objname == "Tile":
            label = "砖头"
        elif objname == "Vegetables":
            label = "蔬菜"
        elif objname == "Walterbottles":
            label = "水瓶"
        else:
            return
        self.ui.textEdit_log.append("第{count:d}次识别,数量1,识别成功,识别结果{label:s}".format(count=count, label=label))

    def predict(self):
        print("收到拍照信号")
        self.t = Thread_Predict(self.v,self.daemon.serialobj,self.model,self.ui)
        self.t.appendsignal.connect(self.append_slot)
        self.t.start()
    def acc_top3(y_true, y_pred):
        return tf.keras.metrics.sparse_top_k_categorical_accuracy(y_true, y_pred, k=3)
    def acc_top5(y_true, y_pred):
        return tf.keras.metrics.sparse_top_k_categorical_accuracy(y_true, y_pred, k=5)
    def loadmodel(self,path):
        # 加载模型
        model = tf.keras.models.load_model(path, compile=True,custom_objects={'acc_top3': init.acc_top3,'acc_top5': init.acc_top5})
        # 编译模型
        return model
    def resultSuccess_Sinal_slot(self):
        if not self.v.path==0:return
        self.v.is_dector_run = True
        self.v.updatetemplate()
    def fullLoadRateChange_slot(self,s1,s2):
        try:
            p = eval(s2)
            if not s1 in self.garbagetype and s2:return
            name = ""
            if s1 == "recycle":
                name = "可回收垃圾"
                self.ui.processbar_recycle.parameterUpdate(p)
            elif s1 == "other":
                name = "其他垃圾"
                self.ui.processbar_other.parameterUpdate(p)
            elif s1 == "kitchen":
                name = "厨余垃圾"
                self.ui.processbar_kitchen.parameterUpdate(p)
            elif s1 == "harmful":
                name = "有害垃圾"
                self.ui.processbar_harmful.parameterUpdate(p)
            else:
                return
            if p >= 95:
                self.ui.textEdit_log.append("警告：" + s1 + "垃圾桶即将满载，请及时更换垃圾袋！")
        except:
            pass
    def videoToggle_Signal_slot(self,s):
        if s == "ON":
            self.v.is_dector_run = False
            if self.v.path == self.videopath:return
            self.ui.label_2.setText("待机中")
            self.v.toggle_playmode(path = self.videopath)
            self.ui.textEdit_log.append("打开宣传视频成功")
        elif s == "OFF":
            self.v.is_dector_run = True
            if self.v.path == 0:return
            self.ui.textEdit_log.append("收到工作信号")
            self.v.toggle_playmode(path=0)
            self.ui.textEdit_log.append("打开相机成功")
            self.ui.label_2.setText("工作中")
        else:
            pass
class Mainwindow(QMainWindow):
    def set(self,v,i):
        self.v = v
        self.i = i
    def closeEvent(self,event) -> None:
        self.v.destroy()
        if self.i.daemon== None:
            return
        self.i.daemon.thread_run = False
        event.accept()
li = sys.argv
if  len(li) == 1:
    print("请指定宣传视频路径")
    exit(1)
elif len(li) == 2:
    if not os.path.exists(li[1]):
        print("视频文件路径错误")
        exit(1)
    app = QApplication(li)
    videopath = li[1]
    ui = ui_Main()
    Mainw = Mainwindow()
    ui.setupUi(Mainw)
    v = Video_Player(ui.label_show,path=videopath)
    if v.open_cv():
        ui.textEdit_log.append("视频加载成功")
    else:
        ui.textEdit_log.append("视频加载失败")
    i = init(ui,v,videopath)
    Mainw.set(v,i)
    Mainw.show()
    sys.exit(app.exec_())
else:
    print("参数格式不正确，命令格式python Start.py 视频路径")