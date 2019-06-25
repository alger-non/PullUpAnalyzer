import cv2
from PoseProcessor import PoseProcessor
from Drawer import Drawer


class ResultsDrawer:

    OLD_REPEATS = 0
    OLD_FAILS = 0

    @staticmethod
    def phase(frame, phase: PoseProcessor, x, y, side):
        Drawer.print_message(frame,'Phase:', x, y+side, Drawer.BLACK_COLOR)
        x += 100
        if phase.cur_state == 'hanging in the bottom position':
            Drawer.glyph_bottom_hanging(frame, x, y, side)
        elif phase.cur_state == 'hanging in the top position':
            Drawer. glyph_top_hanging(frame, x, y, side)
        elif phase.cur_state == 'ascending':
            Drawer.glyph_asc(frame, x, y, side)
        elif phase.cur_state == 'descending':
            Drawer.glyph_desc(frame, x, y, side)
        else:
            Drawer.glyph_undefined(frame, x, y)

    @staticmethod
    def misguided_attempt(frame, x, y):
        Drawer.print_message(frame, 'Misguided attempt!.', x, y)

    @staticmethod
    def repeats(frame, phase: PoseProcessor, x, y):
        now_repeats = phase._pure_repeats
        color = Drawer.GREEN_COLOR
        if ResultsDrawer.OLD_REPEATS != now_repeats:
            color = Drawer.PINK_COLOR
            ResultsDrawer.OLD_REPEATS = now_repeats

        if now_repeats == 0 and phase._failed_state_detection_attempts != 0:
            ResultsDrawer.misguided_attempt(frame, x + 210, y)
            color = Drawer.RED_COLOR
        Drawer.print_message(frame, f'Repeats: {phase.pure_repeats}', x, y, color)

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
        Drawer.print_message(frame, f'Time: {sec:.3} sec', x, y, Drawer.BLUE_COLOR)

    @staticmethod
    def display_info(frame, cap, phase: PoseProcessor,):
        ResultsDrawer.repeats(frame, phase, 0, 30)
        ResultsDrawer.fail(frame, phase, 0, 65)
        ResultsDrawer.phase(frame, phase, 0, 75, 30)
        ResultsDrawer.time(cap, frame, 0, 140)

