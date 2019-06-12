import numpy as np
import math

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


def set_model(model_name: str):
    if model_name is "COCO":
        protoFile = "pose/coco/pose_deploy_linevec.prototxt"
        weightsFile = "pose/coco/pose_iter_440000.caffemodel"

    elif model_name is "MPI":
        protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
        weightsFile = "pose/mpi/pose_iter_160000.caffemodel"

    elif model_name is "BODY_25":
        protoFile = "pose/body_25/pose_deploy.prototxt"
        weightsFile = "pose/body_25/pose_iter_584000.caffemodel"

    return (protoFile, weightsFile)


