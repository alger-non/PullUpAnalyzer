import os
import numpy as np
from Timer import Timer
from PhaseQualifier import PhaseQualifier
from Drawer import Drawer
import cv2
from Animator import Animator


class ResultsDrawer:
    """Class drawing the general information about the pull up process."""

    FAILS_NUMBERS_BORDER_SIZE = 1
    REPS_NUMBERS_BORDER_SIZE = 2
    DEFAULT_FONT = cv2.FONT_HERSHEY_COMPLEX_SMALL
    GENERAL_FONT_THICKNESS = Drawer.DEFAULT_FONT_THICKNESS
    REPS_NUMBERS_FONT_THICKNESS = Drawer.DEFAULT_FONT_THICKNESS + REPS_NUMBERS_BORDER_SIZE
    FAILS_NUMBERS_FONT_THICKNESS = Drawer.DEFAULT_FONT_THICKNESS + FAILS_NUMBERS_BORDER_SIZE
    TIME_FONT_THICKNESS = 1

    REPS_LABEL = 'Reps: '
    FAILS_LABEL = 'Fails: '
    TIME_LABEL = 'Time: '
    MAX_VALUE = '999'
    MAX_TIME_VALUE = '99:59'

    LEFT_PADDING = 10
    REPS_LABEL_SIZE = cv2.getTextSize(REPS_LABEL, DEFAULT_FONT, 1, GENERAL_FONT_THICKNESS)[0][0]
    FAILS_LABELS_SIZE = cv2.getTextSize(FAILS_LABEL, DEFAULT_FONT, 1, GENERAL_FONT_THICKNESS)[0][0]
    MAX_TIME_VALUE_SIZE = cv2.getTextSize(f'{TIME_LABEL}{MAX_TIME_VALUE}', DEFAULT_FONT, 1, TIME_FONT_THICKNESS)[0][0]
    REPS_NUMBERS_SIZE = cv2.getTextSize(MAX_VALUE, DEFAULT_FONT, 1, REPS_NUMBERS_FONT_THICKNESS)[0][0]
    FAILS_NUMBERS_SIZE = cv2.getTextSize(MAX_VALUE, DEFAULT_FONT, 1, FAILS_NUMBERS_FONT_THICKNESS)[0][0]

    MAX_VALUE_POSITION_X = LEFT_PADDING + max(REPS_LABEL_SIZE, FAILS_LABELS_SIZE)
    MAX_WIDTH = max(MAX_VALUE_POSITION_X + max(REPS_NUMBERS_SIZE, FAILS_NUMBERS_SIZE), LEFT_PADDING + MAX_TIME_VALUE_SIZE)

    def __init__(self, fps, animation_duration_in_sec=1, animation_min_font_thickness=2, animation_max_font_thickness=9,
                 animation_min_line_thickness=2, animation_max_line_thickness=13):
        self.old_reps = 0
        self.old_fails = 0
        self.animation_duration_in_sec = animation_duration_in_sec
        queue_size = int(fps * self.animation_duration_in_sec)
        self.animator = Animator(queue_size, animation_min_font_thickness, animation_max_font_thickness,
                                 animation_min_line_thickness, animation_max_line_thickness)
        self.timer = Timer(fps)

    def print_repeats(self, frame, phase_qualifier: PhaseQualifier, x, y):
        now_repeats = phase_qualifier.clean_repeats
        if self.old_reps != now_repeats:
            self.animator.generate_clean_pull_up_animation(now_repeats)
            self.old_reps = now_repeats

        Drawer.print_message(frame, ResultsDrawer.REPS_LABEL, x, y, font=ResultsDrawer.DEFAULT_FONT)

        x = self.get_reps_numbers_position_by_cur_value(self.old_reps)
        if not self.animator.is_clean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x, y, f'{now_repeats}',
                                                  border_size=ResultsDrawer.REPS_NUMBERS_BORDER_SIZE)
        else:
            self.animator.play_clean_pull_up_font_animation(frame, x, y)

    @staticmethod
    def get_reps_numbers_position_by_cur_value(cur_value):
        cur_value_text_width = cv2.getTextSize(str(cur_value), ResultsDrawer.DEFAULT_FONT, 1, ResultsDrawer.REPS_NUMBERS_FONT_THICKNESS)[0][0]
        target_x = ResultsDrawer.MAX_VALUE_POSITION_X + (ResultsDrawer.REPS_NUMBERS_SIZE - cur_value_text_width)
        return target_x

    @staticmethod
    def get_fails_numbers_position_by_cur_value(cur_value):
        cur_value_text_width = \
        cv2.getTextSize(str(cur_value), ResultsDrawer.DEFAULT_FONT, 1, ResultsDrawer.FAILS_NUMBERS_FONT_THICKNESS)[0][0]
        target_x = ResultsDrawer.MAX_VALUE_POSITION_X + (ResultsDrawer.FAILS_NUMBERS_SIZE - cur_value_text_width)
        return target_x

    def print_fails(self, frame, phase_qualifier: PhaseQualifier, x, y):
        now_fails = phase_qualifier.unclean_repeats
        if now_fails != self.old_fails:
            self.animator.generate_unclean_pull_up_animation(now_fails)
            self.old_fails = now_fails
        Drawer.print_message(frame, ResultsDrawer.FAILS_LABEL, x, y, font_scale=1, thickness=1, font=ResultsDrawer.DEFAULT_FONT)

        x = self.get_fails_numbers_position_by_cur_value(self.old_fails)
        if not self.animator.is_unclean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x, y, f'{now_fails}', text_color=Drawer.DARK_RED_COLOR,
                                                  border_size=ResultsDrawer.FAILS_NUMBERS_BORDER_SIZE,
                                                  border_color=Drawer.ORANGE_COLOR)
        else:
            self.animator.play_unclean_pull_up_font_animation(frame, x, y)

    def print_elapsed_time(self, frame, phase_qualifier, x, y):
        self.timer.inc()
        if self.old_reps == 0 and phase_qualifier.cur_state == phase_qualifier.phases[0]:
            self.timer.reset()

        cur_time = self.timer.get_time()
        # save time in moment pull-up execution
        if phase_qualifier.cur_state in phase_qualifier.phases[2]:
            self.timer.store_time()
        if phase_qualifier.cur_state in phase_qualifier.phases[4]:
            cur_time = self.timer.get_stored_time()
        mins, secs = int(cur_time / 60), int(cur_time % 60)
        Drawer.print_message(frame, f'{ResultsDrawer.TIME_LABEL}{mins}:{secs:02}', x, y, thickness=ResultsDrawer.TIME_FONT_THICKNESS,
                             font=ResultsDrawer.DEFAULT_FONT, text_color=Drawer.RED_COLOR)

    @staticmethod
    def draw_info_region(frame, phase_qualifier: PhaseQualifier):
        overlay = frame.copy()
        Drawer.draw_rectangle(overlay, 0, 0, ResultsDrawer.MAX_WIDTH, 95)
        alpha = 0.7
        new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        return ResultsDrawer.draw_glyph(new_frame, phase_qualifier)

    @staticmethod
    def draw_glyph(frame, phase_qualifier: PhaseQualifier):
        overlay = frame.copy()
        icons_dir = 'icons'
        size = ResultsDrawer.MAX_WIDTH
        alpha = 0.7
        cur_icon_name = os.path.join(icons_dir, f'{phase_qualifier.cur_state}.png')
        if not os.path.isfile(os.path.abspath(cur_icon_name)):
            print(f"{cur_icon_name} isn't found.")
            return frame
        pictogram = cv2.imread(cur_icon_name)
        pictogram = cv2.resize(pictogram, (size, size), interpolation=cv2.INTER_AREA)
        init_y = 95
        Drawer.draw_rectangle(overlay, 0, init_y, size, size)
        overlay[init_y:init_y + size, :size] = pictogram
        new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        return new_frame

    def draw_line_between_wrists(self, frame, points):
        l_wrist, r_wrist = points['LWrist'], points['RWrist']
        if not (l_wrist and r_wrist):
            return
        if self.animator.is_pull_up_line_animation_playing():
            self.animator.play_pull_up_line_animation(frame, l_wrist, r_wrist)
        else:
            cv2.line(frame, l_wrist, r_wrist, Drawer.DEFAULT_COLOR, Drawer.DEFAULT_LINE_THICKNESS)

    @staticmethod
    def draw_chin_point(frame, phase_qualifier: PhaseQualifier):
        if phase_qualifier.chin_point:
            cv2.circle(frame, tuple(phase_qualifier.chin_point), 8, Drawer.BLUE_COLOR, thickness=-1,
                       lineType=cv2.FILLED)

    def display_info(self, frame, phase_qualifier: PhaseQualifier):
        new_frame = self.draw_info_region(frame, phase_qualifier)
        self.print_repeats(new_frame, phase_qualifier, ResultsDrawer.LEFT_PADDING, 30)
        self.print_fails(new_frame, phase_qualifier, ResultsDrawer.LEFT_PADDING, 60)
        self.print_elapsed_time(new_frame, phase_qualifier, ResultsDrawer.LEFT_PADDING, 90)
        return new_frame

    @staticmethod
    def display_skeleton(frame, points, required_points):
        Drawer.draw_skeleton(frame, points, required_points)
