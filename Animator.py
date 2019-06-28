from collections import deque
from Drawer import Drawer
import cv2


class Animator:
    """Class performing animation."""

    def __init__(self, animation_queue_size, animation_min_font_thickness, animation_max_font_thickness,
                 animation_min_line_thickness, animation_max_line_thickness):
        self.animation_queue_size = animation_queue_size
        self.clean_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.unclean_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.clean_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)
        self.unclean_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)

        self.animation_min_font_thickness = animation_min_font_thickness
        self.animation_max_font_thickness = animation_max_font_thickness
        self.animation_min_line_thickness = animation_min_line_thickness
        self.animation_max_line_thickness = animation_max_line_thickness

    def generate_clean_pull_up_animation(self, new_value):
        self.clean_reps_line_animation_queue = self.generate_animation(new_value, self.clean_reps_font_animation_queue,
                                                                       self.clean_reps_line_animation_queue,
                                                                       Drawer.GREEN_COLOR)

    def generate_unclean_pull_up_animation(self, new_value):
        self.generate_animation(new_value, self.unclean_reps_font_animation_queue,
                                self.unclean_reps_line_animation_queue, Drawer.RED_COLOR)

    def generate_animation(self, new_value, font_animation_queue, line_animation_queue, line_animation_color):
        self.generate_font_animation_queue(new_value, font_animation_queue,
                                           self.animation_min_font_thickness,
                                           self.animation_max_font_thickness, Drawer.RED_COLOR,
                                           Drawer.WHITE_COLOR)
        self.generate_line_animation_queue(line_animation_queue, self.animation_min_line_thickness,
                                           self.animation_max_line_thickness, Drawer.DEFAULT_COLOR,
                                           line_animation_color)
        return line_animation_queue

    def generate_font_animation_queue(self, new_value, animation_queue: deque, animation_min_font_thickness,
                                      animation_max_font_thickness, animation_initial_color,
                                      animation_final_color):

        thicknesses = self.generate_thickness_range(animation_min_font_thickness, animation_max_font_thickness)
        colors = self.generate_color_range(animation_initial_color, animation_final_color)
        new_values = [new_value for i in range(self.animation_queue_size)]
        for i in range(self.animation_queue_size):
            animation_queue.append((new_values[i], thicknesses[i], colors[i]))

    def generate_color_range(self, animation_initial_color, animation_final_color):
        color_step = self.define_bgr_color_step(animation_initial_color,
                                                animation_final_color)
        colors = [animation_initial_color]
        size = self.animation_queue_size - 1
        for i in range(size // 2):
            colors.append(self.add_color_step_to_color(colors[-1], color_step))
        for i in range(size - (size // 2)):
            colors.append(self.sub_color_step_from_color(colors[-1], color_step))

        return colors

    def generate_thickness_range(self, animation_min_font_thickness, animation_max_font_thickness):
        thickness_step = (animation_max_font_thickness - animation_min_font_thickness + 1) / self.animation_queue_size
        thicknesses = [animation_min_font_thickness]
        thickness = animation_min_font_thickness
        size = self.animation_queue_size - 1
        for i in range(size // 2):
            thickness += thickness_step
            thicknesses.append(int(thickness))
        for i in range(size - (size // 2)):
            thickness -= thickness_step
            thicknesses.append(int(thickness))
        return thicknesses

    def generate_line_animation_queue(self, line_animation_queue, animation_min_font_thickness,
                                      animation_max_font_thickness, animation_initial_color,
                                      animation_final_color):
        thicknesses = self.generate_thickness_range(animation_min_font_thickness, animation_max_font_thickness)
        colors = self.generate_color_range(animation_initial_color, animation_final_color)
        for i in range(self.animation_queue_size):
            line_animation_queue.append((thicknesses[i], colors[i]))

    def play_pull_up_line_animation(self, frame, point_a, point_b):
        thickness, color = None, None
        if self.clean_reps_line_animation_queue:
            thickness, color = self.clean_reps_line_animation_queue.pop()
        elif self.unclean_reps_line_animation_queue:
            thickness, color = self.unclean_reps_line_animation_queue.pop()
        cv2.line(frame, point_a, point_b, color, thickness)

    @staticmethod
    def play_pull_up_font_animation(frame, font_animation_queue: deque, x, y):
        draw_data = font_animation_queue.pop()
        Drawer.print_message_with_text_edging(frame, x, y, draw_data[0], thickness=draw_data[1],
                                              text_color=draw_data[2])

    def play_clean_pull_up_font_animation(self, frame, x, y):
        self.play_pull_up_font_animation(frame, self.clean_reps_font_animation_queue,
                                         x, y)

    def play_unclean_pull_up_font_animation(self, frame, x, y):
        self.play_pull_up_font_animation(frame, self.unclean_reps_font_animation_queue, x, y)

    def define_bgr_color_step(self, initial_color: tuple, final_color: tuple):
        iters = int(self.animation_queue_size / 2)
        b_step = int((final_color[0] - initial_color[0]) / iters)
        g_step = int((final_color[1] - initial_color[1]) / iters)
        r_step = int((final_color[2] - initial_color[2]) / iters)
        return b_step, g_step, r_step

    @staticmethod
    def add_color_step_to_color(color: tuple, color_step: tuple):
        return [sum(color_pair) for color_pair in zip(color, color_step)]

    @staticmethod
    def sub_color_step_from_color(color: tuple, color_step: tuple):
        return [sum([color_pair[0], -color_pair[1]]) for color_pair in zip(color, color_step)]

    def is_clean_pull_up_font_animation_playing(self):
        return self.clean_reps_font_animation_queue

    def is_unclean_pull_up_font_animation_playing(self):
        return self.unclean_reps_font_animation_queue

    def is_pull_up_line_animation_playing(self):
        return self.clean_reps_font_animation_queue or self.unclean_reps_line_animation_queue
