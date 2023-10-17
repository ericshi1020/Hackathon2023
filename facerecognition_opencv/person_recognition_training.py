import cv2
import os
import numpy

root_path = "../data/"

lables = []
faces = []


def getFacesAndLabels():
    """读取图片特征和标签"""
    global root_path

    # 获取人脸检测器
    face_detector = cv2.CascadeClassifier('../haarcascades/haarcascade_frontalface_default.xml')

    # 获取图片路径
    folders = os.listdir(root_path)
    for folder in folders:
        path = os.path.join(root_path, folder)
        files = os.listdir(path)
        for file in files:
            # 读取图片
            path1 = os.path.join(path, file)
            im = cv2.imread(path1)
            # 转换灰度
            grey = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            # 读取人脸数据
            face = face_detector.detectMultiScale(grey)
            for x, y, w, h in face:
                # 设置标签，分离文件名称
                lables.append(int(folder))
                # 设置人脸数据
                faces.append(grey[y:y + h, x:x + w])

    return faces, lables


# 调用方法获取人脸信息及标签
faces, labels = getFacesAndLabels()
# 获取训练对象
recognizer = cv2.face.LBPHFaceRecognizer_create()
# 训练数据
recognizer.train(faces, numpy.array(labels))
# 保存训练数据
recognizer.write('model.yml')