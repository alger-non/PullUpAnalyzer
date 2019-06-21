import numpy as np
import math
import cv2

body25_parts = {"Nose": 0,
              "Neck": 1,
              "RShoulder": 2,
              "RElbow": 3,
              "RWrist": 4,
              "LShoulder": 5,
              "LElbow": 6,
              "LWrist": 7,
              "MidHip": 8,
              "RHip": 9,
              "RKnee": 10,
              "RAnkle": 11,
              "LHip": 12,
              "LKnee": 13,
              "LAnkle": 14,
              "REye": 15,
              "LEye": 16,
              "REar": 17,
              "LEar": 18,
              "LBigToe": 19,
              "LSmallToe": 20,
              "LHeel": 21,
              "RBigToe": 22,
              "RSmallToe": 23,
              "RHeel": 24,
              "Background": 25}

def get_vector_module(vector: list):
    return pow(pow(vector[0], 2) + pow(vector[1], 2), 0.5)


def get_angle_between_vectors(vector_a: list, vector_b: list):
    vectors_product = np.dot(vector_a, vector_b)
    angle_cos = vectors_product / (get_vector_module(vector_a) * get_vector_module(vector_b))
    angle_in_radians = math.acos(angle_cos)
    degrees = math.degrees(angle_in_radians)
    return int(degrees)


def get_vector_from_points(point_a: list, point_b: list):
    vector = [point_a[0] - point_b[0], point_a[1] - point_b[1]]
    return vector


def extract_required_points(points_list, needed_points: dict):
    points = {}
    for joint, joint_number in needed_points.items():
        position = 3 * joint_number
        points[joint] = (int(points_list[position]), int(points_list[position+1]))
    return points
