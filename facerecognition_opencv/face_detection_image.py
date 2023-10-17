import cv2 as cv


def face_detection(image):
	# 转成灰度图像
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # 创建一个级联分类器 加载一个.xml分类器文件 它既可以是Haar特征也可以是LBP特征的分类器
    face_detecter = cv.CascadeClassifier(r'../haarcascades/haarcascade_frontalface_default.xml')
    # 多个尺度空间进行人脸检测   返回检测到的人脸区域坐标信息
    faces = face_detecter.detectMultiScale(image=gray, scaleFactor=1.1, minNeighbors=5)
    print('检测人脸信息如下：\n', faces)
    for x, y, w, h in faces:
        # 在原图像上绘制矩形标识
        cv.rectangle(img=image, pt1=(x, y), pt2=(x+w, y+h), color=(0, 0, 255), thickness=2)
    cv.imshow('result', image)


src = cv.imread(r'../data/1/obama2.jpg')
cv.imshow('input image', src)
face_detection(src)
cv.waitKey(0)
cv.destroyAllWindows()