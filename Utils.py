import numpy as np
import math





def get_vector_module(vector: list):
    return pow(pow(vector[0], 2) + pow(vector[1], 2), 0.5)


def get_angle_between_vectors(vector_a: list, vector_b: list):
    vectors_product = np.dot(vector_a, vector_b)
    angle_cos = vectors_product / (get_vector_module(vector_a) * get_vector_module(vector_b))
    #set cos-value range
    angle_cos = np.clip(angle_cos, -1, 1)
    angle_in_radians = math.acos(angle_cos)
    degrees = math.degrees(angle_in_radians)
    return int(degrees)


def get_vector_from_points(point_a: list, point_b: list):
    vector = [point_a[0] - point_b[0], point_a[1] - point_b[1]]
    return vector


def extract_required_json_points(points_list, needed_points: dict):
    points = {}
    for joint, joint_number in needed_points.items():
        position = 3 * joint_number
        x, y = (int(points_list[position]), int(points_list[position+1]))
        if (x, y) == (0, 0):
            points[joint] = None
        else:
            points[joint] = (x, y)
    return points


def extract_required_points(points_lists, needed_points):
    points = {}
    for joint, joint_number in needed_points.items():
        x, y = (int(x) for x in points_lists[joint_number][:2])
        if (x, y) == (0, 0):
            points[joint] = None
        else:
            points[joint] = (x, y)
    return points
