from Timer import Timer
from PoseProcessor import PoseProcessor
from Drawer import Drawer
from collections import deque
import cv2


class ResultsDrawer:
    OLD_REPEATS = 0
    OLD_FAILS = 0
    ANIMATION_DURATION_IN_SEC = 1
    ANIMATION_MIN_FONT_THICKNESS = 2
    ANIMATION_MAX_FONT_THICKNESS = 9

    ANIMATION_MIN_LINE_THICKNESS = 2
    ANIMATION_MAX_LINE_THICKNESS = 13

    def __init__(self, fps):
        self.fps = fps
        self.animation_queue_size = int(fps * ResultsDrawer.ANIMATION_DURATION_IN_SEC)
        self.pure_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.impure_reps_font_animation_queue = deque(maxlen=self.animation_queue_size)
        self.pure_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)
        self.impure_reps_line_animation_queue = deque(maxlen=self.animation_queue_size)
        self.timer = Timer(self.fps)

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
            self.generate_font_animation_queue(self.pure_reps_font_animation_queue, now_repeats,
                                               ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS,
                                               ResultsDrawer.ANIMATION_MAX_FONT_THICKNESS, Drawer.RED_COLOR,
                                               Drawer.WHITE_COLOR)
            self.generate_line_animation_queue(self.pure_reps_line_animation_queue,
                                               ResultsDrawer.ANIMATION_MIN_LINE_THICKNESS,
                                               ResultsDrawer.ANIMATION_MAX_LINE_THICKNESS, Drawer.BLACK_COLOR,
                                               Drawer.GREEN_COLOR)
            ResultsDrawer.OLD_REPEATS = now_repeats

        Drawer.print_message(frame, 'Reps: ', x, y)
        if not self.pure_reps_font_animation_queue:
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_repeats}')
        else:
            self.draw_animation_from_queue(frame, self.pure_reps_font_animation_queue, x + 100, y)

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

    def fail(self, frame, phase: PoseProcessor, x, y):
        now_fails = phase.impure_repeats
        if now_fails != ResultsDrawer.OLD_FAILS:
            self.generate_font_animation_queue(self.impure_reps_font_animation_queue, now_fails,
                                               ResultsDrawer.ANIMATION_MIN_FONT_THICKNESS,
                                               ResultsDrawer.ANIMATION_MAX_FONT_THICKNESS, Drawer.RED_COLOR,
                                               Drawer.ORANGE_COLOR)
            self.generate_line_animation_queue(self.impure_reps_line_animation_queue,
                                               ResultsDrawer.ANIMATION_MIN_LINE_THICKNESS,
                                               ResultsDrawer.ANIMATION_MAX_LINE_THICKNESS, Drawer.BLACK_COLOR,
                                               Drawer.RED_COLOR)
            ResultsDrawer.OLD_FAILS = now_fails
        Drawer.print_message(frame, f'Fails: ', x, y)

        if not self.impure_reps_font_animation_queue:
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_fails}')
        else:
            self.draw_animation_from_queue(frame, self.impure_reps_font_animation_queue, x + 100, y)

    @staticmethod
    def draw_animation_from_queue(frame, animation_queue: deque, x, y):
        draw_data = animation_queue.pop()
        Drawer.print_message_with_text_edging(frame, x, y, draw_data[0], draw_data[1], draw_data[2])

    def time(self, frame, phase, x, y):

        self.timer.inc()
        if ResultsDrawer.OLD_REPEATS == 0 and phase.cur_state in phase.states[0]:
            self.timer.reset()

        cur_time = self.timer.get_time()
        # save time in moment pull-up execution
        if phase.cur_state in phase.states[2]:
            self.timer.store_time()
        if phase.cur_state in phase.states[4]:
            cur_time = self.timer.get_stored_time()
        min, sec = int(cur_time / 60), int(cur_time % 60)
        Drawer.print_message(frame, f'Time: {min}:{sec:02}', x, y)

    @staticmethod
    def draw_info_region(frame):
        overlay = frame.copy()
        x, y, w, h = 0, 0, 400, 100
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
        alpha = 0.7
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def draw_line_between_wrists(self, frame, points):
        color = Drawer.BLACK_COLOR
        thickness = 3
        if self.pure_reps_line_animation_queue:
            thickness, color = self.pure_reps_line_animation_queue.pop()
        elif self.impure_reps_line_animation_queue:
            thickness, color = self.impure_reps_line_animation_queue.pop()

        cv2.line(frame, points['LWrist'], points['RWrist'], color, thickness)

    def display_info(self, frame, phase: PoseProcessor):
        new_frame = self.draw_info_region(frame)
        self.repeats(new_frame, phase, 0, 30)
        self.fail(new_frame, phase, 200, 30)
        self.phase(new_frame, phase, 200, 45, 30)
        self.time(new_frame, phase, 0, 75)
        return new_frame


    def display_skeleton(self, frame, points, required_points):
        Drawer.draw_skeleton(frame, points, required_points)
        self.draw_line_between_wrists(frame, points)
