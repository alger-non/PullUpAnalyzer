from Timer import Timer
from PhaseQualifier import PhaseQualifier
from Drawer import Drawer
import cv2
from Animator import Animator


class ResultsDrawer:
    """Class drawing the general information about the pull up process."""
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

        Drawer.print_message(frame, 'Reps: ', x, y)
        if not self.animator.is_clean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_repeats}')
        else:
            self.animator.play_clean_pull_up_font_animation(frame, x + 100, y)

    def print_fails(self, frame, phase_qualifier: PhaseQualifier, x, y):
        now_fails = phase_qualifier.unclean_repeats
        if now_fails != self.old_fails:
            self.animator.generate_unclean_pull_up_animation(now_fails)
            self.old_fails = now_fails
        Drawer.print_message(frame, f'Fails: ', x, y)

        if not self.animator.is_unclean_pull_up_font_animation_playing():
            Drawer.print_message_with_text_edging(frame, x + 100, y, f'{now_fails}', text_color=Drawer.DARK_RED_COLOR,
                                                  border_size=3, border_color=Drawer.ORANGE_COLOR)
        else:
            self.animator.play_unclean_pull_up_font_animation(frame, x + 100, y)

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
        Drawer.print_message(frame, f'Time: {mins}:{secs:02}', x, y)

    @staticmethod
    def draw_info_region(frame, phase_qualifier: PhaseQualifier):
        overlay = frame.copy()
        x, y, w, h = 0, 0, 355, 80
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
        alpha = 0.7
        new_frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        return ResultsDrawer.draw_glyph(new_frame, phase_qualifier)

    @staticmethod
    def draw_glyph(frame, phase_qualifier: PhaseQualifier):
        overlay = frame.copy()
        if phase_qualifier.cur_state == 'beginning':
            input_file = 'icons/1.png'
        elif phase_qualifier.cur_state == 'chinning':
            input_file = 'icons/4.png'
        elif phase_qualifier.cur_state == 'pulling':
            input_file = 'icons/3.png'
        elif phase_qualifier.cur_state == 'lowering':
            input_file = 'icons/2.png'
        else:
            input_file = 'icons/5.png'

        alpha = 0.7
        img2 = cv2.imread(input_file)
        size = 100
        pictogram = cv2.resize(img2, (size, size), interpolation=cv2.INTER_AREA)
        x, y, w, h = 0, 80, size, size
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
        overlay[80:80 + size, :size] = pictogram
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
            cv2.circle(frame, tuple(phase_qualifier.chin_point), 8, Drawer.BLUE_COLOR, thickness=-1, lineType=cv2.FILLED)

    def display_info(self, frame, phase_qualifier: PhaseQualifier):
        new_frame = self.draw_info_region(frame, phase_qualifier)
        self.print_repeats(new_frame, phase_qualifier, 0, 30)
        self.print_fails(new_frame, phase_qualifier, 200, 30)
        self.print_elapsed_time(new_frame, phase_qualifier, 0, 75)
        return new_frame

    @staticmethod
    def display_skeleton(frame, points, required_points):
        Drawer.draw_skeleton(frame, points, required_points)
