"""
Made by Adam Suchý, 2019
for the frankfurt competition in robotics 2020
"""

import logging
import time

import cv2
import numpy as np

# setting constants
TURN_THRESHOLD = 75
RESOLUTION = 15
VIDEO_CAPTURE_DEVICE = 2

# setting up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler("imageRecognition.log")
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logging.Formatter("%(levelname)s %(asctime)s : %(message)s"))
logger.addHandler(fileHandler)


def predict(image: np.ndarray, clean: bool = False):
    """
    A function that takes in an image in BGR format and finds a black line on a white background on the image.
    It detects turns and calculates the angle of the line.

    TODO: Make angle not be relative but absolute (do not rely on sides from the y axis)? Maybe more efficient this way.

    :param image: numpy array of an image in BGR format
    :param clean: Should the function be in the background? if true: image displayed
    :return:
    nav (points of the line),
    turn (the point on the image of the turn (none if not detected),
    angle (angle of the line before any turn),
    ori (orientation of the line. if it goes to the left or right)
    """

    # creating the image of the edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, edges = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    # edges = cv2.Canny(thresh, 100, 200)
    if not clean:
        cv2.imshow('b', edges)  # shows the black and white image mask
        cv2.waitKey(1)
    # creating points
    height = edges.shape[0]
    width = edges.shape[1]
    blocks = int((height - 1) / RESOLUTION)
    nav = list()
    for line in range(0, RESOLUTION):
        points_on_row = []
        for j in range(0, width):
            if edges[(height - 1) - blocks * line, j] != 0:
                points_on_row.append(j)

        if len(points_on_row) == 0:  # continue to next line if no line found
            continue
        else:
            avrg = int(np.average(points_on_row))
        nav.append((avrg, height - blocks * line - 1))

    if len(nav) < 2:
        return [], (0, 0), 0, "right"

    # looking for turns, more accurately: any line which angle is more than TURN_THRESHOLD
    p1 = nav[0]
    turn = None
    for p2 in nav[1:]:
        tan = abs(p1[0] - p2[0]) / abs(p1[1] - p2[1])
        angle = np.arctan(tan) * 57.2957795
        if angle > TURN_THRESHOLD:
            turn = nav.index(p1)
            break
        p1 = p2

    # getting the angle of the line
    p1 = nav[0]
    if turn and abs(p1[1] - nav[turn][1]) != 0:
        p2 = nav[turn]
    else:
        p2 = nav[-1]
    tan = abs(p1[0] - p2[0]) / abs(p1[1] - p2[1])
    angle = np.arctan(tan) * 57.2957795  # converting radians to degrees
    ori = "left"
    if p1[0] <= p2[0]:
        ori = "right"
    return nav, turn, angle, ori


if __name__ == '__main__':
    consoleH = logging.StreamHandler()
    consoleH.setLevel(logging.DEBUG)
    consoleH.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(consoleH)
    logger.info("logging initialized")
    i = cv2.imread('r-l.jpg')
    cap = cv2.VideoCapture(VIDEO_CAPTURE_DEVICE)
    if cap.read()[1] is None:
        logger.warning(f"Cannot read fom video capture device on index {VIDEO_CAPTURE_DEVICE}. Defaulting to 0.")
        cap = cv2.VideoCapture(0)

    logger.debug(predict(i))
    sec = 0
    try:
        while True:
            tp = "Ok"
            ret, frame = cap.read()
            if frame is None:
                logger.critical(f"The video capture device did not output a frame, exiting.")
                exit()
            c_frame = frame[70:400, 5:1280]
            start = time.time()
            pnts, t, a, o = predict(c_frame)
            sec = time.time() - start
            if pnts:
                if t is not None:
                    cv2.circle(c_frame, pnts[t], 6, (0, 255, 0), thickness=5)
                if pnts[0][0] < c_frame.shape[1] / 4:
                    tp = "left"
                elif pnts[0][0] > c_frame.shape[1] / 4 * 3:
                    tp = "right"
                elif a > 10 and o == "left":
                    tp = "left"
                elif a > 10 and o == "right":
                    tp = "right"
                logger.debug(f"Angle:       {a}")
                logger.debug(f"Orientation: {o}")
                logger.debug(f"Turn pred. : {tp}")
                prev = pnts[0]
                for point in pnts:
                    cv2.circle(c_frame, point, 3, (0, 0, 255), thickness=3)
                    cv2.line(c_frame, prev, point, (0, 0, 255), 2)
                    prev = point
            # show the final output image
            cv2.imshow('vision', c_frame)
            cv2.waitKey(1)
    except KeyboardInterrupt:
        print("Finish.")
        logger.info(f"Exit. Last prediction was calculated in {round(sec, 3)} seconds.")
