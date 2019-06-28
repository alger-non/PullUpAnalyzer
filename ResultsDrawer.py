from Timer import Timer
from PhaseQualifier import PhaseQualifier
from Drawer import Drawer
import cv2
from Animator import Animator


class ResultsDrawer:

    def __init__(self, fps, animation_duration_in_sec=1, animation_min_font_thickness=2, animation_max_font_thickness=9,
                 animation_min_line_thickness=2, animation_max_line_thickness=13):
        self.old_reps = 0
        self.old_fails = 0
        self.animation_duration_in_sec = animation_duration_in_sec
        queue_size = int(fps * self.animation_duration_in_sec)
        self.animator = Animator(queue_size, animation_min_font_thickness, animation_max_font_thickness,
                                 animation_min_line_thickness, animation_max_line_thickness)
        self.timer = Timer(fps)

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
            self.animator.generate_clean_pull_up_animation(now_repeats)
            self.old_reps = now_repeats

        Drawer.print_message(frame, 'Reps: ', x, y)
        if not self.animator.is_clean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_repeats}')
        else:
            self.animator.play_clean_pull_up_font_animation(frame, x + 100, y)

    def print_fails(self, frame, phase: PhaseQualifier, x, y):
        now_fails = phase.unclean_repeats
        if now_fails != self.old_fails:
            self.animator.generate_unclean_pull_up_animation(now_fails)
            self.old_fails = now_fails
        Drawer.print_message(frame, f'Fails: ', x, y)

        if not self.animator.is_unclean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_fails}', text_color=Drawer.DARK_RED_COLOR,
                                                  border_size=3, border_color=Drawer.ORANGE_COLOR)
        else:
            self.animator.play_unclean_pull_up_font_animation(frame, x + 100, y)

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
        mins, secs = int(cur_time / 60), int(cur_time % 60)
        Drawer.print_message(frame, f'Time: {mins}:{secs:02}', x, y)

    @staticmethod
    def draw_info_region(frame):
        overlay = frame.copy()
        x, y, w, h = 0, 0, 355, 80
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
        alpha = 0.7
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def draw_line_between_wrists(self, frame, points):
        l_wrist, r_wrist = points['LWrist'], points['RWrist']
        if self.animator.is_pull_up_line_animation_playing():
            self.animator.play_pull_up_line_animation(frame, l_wrist, r_wrist)
        else:
            cv2.line(frame, l_wrist, r_wrist, Drawer.DEFAULT_COLOR, Drawer.DEFAULT_LINE_THICKNESS)

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
