import numpy as np
import cv2
import time
import imageRecognition
import pyautogui

while True:
    printscreen_pil = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(printscreen_pil), cv2.COLOR_RGB2BGR)

    c_frame = image[0:600, 100:1820]
    pnts, t = imageRecognition.predict(c_frame)
    if t is not None:
        cv2.circle(c_frame, t, 6, (0, 255, 0), thickness=5)
    cv2.imshow('a', c_frame)
    cv2.waitKey(1)