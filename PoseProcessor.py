import Utils
import cv2
import math
import queue
from collections import deque

from Drawer import Drawer


class PoseProcessor:
    def __init__(self, arm_angle_threshold, leg_angle_threshold, failed_attempts_amount_threshold,
                 neck_chin_top_of_head_ratio, chin_to_wrists_raise_ratio_to_start_attempt=0.7,
                 chin_to_wrists_raise_ration_to_finish_attempt=0.1):
        self._cur_wrists_level_angle = None
        self._cur_left_arm_angle, self._cur_right_arm_angle = None, None
        self._cur_left_leg_angle, self._cur_right_leg_angle = None, None
        self._cur_angle_between_legs = None
        self.arm_angle_threshold = arm_angle_threshold
        self.leg_angle_threshold = leg_angle_threshold
        self.wrists_level_angle_threshold = 5
        self.states = ['hanging in the bottom position', 'ascending', 'hanging in the top position', 'descending',
                       'undefined state']
        self._cur_state = self.states[4]
        self._pure_repeats = 0
        self._impure_repeats = 0
        self._failed_state_detection_attempts = 0
        self.process_current_state = {self.states[0]: self.process_hanging_in_bottom_position,
                                      self.states[1]: self.process_ascending,
                                      self.states[2]: self.process_hanging_in_top_position,
                                      self.states[3]: self.process_descending,
                                      self.states[4]: self.process_undefined_state}
        self.failed_attempts_amount_threshold = failed_attempts_amount_threshold
        self._chin_point = []
        self.neck_chin_nose_ratio = neck_chin_top_of_head_ratio
        self._boundary_distance_between_chin_and_wrist_to_start_attempt = None
        self._boundary_distance_between_chin_and_wrist_to_finish_attempt = None
        self.chin_to_wrists_raise_ratio_to_start_attempt = chin_to_wrists_raise_ratio_to_start_attempt
        self.chin_to_wrists_raise_ratio_to_finish_attempt = chin_to_wrists_raise_ration_to_finish_attempt
        self._pull_up_attempt_flag = False

        self.queue_history = 3
        self.last_wrist_y_deviations = deque(maxlen=self.queue_history)
        self.last_shoulder_y_deviations = deque(maxlen=self.queue_history)
        self.wrists_shoulders_distance_deviation_per_frame_threshold = 1 / 2
        self.deviation_per_frame_threshold = None
        self.prev_shoulders_y = None
        self.prev_wrists_y = None

    def get_wrists_level_angle(self):
        return self._cur_wrists_level_angle

    def get_left_arm_angle(self):
        return self._cur_left_arm_angle

    def get_right_arm_angle(self):
        return self._cur_right_arm_angle

    def get_left_leg_angle(self):
        return self._cur_left_leg_angle

    def get_right_leg_angle(self):
        return self._cur_right_leg_angle

    def get_cur_state(self):
        return self._cur_state

    def get_pure_repeats(self):
        return self._pure_repeats

    def get_impure_repeats(self):
        return self._impure_repeats

    def get_chin_point(self):
        return self._chin_point

    wrists_level_angle = property(get_wrists_level_angle)
    left_arm_angle = property(get_left_arm_angle)
    right_arm_angle = property(get_right_arm_angle)
    left_leg_angle = property(get_left_leg_angle)
    right_leg_angle = property(get_right_leg_angle)
    cur_state = property(get_cur_state)
    pure_repeats = property(get_pure_repeats)
    impure_repeats = property(get_impure_repeats)
    chin_point = property(get_chin_point)

    def zero_failed_state_detection_attempts(self):
        self._failed_state_detection_attempts = 0

    def inc_failed_state_detection_attempts(self):
        self._failed_state_detection_attempts += 1

    def check_failed_state_detection_attempts_amount(self):
        if self._failed_state_detection_attempts > self.failed_attempts_amount_threshold:
            self._cur_state = self.states[4]

    def process_hanging_in_bottom_position(self, points):
        angle_in_arms_is_valid = self.are_arms_straight(points)
        if not angle_in_arms_is_valid:
            self._cur_state = self.states[1]

    def process_hanging_in_top_position(self, points):
        neck_is_over_wrists_level = self.is_chin_over_wrists_level(points)
        if not neck_is_over_wrists_level:
            self._cur_state = self.states[3]

    def process_undefined_state(self, points):
        there_is_initial_position = self.is_there_initial_position(points)
        if there_is_initial_position:
            self._cur_state = self.states[0]

    def reset_shifts(self):
        self.last_shoulder_y_deviations.clear()
        self.last_wrist_y_deviations.clear()
        self.prev_wrists_y = None
        self.prev_shoulders_y = None

    def define_wrists_shoulders_deviation_per_frame(self, points):
        distance_between_wrists_and_shoulders = self.find_distance_between_wrists_and_shoulders(points)
        self.deviation_per_frame_threshold = distance_between_wrists_and_shoulders * self.wrists_shoulders_distance_deviation_per_frame_threshold

    @staticmethod
    def find_distance_between_wrists_and_shoulders(points):
        avg_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2
        avg_shoulders_y = (points['LShoulder'][1] + points['RShoulder'][1]) / 2
        return abs(avg_wrists_y - avg_shoulders_y)

    def find_distance_between_wrists_and_chin(self, points):
        avg_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2
        return None if not self.chin_point else self.chin_point[1] - avg_wrists_y

    def define_initial_distance_between_wrists_and_chin(self, points):
        distance_between_wrists_and_chin = self.find_distance_between_wrists_and_chin(points)
        if not distance_between_wrists_and_chin:
            return
        self._boundary_distance_between_chin_and_wrist_to_start_attempt = distance_between_wrists_and_chin * (
                    1 - self.chin_to_wrists_raise_ratio_to_start_attempt)
        self._boundary_distance_between_chin_and_wrist_to_finish_attempt = distance_between_wrists_and_chin * (
                    1 - self.chin_to_wrists_raise_ratio_to_finish_attempt)

    def is_there_initial_position(self, points):
        self.define_wrists_shoulders_deviation_per_frame(points)
        self.reset_shifts()
        self.define_initial_distance_between_wrists_and_chin(points)

        angle_in_arms_is_valid = self.are_arms_straight(points)
        wrists_are_over_body = self.is_wrists_over_body(points)
        legs_are_straight = self.are_legs_straight(points)
        return True if angle_in_arms_is_valid and wrists_are_over_body and legs_are_straight else False

    def are_legs_straight(self, points):
        # legs are straight if:
        # they are not found or
        # angle in one of them less than leg_angle_threshold and second isn't found or
        # angles in both of them is less than leg_angle_threshold
        self._cur_left_leg_angle, self._cur_right_leg_angle = -math.inf, -math.inf
        if self.are_points_existing(points['LHip'], points['LKnee'], points['LAnkle']):
            self._cur_left_leg_angle = self.get_angle_between_three_points(points['LHip'], points['LKnee'],
                                                                           points['LAnkle'])

        if self.are_points_existing(points['RHip'], points['RKnee'], points['RAnkle']):
            self._cur_right_leg_angle = self.get_angle_between_three_points(points['RHip'], points['RKnee'],
                                                                            points['RAnkle'])

        return True if self._cur_left_leg_angle < self.leg_angle_threshold and self._cur_right_leg_angle < self.leg_angle_threshold else False

    def inc_pure_repeats_amount(self):
        self._pure_repeats += 1
        self.reset_attempt()

    def inc_impure_repeats_amount(self):
        self._impure_repeats += 1
        self.reset_attempt()

    def reset_attempt(self):
        self._pull_up_attempt_flag = False

    def process_ascending(self, points):
        chin_is_over_wrists_level = self.is_chin_over_wrists_level(points)

        self.update_wrist_y_deviations(points)
        self.update_shoulder_y_deviations(points)
        self.check_impure_pull_up(points)

        if chin_is_over_wrists_level:
            wrists_deviations_sum = sum(self.last_wrist_y_deviations)
            shoulders_deviations_sum = sum(self.last_shoulder_y_deviations)
            # just debug, will be deleted
            # print(wrists_deviations_sum, '  |  ', shoulders_deviations_sum)
            if shoulders_deviations_sum > wrists_deviations_sum:
                print(self.chin_point, points['LWrist'], points['LWrist'])
                self.inc_pure_repeats_amount()
                self._cur_state = self.states[2]

    def check_impure_pull_up(self, points):
        if not self.chin_point:
            return
        cur_distance_between_chin_and_wrists = self.find_distance_between_wrists_and_chin(points)

        # print(cur_distance_between_chin_and_wrists, self._boundary_distance_between_chin_and_wrist)
        if not self._pull_up_attempt_flag:
            self._pull_up_attempt_flag = True if cur_distance_between_chin_and_wrists <= self._boundary_distance_between_chin_and_wrist_to_start_attempt else False
        else:
            impure_pull_up_is_done = True if cur_distance_between_chin_and_wrists > self._boundary_distance_between_chin_and_wrist_to_finish_attempt else False
            if impure_pull_up_is_done:
                self.inc_impure_repeats_amount()
                self._pull_up_attempt_flag = False

    def update_wrist_y_deviations(self, points):
        cur_avg_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2

        if not self.prev_wrists_y:
            self.prev_wrists_y = cur_avg_wrists_y
            return

        cur_wrists_y_deviation = abs(self.prev_wrists_y - cur_avg_wrists_y)

        if cur_wrists_y_deviation < self.deviation_per_frame_threshold:
            self.last_wrist_y_deviations.append(cur_wrists_y_deviation)
            self.prev_wrists_y = cur_avg_wrists_y
        else:
            self.prev_wrists_y = None

    def update_shoulder_y_deviations(self, points):
        cur_avg_shoulders_y = (points['LShoulder'][1] + points['RShoulder'][1]) / 2
        if not self.prev_shoulders_y:
            self.prev_shoulders_y = cur_avg_shoulders_y
            return

        cur_shoulders_y_deviation = abs(self.prev_shoulders_y - cur_avg_shoulders_y)

        if cur_shoulders_y_deviation < self.deviation_per_frame_threshold:
            self.last_shoulder_y_deviations.append(cur_shoulders_y_deviation)
            self.prev_shoulders_y = cur_avg_shoulders_y
        else:
            self.prev_shoulders_y = None

    def process_descending(self, points):
        there_is_initial_position = self.is_there_initial_position(points)
        if there_is_initial_position:
            self._cur_state = self.states[0]

    def is_there_hang(self, points):
        wrists_is_on_same_level = self.is_wrists_on_same_level(points)
        wrists_is_higher_than_elbows = self.are_wrists_higher_than_elbows(points)
        head_is_between_arms = self.is_head_between_arms(points)
        return True if wrists_is_on_same_level and wrists_is_higher_than_elbows and head_is_between_arms else False

    def is_head_between_arms(self, points):
        if not (points['LWrist'] and points['RWrist'] and points['Nose']):
            return False

        min_x_of_wrist = min(points['LWrist'][0], points['RWrist'][0])
        max_x_of_wrist = max(points['LWrist'][0], points['RWrist'][0])
        return True if min_x_of_wrist < points['Nose'][0] < max_x_of_wrist else False

    @staticmethod
    def are_wrists_higher_than_elbows(points):
        if not all((points['LWrist'], points['RWrist'], points['LElbow'], points['RElbow'])):
            return False

        left_wrist_y, right_wrist_y = points['LWrist'][1], points['RWrist'][1]
        left_elbow_y, right_elbow_y = points['LElbow'][1], points['RElbow'][1]
        return True if left_wrist_y < left_elbow_y and right_wrist_y < right_elbow_y else False

    @staticmethod
    def are_points_existing(point_a, point_b, point_c):
        return point_a and point_b and point_c

    @staticmethod
    def get_angle_between_three_points(point_a, point_b, point_c):
        return Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(point_a, point_b),
            Utils.get_vector_from_points(point_b, point_c))

    @staticmethod
    def is_wrists_over_body(points):
        # we have to compare wrists y-coordinate with other's y coordinates
        # but since coordinate system begins at the top left corner our highest
        # point is actually lowest one

        if not (points['LWrist'] and points['RWrist']):
            return False
        left_wrist_y, right_wrist_y = points['LWrist'][1], points['RWrist'][1]
        copy_points = dict(points)
        del copy_points['LWrist']
        del copy_points['RWrist']
        ys = (point[1] for point in copy_points.values() if point)

        lowest_y = min(ys)
        return True if left_wrist_y < lowest_y and right_wrist_y < lowest_y else False

    def are_arms_straight(self, points):
        self._cur_left_arm_angle, self._cur_right_arm_angle = math.inf, math.inf
        if self.are_points_existing(points['LWrist'], points['LElbow'], points['LShoulder']):
            self._cur_left_arm_angle = self.get_angle_between_three_points(points['LWrist'], points['LElbow'],
                                                                           points['LShoulder'])

        if self.are_points_existing(points['RWrist'], points['RElbow'], points['RShoulder']):
            self._cur_right_arm_angle = self.get_angle_between_three_points(points['RWrist'], points['RElbow'],
                                                                            points['RShoulder'])

        return True if self._cur_left_arm_angle < self.arm_angle_threshold and self._cur_right_arm_angle < self.arm_angle_threshold else False

    def is_wrists_on_same_level(self, points):
        if not (points['LWrist'] and points['RWrist']):
            return False

        left_wrist_point, right_wrist_point = points['LWrist'], points['RWrist']

        delta_y = abs(left_wrist_point[1] - right_wrist_point[1])
        delta_x = abs(left_wrist_point[0] - right_wrist_point[0])

        # prevention of division by zero
        if delta_x == 0:
            return False
        angle_in_radians = math.atan(delta_y / delta_x)
        self._cur_wrists_level_angle = int(math.degrees(angle_in_radians))

        return True if self._cur_wrists_level_angle <= self.wrists_level_angle_threshold else False

    def is_chin_over_wrists_level(self, points):
        if not (points['LWrist'] and points['RWrist'] and self._chin_point):
            return False

        left_wrist_point, right_wrist_point = points['LWrist'], points['RWrist']
        avg_wrists_y = (left_wrist_point[1] + right_wrist_point[1]) / 2
        return True if self.chin_point[1] < avg_wrists_y else False

    def define_state(self, points):
        self.define_chin(points)
        if self.is_there_hang(points):
            self.zero_failed_state_detection_attempts()
            self.process_current_state[self._cur_state](points)
            return True
        else:
            self.inc_failed_state_detection_attempts()
            self.check_failed_state_detection_attempts_amount()
            return False

    def define_chin(self, points):
        # define chin point by simple ratio between head and neck
        nose_point, neck_point = points['Nose'], points['Neck']
        if not (nose_point and neck_point):
            self._chin_point = None
            return

        chin_point_x = neck_point[0] + int((nose_point[0] - neck_point[0]) * self.neck_chin_nose_ratio)
        chin_point_y = neck_point[1] + int((nose_point[1] - neck_point[1]) * self.neck_chin_nose_ratio)
        self._chin_point = [chin_point_x, chin_point_y]
