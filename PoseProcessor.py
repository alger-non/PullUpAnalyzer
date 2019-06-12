import Utils
import cv2
import math


class PoseProcessor:
    def __init__(self):
        self.angle_threshold = 30
        self.states = ['hanging on straight arms', 'подъем', 'завершение', 'опускание']
        self.cur_state = None

    @staticmethod
    def is_arm_points_valid(point_a, point_b, point_c):
        unique_points = {point_a, point_b, point_c}
        return point_a and point_b and point_c and len(unique_points) == 3

    @staticmethod
    def get_angle_between_wrist_and_shoulder_in_left(points: list):
        return Utils.get_angle_between_vectors(Utils.get_vector_from_points(points['LWrist'], points['LElbow']),
                                               Utils.get_vector_from_points(points['LElbow'], points['LShoulder']))

    @staticmethod
    def get_angle_between_wrist_and_shoulder_in_right(points: list):
        return Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['RWrist'], points['RElbow']),
            Utils.get_vector_from_points(points['RElbow'], points['RShoulder']))

    def define_state(self, points, frame):
        requirements = [self.is_angle_in_arms_valid(points, frame), self.is_wrists_on_one_level(points, frame)]
        if all(requirements):
            self.cur_state = self.states[0]

        cv2.putText(frame, f'{self.cur_state}', (600, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4,
                    lineType=cv2.LINE_AA)

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
