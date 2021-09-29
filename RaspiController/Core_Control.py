import cv2,serial,time
import Thread_Predict
import tensorflow as tf

def acc_top3(y_true, y_pred):
    return tf.keras.metrics.sparse_top_k_categorical_accuracy(y_true, y_pred, k=3)
def acc_top5(y_true, y_pred):
    return tf.keras.metrics.sparse_top_k_categorical_accuracy(y_true, y_pred, k=5)
def loadmodel(path):
    # 加载模型
    model = tf.keras.models.load_model(path, compile=True,
                                       custom_objects={'acc_top3': acc_top3,
                                                       'acc_top5': acc_top5})
    # 编译模型
    return model
cap = cv2.VideoCapture(0)
serialobj = serial.Serial("COM5")
model = loadmodel("weight/epoch-56-val_acc-0.9621-acc_top3-1.0000-acc_top5-1.0000.h5")
while(True):
    ret,frame = cap.read()
    cv2.imshow('frame',frame)
    if cv2.waitKey(1)&0xFF==ord('q'):
        break
    else:
        data = serialobj.read_all().decode()
        if data!="c":
            continue
        else:
            t = Thread_Predict.Thread_Predict(frame, serialobj, model)
            t.start()
            time.sleep(0.02)
cap.release()
cv2.destroyAllWindows()
