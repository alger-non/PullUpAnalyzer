import Utils
import cv2
import math


class PoseProcessor:
    def __init__(self):
        self.angle_threshold = 30
        self.states = ['hanging int the bottom position', 'ascending', 'hanging in the top position', 'descending', 'undefined state']
        self.cur_state = self.states[4]
        self.repeats = 0
        self.process_current_state = {self.states[0]: self.process_hanging_in_bottom_position,
                                      self.states[1]: self.process_ascending,
                                      self.states[2]: self.process_hanging_in_top_position,
                                      self.states[3]: self.process_descending,
                                      self.states[4]: self.process_undefined_state}


    def process_hanging_in_bottom_position(self, points, frame):
        pass


    def process_hanging_in_top_position(self):
        pass

    def process_undefined_state(self, points, frame):
        is_wrists_on_one_level = self.is_wrists_on_one_level(points, frame)
        is_angle_in_arms_valid = self.is_angle_in_arms_valid(points, frame)

        if is_angle_in_arms_valid and is_wrists_on_one_level:
            self.cur_state = self.states[0]

    def process_ascending(self):
        pass

    def process_descending(self):
        pass

    @staticmethod
    def is_arm_points_valid(point_a, point_b, point_c):
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

    def is_angle_in_arms_valid(self, points, frame):
        angle_of_left_arm, angle_of_right_arm = math.inf, math.inf
        ret_val = False
        if self.is_arm_points_valid(points['LWrist'], points['LElbow'], points['LShoulder']):
            angle_of_left_arm = self.get_angle_between_wrist_and_shoulder_in_left(points)
            cv2.putText(frame, f'left arm: {angle_of_left_arm}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)

        if self.is_arm_points_valid(points['RWrist'], points['RElbow'], points['RShoulder']):
            angle_of_right_arm = self.get_angle_between_wrist_and_shoulder_in_right(points)
            cv2.putText(frame, f'right arm: {angle_of_right_arm}', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                        2,
                        lineType=cv2.LINE_AA)

        if angle_of_left_arm < self.angle_threshold and angle_of_right_arm < self.angle_threshold:
            ret_val = True

        return ret_val

    @staticmethod
    def is_wrists_on_one_level(points, frame):

        if not (points['LWrist'] and points['RWrist']):
            return False

        left_wrist_point, right_wrist_point = points['LWrist'], points['RWrist']

        delta_y = abs(left_wrist_point[1] - right_wrist_point[1])
        delta_x = abs(left_wrist_point[0] - right_wrist_point[0])

        # prevention of division by zero
        if delta_x == 0:
            return False
        angle_in_radians = math.atan(delta_y / delta_x)
        angle_in_degrees = int(math.degrees(angle_in_radians))
        cv2.putText(frame, f'angle between wrists is {angle_in_degrees}', (10, 170), cv2.FONT_HERSHEY_COMPLEX, .8,
                    (255, 50, 0), 2, lineType=cv2.LINE_AA)
        return True

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
