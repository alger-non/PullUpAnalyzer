import cv2
import sys
import Utils
import os
from PoseProcessor import PoseProcessor
from Drawer import Drawer
import pickle

drawer = Drawer()
pose_processor = PoseProcessor(30, 5, 1 / 5)
input_source = "test_videos/video2.mp4"
filename = os.path.basename(input_source).split('.')[0]
needed_points = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6,
                 "LWrist": 7}
POSE_PAIRS = (['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
              ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist'], ['Head', 'Neck'])

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
    hasFrame, frame = cap.read()
    if not hasFrame:
        break
    frame_matrix = pickle.load(ready_data)
    points = Utils.extract_body_joints_points(frame_matrix, (cap_width, cap_height), needed_points, threshold)
    if not pose_processor.define_state(points):
        drawer.print_message(frame, f'Failed state detection attempt', 10, 200)
    if pose_processor.chin_point:
        drawer.draw_point(frame, pose_processor.chin_point, Drawer.BLUE_color, 8)
    drawer.draw_numbered_joints(frame, points, needed_points)
    drawer.draw_skeleton(frame, points, POSE_PAIRS)
    drawer.print_message(frame, f'left arm angle: {pose_processor.left_arm_angle}', 10, 50)
    drawer.print_message(frame, f'right arm angle: {pose_processor.right_arm_angle}', 10, 90)
    drawer.print_message(frame, f'wrists levels angle: {pose_processor.wrists_level_angle}', 10, 130)
    drawer.print_message(frame, f'repeats: {pose_processor.repeats}', 10, 170)
    drawer.print_message(frame, f'current state: {pose_processor.cur_state}', 10, frame.shape[0] - 20)
    cv2.imshow('Output-Skeleton', frame)

    vid_writer.write(frame)

vid_writer.release()
