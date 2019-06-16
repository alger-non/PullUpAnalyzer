import cv2
import sys
import Utils
import os
from PoseProcessor import PoseProcessor
from Drawer import Drawer
import pickle
from VideoProcessor import VideoProcessor

pose_processor = PoseProcessor(30, 5, 1 / 5)
input_source = "test_videos/Girl720.mp4"
raw_data = 'test_videos/video2_MPI'
cap = cv2.VideoCapture(input_source)
filename = os.path.basename(input_source).split('.')[0]
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
net = cv2.dnn.readNetFromCaffe(*Utils.get_model_by_name('MPI'))
video_writer = cv2.VideoWriter(f'test_videos_output/{filename}_out.avi', cv2.VideoWriter_fourcc(*"MJPG"), 15,
                               (cap_width, cap_height))
required_points = {"Head": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6,
                 "LWrist": 7}
required_pairs = (['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
                  ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist'], ['Head', 'Neck'])

video_processor = VideoProcessor(pose_processor, required_points, required_pairs)
video_processor.enable_debug()

for processed_frame in video_processor.process_video_with_net(cap, net):
    cv2.imshow('Processed frame', processed_frame)
    video_writer.write(processed_frame)
    if cv2.waitKey(1) > 0:
        break

video_writer.release()
