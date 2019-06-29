import cv2
import Utils
import os
import json
from ResultsDrawer import ResultsDrawer
from os import walk
from PhaseQualifier import PhaseQualifier


class VideoProcessor:
    """Class to handle an input video."""

    def __init__(self, phase_definer: PhaseQualifier, required_points, required_pairs):
        self.phase_definer = phase_definer
        self.required_points = required_points
        self.required_pairs = required_pairs
        self._drawer = None

    def process_video_with_net(self, cap: cv2.VideoCapture, op_wrapper):
        """Create a generator returning processed frames using only an input video.

        :param cap: an initialized video-capture instance to read frames from a video
        :param op_wrapper: an initialized open-pose instance to handle frames
        :return: a generator returning processed frames
        """
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        # pass fps to the ResultsDrawer instance to obtain same animation effect on videos with different fps
        self._drawer = ResultsDrawer(fps)
        while True:
            has_frame, frame = cap.read()
            if not has_frame:
                return None
            datum = op.Datum()
            datum.cvInputData = frame
            op_wrapper.emplaceAndPop([datum])
            # check whether datum contains person key points (25 points consisting of x, y, probability)
            if datum.poseKeypoints.size == 75:
                points = Utils.extract_required_points(datum.poseKeypoints[0], self.required_points)
                self.phase_definer.define_state(points)
                frame = self.put_info_on_frame(frame, points)
            yield frame

    @staticmethod
    def get_json_files_from_dir(json_dir):
        """Return all file names from the specified directory.

        :param json_dir: a directory containing json files producing by OpenPose
        :return: a list of file names
        """
        json_files = []
        for _, _, f_names in walk(json_dir):
            json_files.extend(f_names)
            break
        json_files = sorted(json_files)
        return json_files

    def process_video_with_raw_data(self, cap: cv2.VideoCapture, json_dir):
        """Create a generator returning processed frames using an input video and json key points.

        :param cap: an initialized video-capture instance to read frames from a video
        :param json_dir: a directory name containing json files with key points
        :return: a generator returning processed frames
        """
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        self._drawer = ResultsDrawer(fps)
        json_files = self.get_json_files_from_dir(json_dir)

        for filename in json_files:
            full_filename_path = os.path.join(json_dir, filename)
            with open(full_filename_path, "r") as json_data:
                data = json.load(json_data)
                has_frame, frame = cap.read()
                if not has_frame:
                    return None
                # check whether the json file contains person key points (is a person found?)
                if data['people']:
                    points_list = data['people'][0]['pose_keypoints_2d']
                    points = Utils.extract_required_json_points(points_list, self.required_points)
                    self.phase_definer.define_state(points)
                    frame = self.put_info_on_frame(frame, points)
                yield frame

    def put_info_on_frame(self, frame, points):
        """Put on the frame a pulling ups info.

        :param frame: a frame to be applied
        :param points: key points
        :return: a handled frame
        """
        new_frame = self._drawer.display_info(frame, self.phase_definer)
        self._drawer.display_skeleton(new_frame, points, self.required_pairs)
        self._drawer.draw_line_between_wrists(new_frame, points)
        self._drawer.draw_chin_point(new_frame, self.phase_definer)
        return new_frame
