import sys
from sys import platform
from AudioProcessor import AudioProcessor
from PhaseQualifier import PhaseQualifier
from VideoProcessor import VideoProcessor
import cv2
import os
import argparse
import time

dir_path = os.path.dirname(os.path.realpath(__file__))


class PullUpCounter:
    """The general class for launching the pull ups counter."""

    def __init__(self):
        self.input_file = ""
        self.short_input_filename = ""
        self.output_dir = ""
        self.json_dir = ""
        self.use_raw_data = False
        self.cap = None
        self.video_writer = None
        self.audio_writer = None
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
        self.video_processor = None
        self.parse_cmd_line()

    def parse_cmd_line(self):
        """Extract arguments from the command line."""
        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', help='directory containing source video and json data directory')
        parser.add_argument('output_dir', help='directory in which will be saved the final video')
        parser.add_argument('--use-raw-data', dest='use_raw_data', default=False,
                            help='True or False depending on whether you have json-data in '
                                 'directory with the input video')
        args = parser.parse_args()

        self.use_raw_data = args.use_raw_data
        self.input_file = args.input_file
        if not os.path.isfile(self.input_file):
            raise FileNotFoundError("Input file not found.")
        self.short_input_filename = os.path.basename(self.input_file).split('.')[0]
        if self.use_raw_data:
            self.json_dir = self.find_json_dir_by_video_name(args.input_file)
            if not self.json_dir:
                raise FileNotFoundError("Json directory not found in the video's specified directory")
        self.output_dir = args.output_dir
        if not os.path.isdir(self.output_dir):
            raise FileNotFoundError("Output directory not found.")

    def find_json_dir_by_video_name(self, filename):
        """Find a directory consisting json files by video name.

        In the directory containing our video file we are trying to find the directory
        having the same name which the video has.
        """
        par_dir = os.path.dirname(filename)
        possible_json_dir = f'{os.path.join(par_dir, self.short_input_filename)}_json'
        return possible_json_dir if os.path.isdir(possible_json_dir) else None

    def create_video_capture(self):
        self.cap = cv2.VideoCapture(self.input_file)

    def create_video_writer(self):
        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        output_filename_without_sound = os.path.join(self.output_dir, f'{self.short_input_filename}_without_audio.avi')
        self.video_writer = cv2.VideoWriter(output_filename_without_sound, cv2.VideoWriter_fourcc(*"XVID"), fps,
                                            (cap_width, cap_height))

    def add_audio(self):
        self.audio_writer.add_background_audio()

    def create_audio_writer(self):
        output_filename_without_sound = os.path.join(self.output_dir, f'{self.short_input_filename}_without_audio.avi')
        output_filename_with_sound = os.path.join(self.output_dir, f'{self.short_input_filename}.avi')
        self.audio_writer = AudioProcessor(self.input_file, output_filename_without_sound, output_filename_with_sound)

    def create_video_processor(self):
        self.video_processor = VideoProcessor(self.cap, self.pose_processor, self.required_points, self.required_pairs)

    def start(self):
        """Launch the pull up counter in the way depending on the chosen method."""
        self.create_video_capture()
        self.create_video_writer()
        self.create_audio_writer()
        self.create_video_processor()

        if self.use_raw_data:
            self.exec_with_raw_data()
        else:
            self.exec()
        self.release_video_cap()
        self.release_video_writer()
        cv2.destroyAllWindows()

    def exec(self):
        """Process the input video using the OpenPose library."""
        # We moved import statement here to use preprocessed data without existing OpenPose.
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '/../../python/openpose/Release')
                os.environ['PATH'] = os.environ[
                                         'PATH'] + ';' + dir_path + '/../../x64/Release;' + dir_path + '/../../bin;'
                import pyopenpose as op
            else:
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append('../../python')
                # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access
                # the OpenPose/python module from there. This will install OpenPose and the python library at your
                # desired installation path. Ensure that this is in your python path in order to use it.
                # sys.path.append('/usr/local/python')
                from openpose import pyopenpose as op
        except ImportError as e:
            print(
                'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON`'
                ' in CMake and have this Python script in the right folder?')
            raise e


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
        """Process the input file using prepared json-files."""
        for processed_frame in self.video_processor.process_video_with_raw_data(self.cap, self.json_dir):
            self.show_processed_frame(processed_frame)
            self.write_frame_to_output(processed_frame)
            if cv2.waitKey(1) > 0:
                break

    def release_video_cap(self):
        if self.cap:
            self.cap.release()

    def release_video_writer(self):
        if self.video_writer:
            self.video_writer.release()

    @staticmethod
    def show_processed_frame(frame):
        cv2.imshow('Output', frame)

    def write_frame_to_output(self, frame):
        self.video_writer.write(frame)


pull_up_counter = PullUpCounter()
t = time.time()
pull_up_counter.start()

for rep_time, is_clean_rep in pull_up_counter.video_processor.events_labels:
    event = 'Complete' if is_clean_rep else 'Fail'
    pull_up_counter.audio_writer.add_event(event, rep_time)

pull_up_counter.add_audio()
print(f'Execution time: {time.time() - t:.3} sec')
