import numpy as np
import math
import cv2
from PoseProcessor import body25_parts



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


def get_model_by_name(model_name: str):
    if model_name is "COCO":
        proto_file = "pose/coco/pose_deploy_linevec.prototxt"
        weights_file = "pose/coco/pose_iter_440000.caffemodel"

    elif model_name is "MPI":
        proto_file = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
        weights_file = "pose/mpi/pose_iter_160000.caffemodel"

    elif model_name is "BODY_25":
        proto_file = "pose/body_25/pose_deploy.prototxt"
        weights_file = "pose/body_25/pose_iter_584000.caffemodel"

    return proto_file, weights_file


def extract_required_points(points_list, needed_points: dict):
    points = {}
    for joint, joint_number in needed_points.items():
        position = 3 * joint_number
        points[joint] = (int(points_list[position]), int(points_list[position+1]))
    return points
