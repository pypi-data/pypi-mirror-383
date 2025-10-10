# -*- coding: utf-8 -*-
"""
# --------------------------------------------------------
# @Author : Pan
# @E-mail :
# @Date   : 2025-07-08 14:10:15
# @Brief  :
# --------------------------------------------------------
"""
import cv2
import numpy as np
from pybaseutils import file_utils, image_utils

import cv2

# 打开默认摄像头（0表示第一个摄像头）
rtsp_url = "rtsp://username:password@192.168.1.64:554/stream1"
# cap = cv2.VideoCapture("192.168.2.52livestream")
# cap = cv2.VideoCapture("rtsp://0.0.0.0:8554/")
# cap = cv2.VideoCapture("rtsp://192.168.2.52:8554/")
cap = cv2.VideoCapture("rtsp://admin:dm-ai12345@192.168.2.222")

# 检查摄像头是否成功打开
if not cap.isOpened():
    print("无法打开摄像头")
    exit()

print("按 'q' 键退出")

while True:
    # 读取一帧
    ret, frame = cap.read()

    # 如果读取成功，ret为True
    if not ret:
        print("无法读取帧")
        break

    # 显示帧
    cv2.imshow('Camera', frame)

    # 按'q'键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()