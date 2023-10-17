import cv2 as cv
from time import sleep
import os
import matplotlib
from collections import deque
matplotlib.use('Agg')

d = deque(maxlen=30)
def faceRecognition(dirPath) -> int:
    # 加载训练数据集
    recognizer = cv.face.LBPHFaceRecognizer_create()
    recognizer.read(os.path.join(dirPath,'facerecognition_opencv/model.yml'))

    # 识别电脑摄像头并打开
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)
    # 创建一个级联分类器 加载一个.xml分类器文件 它既可以是Haar特征也可以是LBP特征的分类器
    face_detect = cv.CascadeClassifier(os.path.join(dirPath,'haarcascades/haarcascade_frontalface_default.xml'))

    # lables = [0]


    cap.open(0)
    if cap.isOpened():
        # i = 0
        # while i < 30:
        while True:
            print("==============================")
            # print(i)
            sleep(0.1)
            # 读取视频片段
            flag, frame = cap.read()
            frame = cv.flip(frame, 1)
            if not flag:  # 读完视频后falg返回False
                break
            # 灰度处理
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # 多个尺度空间进行人脸检测   返回检测到的人脸区域坐标信息
            face_zone = face_detect.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            # 绘制矩形和圆形检测人脸
            for x, y, w, h in face_zone:
                cv.rectangle(frame, pt1=(x, y), pt2=(x + w, y + h), color=[0, 0, 255], thickness=2)
                cv.circle(frame, center=(x + w // 2, y + h // 2), radius=w // 2, color=[0, 255, 0], thickness=2)

            label, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            print(
                """
                Label：%d
                Confidence：%d
                """ % (label, confidence)
            )

            # lables.append(int(label))
            d.append(int(label))
            # if confidence > 60:
            #     if label == 1:
            #         print("Obama")
            #         print("图片标签：", str(label))
            #         print("可信度：", str(confidence))
            #     elif label == 2:
            #         print("Eric")
            #         print("图片标签：", str(label))
            #         print("可信度：", str(confidence))
            # else:
            #     print("未匹配到数据")

            # 显示图片
            # cv.imshow('video', frame)
            # i += 1
            # 设置退出键q 展示频率
            # if ord('q') == cv.waitKey(30):
            #     break

    # 释放资源
    # cap.release()
    # cv.destroyAllWindows()

    # id = max(set(d) , key=d.count)
    # print("""出现最多的为""" + str(id))
    #
    # return id

def getRecent3sUser():
    return max(set(d) , key=d.count)