import cv2


class Drawer:
    YELLOW_COLOR = (0, 255, 255)
    RED_COLOR = (0, 0, 255)
    BLUE_color = (255, 0, 0)
    GREEN_COLOR = (0, 255, 0)
    BLACK_COLOR = (0, 0, 0)

    def __init__(self):
        pass

    @staticmethod
    def draw_skeleton(frame, points, pose_pairs, line_color=YELLOW_COLOR, circle_color=RED_COLOR, radius=8,
                      line_thickness=3):

        for pair in pose_pairs:
            part_a = pair[0]
            part_b = pair[1]

            if points[part_a] and points[part_b]:
                cv2.line(frame, points[part_a], points[part_b], line_color, line_thickness, lineType=cv2.LINE_AA)
                Drawer.draw_point(frame, points[part_a], circle_color, radius)
                Drawer.draw_point(frame, points[part_b], circle_color, radius)

    @staticmethod
    def draw_numbered_joints(frame, points: dict, needed_points: dict, circle_color=YELLOW_COLOR, text_color=RED_COLOR,
                             radius=8, thickness=2, font_scale=1):
        for joint, point in points.items():
            if not point:
                break
            joint_number = needed_points[joint]
            cv2.putText(frame, f'{joint_number}', (point[0], point[1]), cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                        text_color, thickness,
                        lineType=cv2.LINE_AA)

    @staticmethod
    def print_message(frame, message, x, y, text_color=RED_COLOR, thickness=2, font_scale=1):
        cv2.putText(frame, message, (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness,
                    lineType=cv2.LINE_AA)

    @staticmethod
    def draw_point(frame, point, color, radius):
        cv2.circle(frame, (point[0], point[1]), radius, color, thickness=-1, lineType=cv2.FILLED)
