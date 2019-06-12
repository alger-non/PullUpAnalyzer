import Utils
import cv2
import math

class PoseProcessor:
    def __init__(self):
        self.angle_threshold = 30
        self.states = ['hanging on straight arms', 'подъем', 'завершение', 'опускание']
        self.cur_state = None

    def get_angle_between_wrist_and_shoulder_in_left(self, points: list):
        return Utils.get_angle_between_vectors(Utils.get_vector_from_points(points['LWrist'], points['LElbow']),
            Utils.get_vector_from_points(points['LElbow'], points['LShoulder']))

    def get_angle_between_wrist_and_shoulder_in_right(self, points: list):
        return Utils.get_angle_between_vectors(
            Utils.get_vector_from_points(points['RWrist'], points['RElbow']),
            Utils.get_vector_from_points(points['RElbow'], points['RShoulder']))



    def define_state(self, points, frame):
        angle_of_left_arm, angle_of_right_arm = math.inf, math.inf
        if Utils.is_arm_points_valid(points['LWrist'], points['LElbow'], points['LShoulder']):
            angle_of_left_arm = self.get_angle_between_wrist_and_shoulder_in_left(points)
            cv2.putText(frame, f'left arm: {angle_of_left_arm}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)

        if Utils.is_arm_points_valid(points['RWrist'], points['RElbow'], points['RShoulder']):
            angle_of_right_arm = self.get_angle_between_wrist_and_shoulder_in_right(points)
            cv2.putText(frame, f'right arm: {angle_of_right_arm}', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                        2,
                        lineType=cv2.LINE_AA)

        if angle_of_left_arm < self.angle_threshold and angle_of_right_arm < self.angle_threshold:
            cv2.putText(frame, f'{self.states[0]}', (600, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4,
                        lineType=cv2.LINE_AA)
