import cv2
import time
import numpy as np
import sys
import Utils
import os
from PoseProcessor import PoseProcessor
from Drawer import Drawer


drawer = Drawer()
poseProcessor = PoseProcessor()
input_source = "test_videos/video2.mp4"
filename = os.path.basename(input_source).split('.')[0]
protoFile, weightsFile = Utils.set_model('MPI')


needed_points = {"Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6, "LWrist": 7}

inWidth = 368
inHeight = 368
threshold = 0.1
angle_threshold = 30

cap = cv2.VideoCapture(input_source)

cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
vid_writer = cv2.VideoWriter(f'test_videos_output/{filename}_out.avi', cv2.VideoWriter_fourcc(*"MJPG"), 15,
                             (cap_width, cap_height))
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

while cv2.waitKey(1) < 0:
    t = time.time()
    hasFrame, frame = cap.read()

    if not hasFrame:
        break

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                    (0, 0, 0), swapRB=False, crop=False)
    net.setInput(inpBlob)
    output = net.forward()
    points = Utils.extract_body_joints_points(output, (cap_width, cap_height), needed_points, threshold)
    drawer.draw_numbered_joints(frame, points, needed_points)
    drawer.draw_skeleton(frame, points, Utils.POSE_PAIRS)
    drawer.print_message(frame, f'time taken = {time.time() - t:0.3} sec', 10, 50)
    cv2.imshow('Output-Skeleton', frame)
    vid_writer.write(frame)

vid_writer.release()
