import cv2
from PoseProcessor import PoseProcessor
from Drawer import Drawer
from collections import deque


class ResultsDrawer:
    OLD_REPEATS = 0
    OLD_FAILS = 0
    ANIMATION_QUEUE_SIZE = 30
    ANIMATION_MIN_FONT_THICKNESS = 2
    ANIMATION_MAX_FONT_THICKNESS = 13
    ANIMATION_INITIAL_COLOR = Drawer.RED_COLOR
    ANIMATION_FINAL_COLOR = Drawer.WHITE_COLOR

    def __init__(self):
        self.animation_queue = deque(maxlen=ResultsDrawer.ANIMATION_QUEUE_SIZE)

    def phase(self, frame, phase: PoseProcessor, x, y, side):
        Drawer.print_message(frame, 'Phase:', x, y + side, Drawer.BLACK_COLOR)
        x += 100
        if phase.cur_state == 'hanging in the bottom position':
            Drawer.glyph_bottom_hanging(frame, x, y, side)
        elif phase.cur_state == 'hanging in the top position':
            Drawer.glyph_top_hanging(frame, x, y, side)
        elif phase.cur_state == 'ascending':
            Drawer.glyph_asc(frame, x, y, side)
        elif phase.cur_state == 'descending':
            Drawer.glyph_desc(frame, x, y, side)
        else:
            Drawer.glyph_undefined(frame, x, y)

    @staticmethod
    def misguided_attempt(frame, x, y):
        Drawer.print_message(frame, 'Misguided attempt!.', x, y)

    def repeats(self, frame, phase: PoseProcessor, x, y):
        now_repeats = phase.pure_repeats
        color = Drawer.GREEN_COLOR
        if ResultsDrawer.OLD_REPEATS != now_repeats:
            self.generate_animation_queue(now_repeats)
            ResultsDrawer.OLD_REPEATS = now_repeats

        if now_repeats == 0 and phase._failed_state_detection_attempts != 0:
            ResultsDrawer.misguided_attempt(frame, x + 210, y)
            color = Drawer.RED_COLOR

        Drawer.print_message(frame, 'Reps: ', x, y, color)

        if self.is_animation_queue_empty():
            Drawer.print_message(frame, f'{phase.pure_repeats}', x + 100, y)
        else:
            draw_data = self.animation_queue.pop()
            print('draw data is ', draw_data[0], draw_data[1])
            Drawer.print_message(frame, f'{draw_data[0]}', x + 100, y, thickness=draw_data[1], text_color=draw_data[2], font_scale=1.1)

    def is_animation_queue_empty(self):
        return False if self.animation_queue else True

    def generate_animation_queue(self, new_value):
        font_thickness_step = (ResultsDrawer.ANIMATION_MAX_FONT_THICKNESS - ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS + 1) / ResultsDrawer.ANIMATION_QUEUE_SIZE
        font_thickness = ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS
        color_step = self.define_bgr_color_step(ResultsDrawer.ANIMATION_INITIAL_COLOR, ResultsDrawer.ANIMATION_FINAL_COLOR, ResultsDrawer.ANIMATION_QUEUE_SIZE)
        color = ResultsDrawer.ANIMATION_INITIAL_COLOR

        for i in range(int(ResultsDrawer.ANIMATION_QUEUE_SIZE / 2) + 1):
            font_thickness += font_thickness_step
            color = self.add_color_step_to_color(color, color_step)
            self.animation_queue.append((new_value, int(font_thickness), color))

        for i in range(int(ResultsDrawer.ANIMATION_QUEUE_SIZE / 2) + 1):
            font_thickness -= font_thickness_step
            color = self.sub_color_step_from_color(color, color_step)
            self.animation_queue.append((new_value, int(font_thickness), color))
        print(self.animation_queue)


    def define_bgr_color_step(self, initial_color: tuple, final_color: tuple, iterations_num):
        iters = int(iterations_num / 2)
        b_step = int((final_color[0] - initial_color[0]) / iters)
        g_step = int((final_color[1] - initial_color[1]) / iters)
        r_step = int((final_color[2] - initial_color[2]) / iters)
        return b_step, g_step, r_step

    def add_color_step_to_color(self, color: tuple, color_step: tuple):
        return [sum(color_pair) for color_pair in zip(color, color_step)]

    def sub_color_step_from_color(self, color: tuple, color_step: tuple):
        return [sum([color_pair[0], -color_pair[1]]) for color_pair in zip(color, color_step)]

    @staticmethod
    def fail(frame, phase: PoseProcessor, x, y):
        now_fails = phase._failed_state_detection_attempts
        if now_fails != ResultsDrawer.OLD_FAILS:
            Drawer.glyph_cross(frame, x + 200, y)
            ResultsDrawer.OLD_FAILS = now_fails
        Drawer.print_message(frame, f'Fails: {now_fails}', x, y)

    @staticmethod
    def time(cap, frame, x, y):
        cp_fps = int(cap.get(cv2.CAP_PROP_FPS))
        cp_current = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        sec = cp_current / cp_fps
        Drawer.print_message(frame, f'Time: {sec:.3f} sec', x, y, Drawer.BLUE_COLOR)

    def display_info(self, frame, cap, phase: PoseProcessor):
        self.repeats(frame, phase, 0, 30)
        self.fail(frame, phase, 0, 65)
        self.phase(frame, phase, 0, 75, 30)
        self.time(cap, frame, 0, 140)
