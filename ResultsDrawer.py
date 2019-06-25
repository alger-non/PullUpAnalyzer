import cv2
from PoseProcessor import PoseProcessor
from Drawer import Drawer
from collections import deque


class ResultsDrawer:
    OLD_REPEATS = 0
    OLD_FAILS = 0
    ANIMATION_DURATION_IN_SEC = 1
    ANIMATION_MIN_FONT_THICKNESS = 2
    ANIMATION_MAX_FONT_THICKNESS = 9
    ANIMATION_INITIAL_COLOR = Drawer.RED_COLOR
    ANIMATION_FINAL_COLOR = Drawer.WHITE_COLOR

    def __init__(self, fps):
        self.fps = fps
        self.animation_queue_size = int(fps * ResultsDrawer.ANIMATION_DURATION_IN_SEC)
        self.pure_reps_animation_queue = deque(maxlen=self.animation_queue_size)
        self.impure_reps_animation_queue = deque(maxlen=self.animation_queue_size)

    @staticmethod
    def phase(frame, phase: PoseProcessor, x, y, side):
        Drawer.print_message(frame, 'Phase:', x, y + side)
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
            Drawer.glyph_undefined(frame, x + 10, y + 30)

    # @staticmethod
    # def misguided_attempt(frame, x, y):
    #     Drawer.print_message(frame, 'Misguided attempt!.', x, y)

    def repeats(self, frame, phase: PoseProcessor, x, y):
        now_repeats = phase.pure_repeats
        if ResultsDrawer.OLD_REPEATS != now_repeats:
            self.generate_animation_queue(self.pure_reps_animation_queue, now_repeats)
            ResultsDrawer.OLD_REPEATS = now_repeats

        Drawer.print_message(frame, 'Reps: ', x, y)
        if self.is_pure_reps_animation_queue_empty():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_repeats}')
        else:
            self.draw_animation_from_queue(frame, self.pure_reps_animation_queue, x, y)

    def is_pure_reps_animation_queue_empty(self):
        return False if self.pure_reps_animation_queue else True

    def is_impure_reps_animation_queue_empty(self):
        return False if self.impure_reps_animation_queue else True

    def generate_animation_queue(self, animation_queue: deque, new_value):
        font_thickness_step = (
                                          ResultsDrawer.ANIMATION_MAX_FONT_THICKNESS - ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS + 1) / self.animation_queue_size
        font_thickness = ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS
        color_step = self.define_bgr_color_step(ResultsDrawer.ANIMATION_INITIAL_COLOR,
                                                ResultsDrawer.ANIMATION_FINAL_COLOR)
        color = ResultsDrawer.ANIMATION_INITIAL_COLOR

        for i in range(int(self.animation_queue_size / 2)):
            font_thickness += font_thickness_step
            color = self.add_color_step_to_color(color, color_step)
            animation_queue.append((new_value, int(font_thickness), color))

        for i in range(int(self.animation_queue_size / 2)):
            font_thickness -= font_thickness_step
            color = self.sub_color_step_from_color(color, color_step)
            animation_queue.append((new_value, int(font_thickness), color))

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

    def fail(self, frame, phase: PoseProcessor, x, y):
        now_fails = phase.impure_repeats
        if now_fails != ResultsDrawer.OLD_FAILS:
            self.generate_animation_queue(self.impure_reps_animation_queue, now_fails)
            ResultsDrawer.OLD_FAILS = now_fails
        Drawer.print_message(frame, f'Fails: ', x, y)

        if self.is_impure_reps_animation_queue_empty():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_fails}')
        else:
            self.draw_animation_from_queue(frame, self.impure_reps_animation_queue, x, y)

    @staticmethod
    def draw_animation_from_queue(frame, animation_queue: deque, x, y):
        draw_data = animation_queue.pop()
        Drawer.print_message_with_text_edging(frame, x + 100, y, draw_data[0], draw_data[1], draw_data[2])

    def time(self, frame, x, y, cur_frame_num):
        cp_fps = self.fps
        sec = cur_frame_num / cp_fps
        Drawer.print_message(frame, f'Time: {sec:.3f} sec', x, y)

    def display_info(self, frame, phase: PoseProcessor, cur_frame_num):
        self.repeats(frame, phase, 0, 30)
        self.fail(frame, phase, 0, 65)
        self.phase(frame, phase, 0, 75, 30)
        self.time(frame, 0, 140, cur_frame_num)
