import cv2
import Utils
import os
import json
from Drawer import Drawer
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
                    is_state_defined = self._pose_processor.define_state(points)
                    if self._debug:
                        # probably add some options for displaying _debug information
                        self.display_debug_info(frame, points, is_state_defined)
                yield frame


    @staticmethod
    def get_video_size(cap):
        input_video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        input_video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return input_video_width, input_video_height

    def display_debug_info(self, frame, points, is_state_defined):
        if not is_state_defined:
            Drawer.print_message(frame, f'Failed state detection attempt', 10, 200)
        if self._pose_processor.chin_point:
            Drawer.draw_point(frame, self._pose_processor.chin_point, Drawer.BLUE_COLOR, 8)
        Drawer.draw_skeleton(frame, points, self._required_pairs)
        Drawer.print_message(frame, f'left arm angle: {self._pose_processor.left_arm_angle}', 10, 50)
        Drawer.print_message(frame, f'right arm angle: {self._pose_processor.right_arm_angle}', 10, 90)
        Drawer.print_message(frame, f'wrists levels angle: {self._pose_processor.wrists_level_angle}', 10, 130)
        Drawer.print_message(frame, f'repeats: {self._pose_processor.repeats}', 10, 170)
        Drawer.print_message(frame, f'current state: {self._pose_processor.cur_state}', 10, frame.shape[0] - 20)

    def get_threshold(self):
        return self._threshold

    def set_threshold(self, threshold):
        # have to add some constraint logic on threshold
        self._threshold = threshold

    threshold = property(get_threshold, set_threshold)
