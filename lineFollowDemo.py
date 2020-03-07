import imageRecognition
import serial
import cv2
import time

VIDEO_CAPTURE_DEVICE = 2
imageRecognition.RESOLUTION = 10
ser = serial.Serial("/dev/ttyACM0")

cap = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE)
pv = "3060"
tp = "3060"
try:
    while True:
        # TODO: Make turning curves. Bot too sensitive.
        # TODO: Finish preparing raspberry pi (discord might help) test
        ret, frame = cap.read()
        if frame is None:
            exit()
        c_frame = frame[70:400, 5:1280]
        nav_mesh, t, a, o = imageRecognition.predict(c_frame)
        if nav_mesh:
            if t:
                cv2.circle(c_frame, nav_mesh[t], 6, (0, 255, 0), thickness=5)
                if nav_mesh[t][1] < (c_frame.shape[0] / 5) and a < 50:
                    if nav_mesh[t + 1][0] > nav_mesh[t][0]:
                        tp = "6933"
                    else:
                        tp = "6339"
                    cv2.imshow('vision', c_frame)
                    cv2.waitKey(1)
                    continue

            if nav_mesh[0][0] < c_frame.shape[1] / 4 and a < 50:
                tp = "6339"
                print("right")
            elif nav_mesh[0][0] > c_frame.shape[1] / 4 * 3 and a < 50:
                tp = "6933"
                print("left")
            elif a > 10 and o == "left":
                tp = "6339"
                print("right")
            elif a > 10 and o == "right":
                tp = "6933"
                print("left")
            else:
                tp = "3969"
                print("ok")
            prev = nav_mesh[0]
            for point in nav_mesh:
                cv2.circle(c_frame, point, 3, (0, 0, 255), thickness=3)
                cv2.line(c_frame, prev, point, (0, 0, 255), 2)
                prev = point
        else:
            tp = "3060"

        if tp != pv:
            ser.write(tp.encode())
            pv = tp

        # show the final output image
        cv2.imshow('vision', c_frame)
        cv2.waitKey(1)
except KeyboardInterrupt:
    print("finish")
    ser.write("3060".encode())
    ser.close()
