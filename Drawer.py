import cv2
import skcuda


class Drawer:
    def __init__(self):
        pass

    @staticmethod
    def draw_skeleton(frame, points, pose_pairs):
        line_color = (0, 255, 255)

        for pair in pose_pairs:
            part_a = pair[0]
            part_b = pair[1]

            if points[part_a] and points[part_b]:
                cv2.line(frame, points[part_a], points[part_b], line_color, 3, lineType=cv2.LINE_AA)
                cv2.circle(frame, points[part_a], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.circle(frame, points[part_b], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

    @staticmethod
    def draw_numbered_joints(frame, points: dict, needed_points: dict):
        for joint, point in points.items():
            if not point:
                break
            joint_number = needed_points[joint]
            cv2.circle(frame, (point[0], point[1]), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
            cv2.putText(frame, f'{joint_number}', (point[0], point[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                        lineType=cv2.LINE_AA)

    @staticmethod
    def print_message(frame, message, x, y):
        cv2.putText(frame, message, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                    lineType=cv2.LINE_AA)
