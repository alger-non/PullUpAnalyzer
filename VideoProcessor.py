import cv2
import Utils
import os
import json
from ResultsDrawer import ResultsDrawer
from os import walk


class VideoProcessor:
    def __init__(self, pose_processor, required_points, required_pairs, threshold=0.1, default_in_size=368):
        self._pose_processor = pose_processor
        self._required_points = required_points
        self._required_pairs = required_pairs
        self._threshold = threshold
        self._debug = False
        self._default_in_size = default_in_size

    def enable_debug(self):
        self._debug = True

    def disable_debug(self):
        self._debug = False

    def process_video_with_net(self, cap, net, in_size=None):
        raise NotImplementedError('This method not implemented yet')

    def process_video_with_raw_data(self, cap, json_dir):
        filenames = []
        for _, _, f_names in walk(json_dir):
            filenames.extend(f_names)
            break
        filenames = sorted(filenames)
        for filename in filenames:

            full_filename_path = os.path.join(json_dir, filename)
            with open(full_filename_path, "r") as json_data:
                data = json.load(json_data)

                has_frame, frame = cap.read()
                if not has_frame:
                    return None

                if data['people']:
                    points_list = data['people'][0]['pose_keypoints_2d']
                    points = Utils.extract_required_points(points_list, self._required_points)
                    self._pose_processor.define_state(points)
                    if self._debug:
                        # probably add some options for displaying _debug information
                        self.display_debug_info(frame, cap)
                yield frame

    def display_debug_info(self, frame, cap):
        ResultsDrawer.display_info(frame, cap, self._pose_processor)

    def get_threshold(self):
        return self._threshold

    def set_threshold(self, threshold):
        # have to add some constraint logic on threshold
        self._threshold = threshold

    threshold = property(get_threshold, set_threshold)
