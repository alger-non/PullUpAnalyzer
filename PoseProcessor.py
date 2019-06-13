import Utils
import cv2
import math


class PoseProcessor:
    def __init__(self):
        self._cur_wrists_level_angle = None
        self._cur_left_arm_angle, self._cur_right_arm_angle = None, None
        self.arm_angle_threshold = 30
        self.wrists_level_angle_threshold = 10
        self.states = ['hanging in the bottom position', 'ascending', 'hanging in the top position', 'descending',
                       'undefined state']
        self._cur_state = self.states[4]
        self._repeats = 0

        self.process_current_state = {self.states[0]: self.process_hanging_in_bottom_position,
                                      self.states[1]: self.process_ascending,
                                      self.states[2]: self.process_hanging_in_top_position,
                                      self.states[3]: self.process_descending,
                                      self.states[4]: self.process_undefined_state}

    def get_wrists_level_angle(self):
        return self._cur_wrists_level_angle

    def get_left_arm_angle(self):
        return self._cur_left_arm_angle

    def get_right_arm_angle(self):
        return self._cur_right_arm_angle

    def get_cur_state(self):
        return self._cur_state

    def get_repeats(self):
        return self._repeats

    wrists_level_angle = property(get_wrists_level_angle)
    left_arm_angle = property(get_left_arm_angle)
    right_arm_angle = property(get_right_arm_angle)
    cur_state = property(get_cur_state)
    repeats = property(get_repeats)

    def process_hanging_in_bottom_position(self, points):
        angle_in_arms_is_valid = self.is_arms_straight(points)
        if not angle_in_arms_is_valid:
            self._cur_state = self.states[1]

    def process_hanging_in_top_position(self, points):
        neck_is_over_wrists_level = self.is_neck_over_wrists_level(points)
        if not neck_is_over_wrists_level:
            self._cur_state = self.states[3]

    def process_undefined_state(self, points):
        there_is_initial_position = self.is_there_initial_position(points)
        if there_is_initial_position:
            self._cur_state = self.states[0]

    def is_there_initial_position(self, points):
        wrists_is_on_same_level = self.is_wrists_on_same_level(points)
        angle_in_arms_is_valid = self.is_arms_straight(points)
        wrists_is_over_body = self.is_wrists_over_body(points)
        print(wrists_is_on_same_level, angle_in_arms_is_valid, wrists_is_over_body)
        return True if angle_in_arms_is_valid and wrists_is_on_same_level and wrists_is_over_body else False

    def process_ascending(self, points):
        neck_is_over_wrists_level = self.is_neck_over_wrists_level(points)
        if neck_is_over_wrists_level:
            self._repeats += 1
            self._cur_state = self.states[2]

    def process_descending(self, points):
        there_is_initial_position = self.is_there_initial_position(points)
        if there_is_initial_position:
            self._cur_state = self.states[0]

    @staticmethod
    def is_arm_points_exist(point_a, point_b, point_c):
        unique_points = {point_a, point_b, point_c}
        return point_a and point_b and point_c and len(unique_points) == 3

    @staticmethod
    def get_angle_between_wrist_and_shoulder_in_left(points: list):
        return Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['LWrist'], points['LElbow']),
            Utils.get_vector_from_points(points['LElbow'], points['LShoulder']))

    @staticmethod
    def get_angle_between_wrist_and_shoulder_in_right(points: list):
        return Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['RWrist'], points['RElbow']),
            Utils.get_vector_from_points(points['RElbow'], points['RShoulder']))

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

    def is_arms_straight(self, points):
        self._cur_left_arm_angle, self._cur_right_arm_angle = math.inf, math.inf
        if self.is_arm_points_exist(points['LWrist'], points['LElbow'], points['LShoulder']):
            self._cur_left_arm_angle = self.get_angle_between_wrist_and_shoulder_in_left(points)

        if self.is_arm_points_exist(points['RWrist'], points['RElbow'], points['RShoulder']):
            self._cur_right_arm_angle = self.get_angle_between_wrist_and_shoulder_in_right(points)

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

    @staticmethod
    def is_neck_over_wrists_level(points):
        if not (points['LWrist'] and points['RWrist'] and points['Neck']):
            return False

        left_wrist_point, right_wrist_point, neck_point = points['LWrist'], points['RWrist'], points['Neck']
        lowest_wrist_y = max(left_wrist_point[1], right_wrist_point[1])
        return True if neck_point[1] <= lowest_wrist_y else False

    def define_state(self, points):
        self.process_current_state[self._cur_state](points)
