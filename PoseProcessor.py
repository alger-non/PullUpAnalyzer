import Utils
import cv2
import math


class PoseProcessor:
    def __init__(self):
        self._cur_wrists_level_angle = None
        self._cur_left_arm_angle, self._cur_right_arm_angle = None, None
        self.arm_angle_threshold = 30
        self.wrists_level_angle_threshold = 10
        self.states = ['hanging int the bottom position', 'ascending', 'hanging in the top position', 'descending',
                       'undefined state']
        self.cur_state = self.states[4]
        self.repeats = 0

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

    wrists_level_angle = property(get_wrists_level_angle)
    left_arm_angle = property(get_left_arm_angle)
    right_arm_angle = property(get_right_arm_angle)

    def process_hanging_in_bottom_position(self, points, frame):
        pass

    def process_hanging_in_top_position(self):
        pass

    def process_undefined_state(self, points, frame):
        wrists_is_on_same_level = self.is_wrists_on_same_level(points, frame)
        angle_in_arms_is_valid = self.is_arms_straight(points, frame)

        if angle_in_arms_is_valid and wrists_is_on_same_level:
            self.cur_state = self.states[0]

    def process_ascending(self):
        pass

    def process_descending(self):
        pass

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

    def is_arms_straight(self, points, frame):
        angle_of_left_arm, angle_of_right_arm = math.inf, math.inf
        if self.is_arm_points_exist(points['LWrist'], points['LElbow'], points['LShoulder']):
            self._cur_left_arm_angle = self.get_angle_between_wrist_and_shoulder_in_left(points)

        if self.is_arm_points_exist(points['RWrist'], points['RElbow'], points['RShoulder']):
            self._cur_right_arm_angle = self.get_angle_between_wrist_and_shoulder_in_right(points)

        return True if angle_of_left_arm < self.arm_angle_threshold and angle_of_right_arm < self.arm_angle_threshold else False

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
        lowest_wrist_y = min(left_wrist_point[1], right_wrist_point[1])
        if neck_point[1] >= lowest_wrist_y:
            return True
        else:
            return False

    def define_state(self, points, frame):
        self.process_current_state[self.cur_state](points, frame)
        cv2.putText(frame, f'{self.cur_state}', (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4,
                    lineType=cv2.LINE_AA)
