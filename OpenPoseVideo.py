import cv2
import time
import numpy as np
import math
import Utils
import os
from PoseProcessor import PoseProcessor
from Drawer import Drawer


drawer = Drawer()
poseProcessor = PoseProcessor()
input_source = "test_videos/video2.mp4"
filename = os.path.basename(input_source).split('.')[0]

protoFile, weightsFile = Utils.set_model('MPI')
POSE_PAIRS = [['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
              ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist']]

interesting_points = {"Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6, "LWrist": 7}

inWidth = 368
inHeight = 368
threshold = 0.1
angle_threshold = 30

cap = cv2.VideoCapture(input_source)

hasFrame, frame = cap.read()
if not hasFrame:
    raise Exception("Video isn't found")
vid_writer = cv2.VideoWriter(f'test_videos_output/{filename}_out.avi', cv2.VideoWriter_fourcc(*"MJPG"), 15,
                             (frame.shape[1], frame.shape[0]))
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

while cv2.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()

    if not hasFrame:
        cv2.waitKey()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()

    H = output.shape[2]
    W = output.shape[3]
    points = {}

    for joint, i in interesting_points.items():
        probMap = output[0, i, :, :]
        _, prob, _, point = cv2.minMaxLoc(probMap)

        if prob > threshold:
            x = int((frameWidth * point[0]) / W)
            y = int((frameHeight * point[1]) / H)
            cv2.circle(frame, (x, y), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frame, "{}".format(i), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)
            points[joint] = (x, y)
        else:
            points[joint] = None

    drawer.draw_skeleton(frame, points, POSE_PAIRS)

    cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (10, 50), cv2.FONT_HERSHEY_COMPLEX, .8,
                (255, 50, 0), 2, lineType=cv2.LINE_AA)

    cv2.imshow('Output-Skeleton', frame)
    vid_writer.write(frame)

vid_writer.release()
