import cv2
import Utils
import os
import json
from ResultsDrawer import ResultsDrawer
from os import walk
from openpose import pyopenpose as op


class VideoProcessor:
    """Class to handle input video."""
    def __init__(self, pose_processor, required_points, required_pairs, threshold=0.1, default_in_size=368):
        self.pose_processor = pose_processor
        self._required_points = required_points
        self._required_pairs = required_pairs
        self._threshold = threshold
        self._default_in_size = default_in_size
        self._drawer = None

    def process_video_with_net(self, cap: cv2.VideoCapture, op_wrapper: op.WrapperPython):
        """Create generator returning processed frames.

        :param cap: initialized video-capture instance to read frames from video
        :param op_wrapper: initialized open-pose instance to handle frames
        :return: generator returning processed frames

        """
        fps = int(cap.get(cv2.CAP_PROP_FPS))
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
                points = Utils.extract_required_points(datum.poseKeypoints[0], self._required_points)
                self.pose_processor.define_state(points)
                frame = self.display_debug_info(frame, points)
            yield frame

    @staticmethod
    def get_json_files_from_dir(json_dir):
        """

        :param json_dir:
        :return:
        """
        json_files = []
        for _, _, f_names in walk(json_dir):
            json_files.extend(f_names)
            break
        json_files = sorted(json_files)
        return json_files

    def process_video_with_raw_data(self, cap: cv2.VideoCapture, json_dir):

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

                if data['people']:
                    points_list = data['people'][0]['pose_keypoints_2d']
                    points = Utils.extract_required_json_points(points_list, self._required_points)
                    self.pose_processor.define_state(points)
                    frame = self.display_debug_info(frame, points)
                yield frame

    def display_debug_info(self, frame, points):
        new_frame = self._drawer.display_info(frame, self.pose_processor)
        self._drawer.display_skeleton(new_frame, points, self._required_pairs)
        self._drawer.draw_line_between_wrists(new_frame, points)
        self._drawer.draw_chin_point(new_frame, self.pose_processor)

        return new_frame

    def get_threshold(self):
        return self._threshold

    threshold = property(get_threshold)
