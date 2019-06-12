import cv2
import time
import numpy as np
import math
import Utils
import os

input_source = "test_videos/video2.mp4"
filename = os.path.basename(input_source).split('.')[0]

protoFile, weightsFile = Utils.set_model("MPI")
POSE_PAIRS = [['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
              ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist']]

interesting_points = {"Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6, "LWrist": 7}

inWidth = 368
inHeight = 368
threshold = 0.1
angle_threshold = 30

cap = cv2.VideoCapture(input_source)

states = ['hanging on straight arms', 'подъем', 'завершение', 'опускание']
cur_state = None

hasFrame, frame = cap.read()
if not hasFrame:
    raise Exception("Video isn't found")
vid_writer = cv2.VideoWriter(f'test_videos_output/{filename}_out.avi', cv2.VideoWriter_fourcc(*"MJPG"), 15,
                             (frame.shape[1], frame.shape[0]))
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

reps = 0



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

    # if cur_state is None:

    for joint, i in interesting_points.items():
        probMap = output[0, i, :, :]
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

    angle_of_left_arm, angle_of_right_arm = math.inf, math.inf

    if Utils.is_arm_points_valid(points['LWrist'], points['LElbow'], points['LShoulder']):
        print(points['LWrist'], points['LElbow'], points['LShoulder'])
        angle_of_left_arm = Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['LWrist'], points['LElbow']),
            Utils.get_vector_from_points(points['LElbow'], points['LShoulder']))
        cv2.putText(frame, f'left arm: {angle_of_left_arm}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                    lineType=cv2.LINE_AA)

    if Utils.is_arm_points_valid(points['RWrist'], points['RElbow'], points['RShoulder']):
        print(points['RWrist'], points['RElbow'], points['RShoulder'])
        angle_of_right_arm = Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['RWrist'], points['RElbow']),
            Utils.get_vector_from_points(points['RElbow'], points['RShoulder']))
        cv2.putText(frame, f'right arm: {angle_of_right_arm}', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                    lineType=cv2.LINE_AA)

    line_color = (0, 255, 255)
    if angle_of_left_arm < angle_threshold and angle_of_right_arm < angle_threshold:
        cv2.putText(frame, f'{states[0]}', (600, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4,
                    lineType=cv2.LINE_AA)
        line_color = (0, 255, 0)
    # Draw Skeleton
    for pair in POSE_PAIRS:
        partA = pair[0]
        partB = pair[1]

        if points[partA] and points[partB]:
            cv2.line(frame, points[partA], points[partB], line_color, 3, lineType=cv2.LINE_AA)
            cv2.circle(frame, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.circle(frame, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    cv2.putText(frame, "time taken = {:.2f} sec".format(time.time() - t), (10, 50), cv2.FONT_HERSHEY_COMPLEX, .8,
                (255, 50, 0), 2, lineType=cv2.LINE_AA)

    cv2.imshow('Output-Skeleton', frame)

    vid_writer.write(frame)

vid_writer.release()
