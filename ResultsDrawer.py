from Timer import Timer
from PhaseQualifier import PhaseQualifier
from Drawer import Drawer
from collections import deque
import cv2


class ResultsDrawer:

    def __init__(self, fps, animation_duration_in_sec=1, animation_min_font_thickness=2, animation_max_font_thickness=9,
                 animation_min_line_thickness=2, animation_max_line_thickness=13):
        self.fps = fps
        self.old_reps = 0
        self.old_fails = 0
        self.animation_duration_in_sec = animation_duration_in_sec
        self.animation_min_font_thickness = animation_min_font_thickness
        self.animation_max_font_thickness = animation_max_font_thickness
        self.animation_min_line_thickness = animation_min_line_thickness
        self.animation_max_line_thickness = animation_max_line_thickness
        self.animation_queue_size = int(fps * self.animation_duration_in_sec)
        self.pure_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.impure_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.pure_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)
        self.impure_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)
        self.timer = Timer(self.fps)

    @staticmethod
    def draw_phase(frame, phase: PhaseQualifier, x, y, side):

        Drawer.print_message(frame, 'Phase:', x, y + side)
        x += 100
        if phase.cur_state == 'beginning':
            Drawer.glyph_bottom_hanging(frame, x, y, side)
        elif phase.cur_state == 'chinning':
            Drawer.glyph_top_hanging(frame, x, y, side)
        elif phase.cur_state == 'pulling':
            Drawer.glyph_asc(frame, x, y, side)
        elif phase.cur_state == 'lowering':
            Drawer.glyph_desc(frame, x, y, side)
        else:
            Drawer.glyph_undefined(frame, x + 10, y + 30)

    def print_repeats(self, frame, phase: PhaseQualifier, x, y):
        now_repeats = phase.clean_repeats
        if self.old_reps != now_repeats:
            self.generate_animation(self.pure_reps_font_animation_queue, now_repeats, self.pure_reps_line_animation_queue)
            self.old_reps = now_repeats

        Drawer.print_message(frame, 'Reps: ', x, y)
        if not self.pure_reps_font_animation_queue:
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_repeats}')
        else:
            self.draw_animation_from_queue(frame, self.pure_reps_font_animation_queue, x + 100, y)

    def generate_animation(self, font_animation_queue, new_value, line_animation_queue):
        self.generate_font_animation_queue(font_animation_queue, new_value,
                                           self.animation_min_font_thickness,
                                           self.animation_max_font_thickness, Drawer.RED_COLOR,
                                           Drawer.WHITE_COLOR)
        self.generate_line_animation_queue(line_animation_queue,
                                           self.animation_min_line_thickness,
                                           self.animation_max_line_thickness, Drawer.YELLOW_COLOR,
                                           Drawer.GREEN_COLOR)

    def generate_font_animation_queue(self, animation_queue: deque, new_value, animation_min_font_thickness,
                                      animation_max_font_thickness, animation_initial_color,
                                      animation_final_color):
        font_thickness_step = (
                                      animation_max_font_thickness - animation_min_font_thickness + 1) / self.animation_queue_size
        font_thickness = animation_min_font_thickness
        color_step = self.define_bgr_color_step(animation_initial_color,
                                                animation_final_color)
        color = animation_initial_color

        for i in range(int(self.animation_queue_size / 2)):
            font_thickness += font_thickness_step
            color = self.add_color_step_to_color(color, color_step)
            animation_queue.append((new_value, int(font_thickness), color))

        for i in range(int(self.animation_queue_size / 2)):
            font_thickness -= font_thickness_step
            color = self.sub_color_step_from_color(color, color_step)
            animation_queue.append((new_value, int(font_thickness), color))

    def generate_line_animation_queue(self, animation_queue: deque, animation_min_font_thickness,
                                      animation_max_font_thickness, animation_initial_color,
                                      animation_final_color):
        line_thickness_step = (
                                      animation_max_font_thickness - animation_min_font_thickness + 1) / self.animation_queue_size
        line_thickness = animation_min_font_thickness
        color_step = self.define_bgr_color_step(animation_initial_color,
                                                animation_final_color)
        color = animation_initial_color

        for i in range(int(self.animation_queue_size / 2)):
            line_thickness += line_thickness_step
            color = self.add_color_step_to_color(color, color_step)
            animation_queue.append((int(line_thickness), color))

        for i in range(int(self.animation_queue_size / 2)):
            line_thickness -= line_thickness_step
            color = self.sub_color_step_from_color(color, color_step)
            animation_queue.append((int(line_thickness), color))

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

    def print_fails(self, frame, phase: PhaseQualifier, x, y):
        now_fails = phase.unclean_repeats
        if now_fails != self.old_fails:
            self.generate_animation(self.impure_reps_font_animation_queue, now_fails, self.impure_reps_line_animation_queue)
            self.old_fails = now_fails
        Drawer.print_message(frame, f'Fails: ', x, y)

        if not self.impure_reps_font_animation_queue:
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_fails}', text_color=Drawer.DARK_RED_COLOR,
                                                  border_size=3, border_color=Drawer.ORANGE_COLOR)
        else:
            self.draw_animation_from_queue(frame, self.impure_reps_font_animation_queue, x + 100, y)

    @staticmethod
    def draw_animation_from_queue(frame, animation_queue: deque, x, y):
        draw_data = animation_queue.pop()
        Drawer.print_message_with_text_edging(frame, x, y, draw_data[0], thickness=draw_data[1],
                                              text_color=draw_data[2])

    def print_elapsed_time(self, frame, phase, x, y):

        self.timer.inc()
        if self.old_reps == 0 and phase.cur_state == phase.phases[0]:
            self.timer.reset()

        cur_time = self.timer.get_time()
        # save time in moment pull-up execution
        if phase.cur_state in phase.phases[2]:
            self.timer.store_time()
        if phase.cur_state in phase.phases[4]:
            cur_time = self.timer.get_stored_time()
        min, sec = int(cur_time / 60), int(cur_time % 60)
        Drawer.print_message(frame, f'Time: {min}:{sec:02}', x, y)

    @staticmethod
    def draw_info_region(frame):
        overlay = frame.copy()
        x, y, w, h = 0, 0, 355, 80
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
        alpha = 0.7
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def draw_line_between_wrists(self, frame, points):
        color = Drawer.YELLOW_COLOR
        thickness = 3
        if self.pure_reps_line_animation_queue:
            thickness, color = self.pure_reps_line_animation_queue.pop()
        elif self.impure_reps_line_animation_queue:
            thickness, color = self.impure_reps_line_animation_queue.pop()

        cv2.line(frame, points['LWrist'], points['RWrist'], color, thickness)

    @staticmethod
    def draw_chin_point(frame, phase: PhaseQualifier):
        if phase.chin_point:
            cv2.circle(frame, tuple(phase.chin_point), 8, Drawer.BLUE_COLOR, thickness=-1, lineType=cv2.FILLED)

    def display_info(self, frame, phase: PhaseQualifier):
        new_frame = self.draw_info_region(frame)
        self.print_repeats(new_frame, phase, 0, 30)
        self.print_fails(new_frame, phase, 200, 30)
        self.draw_phase(new_frame, phase, 200, 45, 30)
        self.print_elapsed_time(new_frame, phase, 0, 75)
        return new_frame

    @staticmethod
    def display_skeleton(frame, points, required_points):
        Drawer.draw_skeleton(frame, points, required_points)
