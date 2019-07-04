import sys
from sys import platform
from PhaseQualifier import PhaseQualifier
from VideoProcessor import VideoProcessor
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
        self.output_file_name = ""
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
        self.short_input_filename = os.path.basename(self.input_file)
        if self.use_raw_data:
            self.json_dir = self.find_json_dir_by_video_name(self.input_file)
            if not self.json_dir:
                raise FileNotFoundError("Json directory not found in the video's specified directory")
        self.output_dir = args.output_dir
        if not os.path.isdir(self.output_dir):
            raise FileNotFoundError("Output directory not found.")
        self.output_file_name = os.path.join(self.output_dir, f'{self.short_input_filename}')

    def find_json_dir_by_video_name(self, filename):
        """Find a directory consisting json files by video name.

        In the directory containing our video file we are trying to find the directory
        having the same name which the video has.
        """
        par_dir = os.path.dirname(filename)
        possible_json_dir = f'{os.path.join(par_dir, self.short_input_filename.split(".")[0])}_json'
        return possible_json_dir if os.path.isdir(possible_json_dir) else None

    def create_video_processor(self):
        self.video_processor = VideoProcessor(self.input_file, self.output_file_name, self.pose_processor,
                                              self.required_points, self.required_pairs)

    def start(self):
        """Launch the pull up counter in the way depending on the chosen method."""
        self.create_video_processor()

        if self.use_raw_data:
            self.exec_with_raw_data()
        else:
            self.exec()

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

        self.video_processor.process_video_with_net(op_wrapper)

    def exec_with_raw_data(self):
        """Process the input file using prepared json-files."""
        self.video_processor.process_video_with_raw_data(self.json_dir)


pull_up_counter = PullUpCounter()
t = time.time()
pull_up_counter.start()
print(f'Execution time: {time.time() - t:.3} sec')
