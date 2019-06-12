import cv2
import time
import numpy as np
import math
import Utils
import os
from PoseProcessor import PoseProcessor
from Drawer import Drawer
import pickle

drawer = Drawer()
poseProcessor = PoseProcessor()
input_source = "test_videos/video2.mp4"
filename = os.path.basename(input_source).split('.')[0]

POSE_PAIRS = [['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
              ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist']]

interesting_points = {"Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6, "LWrist": 7}

inWidth = 368
inHeight = 368
threshold = 0.1

cap = cv2.VideoCapture(input_source)

ready_date_filename = 'test_videos/video2_MPI'
ready_data = open(ready_date_filename, 'rb')

cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

vid_writer = cv2.VideoWriter(f'test_videos_output/{filename}_out.avi', cv2.VideoWriter_fourcc(*"MJPG"), 15,
                             (cap_width, cap_height))

while cv2.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()

    if not hasFrame:
        break

    frame_matrix = pickle.load(ready_data)

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    H = frame_matrix.shape[2]
    W = frame_matrix.shape[3]
    points = {}

    for joint, i in interesting_points.items():
        probMap = frame_matrix[0, i, :, :]
        _, prob, _, point = cv2.minMaxLoc(probMap)
        x = (frameWidth * point[0]) / W
        y = (frameHeight * point[1]) / H

        if prob > threshold:
            cv2.circle(frame, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frame, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)
            points[joint] = (int(x), int(y))
        else:
            points[joint] = None

    poseProcessor.define_state(points, frame)
    drawer.draw_skeleton(frame, points, POSE_PAIRS)
    cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (10, 50), cv2.FONT_HERSHEY_COMPLEX, .8,
                (255, 50, 0), 2, lineType=cv2.LINE_AA)

    cv2.imshow('Output-Skeleton', frame)

    vid_writer.write(frame)

vid_writer.release()
