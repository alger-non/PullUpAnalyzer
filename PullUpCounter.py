from PhaseQualifier import PhaseQualifier
from VideoProcessor import VideoProcessor
import cv2
import os
import argparse
from openpose import pyopenpose as op
import time


class PullUpCounter:
    def __init__(self):
        self.input_file = ""
        self.short_input_filename = ""
        self.output_dir = ""
        self.json_dir = ""
        self.use_raw_data = False
        self.cap = None
        self.video_writer = None
        self.required_points = {"Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4, "LShoulder": 5,
                                "LElbow": 6,
                                "LWrist": 7, "MidHip": 8, "RHip": 9, "RKnee": 10, "RAnkle": 11, "LHip": 12, "LKnee": 13,
                                "LAnkle": 14, "REar": 17, "LEar": 18}

        self.required_pairs = (
            ['Neck', 'RShoulder'], ['Neck', 'LShoulder'], ['RShoulder', 'RElbow'], ['LShoulder', 'LElbow'],
            ['RElbow', 'RWrist'], ['LElbow', 'LWrist'],
            ['Neck', 'MidHip'],
            ['MidHip', 'LHip'], ['MidHip', 'RHip'], ['RHip', 'RKnee'], ['LHip', 'LKnee'], ['LKnee', 'LAnkle'],
            ['RKnee', 'RAnkle'])

        self.pose_processor = PhaseQualifier(30, 30, 5, 0.5)
        self.video_processor = VideoProcessor(self.pose_processor, self.required_points, self.required_pairs)
        self.parse_cmd_line()

    def parse_cmd_line(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', help='directory containing source video and json data directory')
        parser.add_argument('output_dir', help='directory in which will be saved the final video')
        parser.add_argument('--use-raw-data', dest='use_raw_data', default=False,
                            help='True or False depending on whether you have json-data in '
                                 'directory with the input video')
        args = parser.parse_args()

        self.use_raw_data = args.use_raw_data
        self.input_file = args.input_file
        self.short_input_filename = os.path.basename(self.input_file).split('.')[0]
        if self.use_raw_data:
            self.json_dir = self.find_json_dir_by_video_name(args.input_file)
            if not self.json_dir:
                raise FileNotFoundError("Json-dir not found in the video's specified directory")
        self.output_dir = args.output_dir

    def find_json_dir_by_video_name(self, filename):
        par_dir = os.path.dirname(filename)
        print(self.short_input_filename)
        possible_json_dir = f'{os.path.join(par_dir, self.short_input_filename)}_json'
        print(possible_json_dir)
        return possible_json_dir if os.path.isdir(possible_json_dir) else None

    def start(self):
        self.cap = cv2.VideoCapture(self.input_file)
        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        output_filename = os.path.join(self.output_dir, f'{self.short_input_filename}_out.avi')
        self.video_writer = cv2.VideoWriter(output_filename, cv2.VideoWriter_fourcc(*"FMP4"), fps,
                                            (cap_width, cap_height))
        if self.use_raw_data:
            self.exec_with_raw_data()
        else:
            self.exec()

    def exec(self):
        params = dict()
        params["model_folder"] = "models/"
        params['number_people_max'] = 1
        params['render_pose'] = 0

        op_wrapper = op.WrapperPython()
        op_wrapper.configure(params)
        op_wrapper.start()

        for processed_frame in self.video_processor.process_video_with_net(self.cap, op_wrapper):
            self.show_processed_frame(processed_frame)
            self.write_frame_to_output(processed_frame)
            if cv2.waitKey(1) > 0:
                break

    def exec_with_raw_data(self):
        for processed_frame in self.video_processor.process_video_with_raw_data(self.cap, self.json_dir):
            self.show_processed_frame(processed_frame)
            self.write_frame_to_output(processed_frame)
            if cv2.waitKey(1) > 0:
                break

    @staticmethod
    def show_processed_frame(frame):
        cv2.imshow('Output', frame)

    def write_frame_to_output(self, frame):
        self.video_writer.write(frame)

    def __del__(self):
        if self.cap:
            self.cap.release()
        if self.video_writer:
            self.video_writer.release()


pulluper = PullUpCounter()
t = time.time()
pulluper.start()
print(f'Execution time: {time.time() - t:.3} sec')