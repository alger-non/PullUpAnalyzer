import cv2
import argparse
from os import walk
import os
from PoseProcessor import PoseProcessor
from VideoProcessor import VideoProcessor



def extract_data_from_dir(dir_name):
    file_names = []
    dir_names = []
    for root, d_names, f_names in walk(dir_name):
        file_names.append(os.path.join(root, f_names[0]))
        dir_names.append(os.path.join(root, d_names[0]))
        break
    return file_names[0], dir_names[0]


parser = argparse.ArgumentParser()
parser.add_argument('input_dir', help='directory containing source video and json data directory')
parser.add_argument('output_dir', help='directory in which will be saved the final video')
args = parser.parse_args()
input_source, json_dir = extract_data_from_dir(args.input_dir)
output_dir = args.output_dir


pose_processor = PoseProcessor(30, 10, 5, 1 / 2)


cap = cv2.VideoCapture(input_source)
filename = os.path.basename(input_source).split('.')[0]
cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
output_video = os.path.join(output_dir, f'{filename}_out.avi')

video_writer = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*"FMP4"), 24,
                               (cap_width, cap_height))
required_points = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5, "LElbow": 6,
                   "LWrist": 7, "MidHip": 8, "RHip": 9, "RKnee": 10, "RAnkle": 11, "LHip": 12, "LKnee": 13,
                   "LAnkle": 14, "REar": 17, "LEar": 18}
required_pairs = (['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
                  ['RElbow', 'RWrist'], ['LElbow', 'LWrist'], ['LWrist', 'RWrist'],
                  ['Neck', 'MidHip'],
                  ['MidHip', 'LHip'], ['MidHip', 'RHip'], ['RHip', 'RKnee'], ['LHip', 'LKnee'], ['LKnee', 'LAnkle'],
                  ['RKnee', 'RAnkle'])

video_processor = VideoProcessor(pose_processor, required_points, required_pairs)
video_processor.enable_debug()


for processed_frame in video_processor.process_video_with_raw_data(cap, json_dir):
    cv2.imshow('Processed frame', processed_frame)
    video_writer.write(processed_frame)
    if cv2.waitKey(1) > 0:
        break

video_writer.release()
