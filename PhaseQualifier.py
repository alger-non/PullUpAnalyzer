import Utils
import math
from collections import deque


class PhaseQualifier:
    """Class processing key points to identify athlete state."""

    def __init__(self, arm_angle_threshold, leg_angle_threshold, failed_attempts_amount_threshold,
                 neck_chin_top_of_head_ratio, chin_to_wrists_raise_ratio_to_start_attempt=0.7,
                 chin_to_wrists_raise_ration_to_finish_attempt=0.1, wrists_level_angle_threshold=5,
                 false_pull_up_check_queue_history=20):
        self._cur_wrists_level_angle = None
        self._cur_left_arm_angle, self._cur_right_arm_angle = None, None
        self._cur_left_leg_angle, self._cur_right_leg_angle = None, None
        self.arm_angle_threshold = arm_angle_threshold
        self.leg_angle_threshold = leg_angle_threshold
        self.wrists_level_angle_threshold = wrists_level_angle_threshold
        self._phases = ('beginning', 'pulling', 'chinning', 'lowering', 'unknown')
        self._cur_phase = 'unknown'
        self._clean_repeats = 0
        self._unclean_repeats = 0
        self._failed_phase_define_attempts = 0
        self.failed_attempts_amount_threshold = failed_attempts_amount_threshold
        self._process_phase = {self._phases[0]: self._process_beginning,
                               self._phases[1]: self._process_pulling,
                               self._phases[2]: self._process_chinning,
                               self._phases[3]: self._process_lowering,
                               self._phases[4]: self._process_unknown_state}
        self._chin_point = []
        self.neck_chin_nose_ratio = neck_chin_top_of_head_ratio
        self._distance_between_chin_and_wrist_to_start_attempt = None
        self._distance_between_chin_and_wrist_to_finish_attempt = None
        self.chin_to_wrists_raise_ratio_to_start_attempt = chin_to_wrists_raise_ratio_to_start_attempt
        self.chin_to_wrists_raise_ratio_to_finish_attempt = chin_to_wrists_raise_ration_to_finish_attempt
        self._pull_up_attempt_flag = False
        self.false_pull_up_check_queue_history = false_pull_up_check_queue_history
        self._last_wrist_y_deviations = deque(maxlen=self.false_pull_up_check_queue_history)
        self._last_shoulder_y_deviations = deque(maxlen=self.false_pull_up_check_queue_history)
        self._prev_shoulders_y = None
        self._prev_wrists_y = None
        self._angle_between_legs = None

    def get_wrists_level_angle(self):
        return self._cur_wrists_level_angle

    def get_left_arm_angle(self):
        return self._cur_left_arm_angle

    def get_right_arm_angle(self):
        return self._cur_right_arm_angle

    def get_left_leg_angle(self):
        return self._cur_left_leg_angle

    def get_right_leg_angle(self):
        return self._cur_right_leg_angle

    def get_cur_state(self):
        return self._cur_phase

    def get_clean_repeats(self):
        return self._clean_repeats

    def get_unclean_repeats(self):
        return self._unclean_repeats

    def get_chin_point(self):
        return self._chin_point

    def get_phases(self):
        return self._phases

    wrists_level_angle = property(get_wrists_level_angle)
    left_arm_angle = property(get_left_arm_angle)
    right_arm_angle = property(get_right_arm_angle)
    left_leg_angle = property(get_left_leg_angle)
    right_leg_angle = property(get_right_leg_angle)
    cur_state = property(get_cur_state)
    clean_repeats = property(get_clean_repeats)
    unclean_repeats = property(get_unclean_repeats)
    chin_point = property(get_chin_point)
    phases = property(get_phases)

    def _zero_failed_phase_define_attempts(self):
        self._failed_phase_define_attempts = 0

    def _inc_failed_phase_define_attempts(self):
        self._failed_phase_define_attempts += 1

    def check_failed_state_detection_attempts_amount(self):
        if self._failed_phase_define_attempts > self.failed_attempts_amount_threshold:
            self._cur_phase = self._phases[4]

    def _process_beginning(self, points):
        """Handle the initial pull up phase.

        At this stage we are waiting for the next phase viz. a pulling phase.
        Transition to this phase we define by the angle decreasing in athlete's arms.
        """
        arms_are_straight = self.are_arms_straight(points)
        if not arms_are_straight:
            self._cur_phase = self._phases[1]

    def _process_chinning(self, points):
        """Handle the chinning pull up phase.

        At this stage we are waiting for the next phase viz. a lowering phase.
        Transition to this phase we define by the chin position under the bar (actually under the wrists level).
        """
        neck_is_over_wrists_level = self.is_chin_over_wrists_level(points)
        if not neck_is_over_wrists_level:
            self._cur_phase = self._phases[3]

    def _process_unknown_state(self, points):
        """Handle the state that does not fit under any of the states specified by us.

        If the state is unknown then we just are waiting for the initial phase of pull up - hanging in the bottom position
        on the straight arms. And if it is then we move to the next phase.
        """
        there_is_initial_position = self.is_there_initial_position(points)
        if there_is_initial_position:
            self._cur_phase = self._phases[0]
            self._reset_deviations_calculation()
            self._calculate_attempt_positions(points)

    def _reset_deviations_calculation(self):
        self._last_shoulder_y_deviations.clear()
        self._last_wrist_y_deviations.clear()
        self._prev_wrists_y = None
        self._prev_shoulders_y = None

    @staticmethod
    def find_distance_between_wrists_and_shoulders(points):
        avg_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2
        avg_shoulders_y = (points['LShoulder'][1] + points['RShoulder'][1]) / 2
        return abs(avg_wrists_y - avg_shoulders_y)

    def find_distance_between_wrists_and_chin(self, points):
        avg_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2
        return None if not self.chin_point else self.chin_point[1] - avg_wrists_y

    def _calculate_attempt_positions(self, points):
        """Calculate the initial and final positions of a pulling up attempt.

        To count unclean reps we have to define the position from which we start to count unclean repetition
        and the position in which we consider this repetition as done.
        So we have found the distance between wrists and a chin (since we're in the initial phase that's maximum
        possible distance between these points) and multiply it by our chin-to-wrists-raise-ratio-to-start-attempt
        and chin-to-wrists-raise-ration-to-finish-attempt COEFFs.
        """
        distance_between_wrists_and_chin = self.find_distance_between_wrists_and_chin(points)

        if not distance_between_wrists_and_chin:
            # if the distance isn't found we set our threshold distances in infinity to
            # prevent unclean pull ups attempt counting while comparing them with current wrists-chin distances
            self._distance_between_chin_and_wrist_to_start_attempt = math.inf
            self._distance_between_chin_and_wrist_to_finish_attempt = math.inf
            return
        self._distance_between_chin_and_wrist_to_start_attempt = distance_between_wrists_and_chin * (
                1 - self.chin_to_wrists_raise_ratio_to_start_attempt)
        self._distance_between_chin_and_wrist_to_finish_attempt = distance_between_wrists_and_chin * (
                1 - self.chin_to_wrists_raise_ratio_to_finish_attempt)

    def is_there_initial_position(self, points):
        """Define whether there is the initial position viz. hanging in the bottom position on the straight arms.

        To define hanging in the bottom position on the straight arms we check the following conditions:
        1) Are arms straight?
        2) Are wrists over the body?

        NOTE: these conditions are not enough to determine hanging exactly
        but they work in "most" cases.
        """
        arms_are_straight = self.are_arms_straight(points)
        wrists_are_over_body = self.are_wrists_over_body(points)
        return arms_are_straight and wrists_are_over_body

    def are_legs_together(self, points):
        """Define whether legs are together.

        We have found the angle between legs-vectors in points Hip - Knee and
        compare the angle with our leg-angle-threshold COEFF.
        If legs aren't found we imply that legs are together otherwise
        we'd have "unknown state" every time when athlete's legs are out of the frame.
        """
        self._angle_between_legs = -math.inf
        if points['LHip'] and points['LKnee'] and points['RHip'] and points['RKnee']:
            self._angle_between_legs = Utils.get_angle_between_vectors(
                Utils.get_vector_from_points(points['LHip'], points['LKnee']),
                Utils.get_vector_from_points(points['RHip'], points['RKnee']))

        return self._angle_between_legs <= self.leg_angle_threshold

    def _inc_clean_repeats_amount(self):
        self._clean_repeats += 1
        self._reset_attempt()

    def _inc_unclean_repeats_amount(self):
        self._unclean_repeats += 1
        self._reset_attempt()

    def _reset_attempt(self):
        self._pull_up_attempt_flag = False

    def are_shoulders_deviation_greater_than_wrists_one(self):
        wrists_deviations_sum = sum(self._last_wrist_y_deviations)
        shoulders_deviations_sum = sum(self._last_shoulder_y_deviations)
        return shoulders_deviations_sum > wrists_deviations_sum

    def _process_pulling(self, points):
        """Handle the pulling phase.

        From this phase we can pass to the next chinning phase or back to the previous initial position.
        The following phase we determine by the chin position above the wrists level.
        To avoid false pull ups when an athlete imitates a pull up standing on the ground
        instead of executing real one, we calculate vertical distance overcome by wrists and by shoulders in the frames
        amount of which is defined by our false-pull-up-check-queue-history COEFF.
        And at the moment of a possible pull up we compare these distances and count pull up if the distance overcome by
        shoulders is greater than the distance overcome by wrists
        (in a real pull up there's a shoulders movement not a wrists one).

        If we don't qualify any of the possible phases we check a possibility of unclean pull up.

        Note: we don't compare the chin position with the bar since we only operate with
        athlete's body key points, so it will be a bit inaccurate.
        """
        self._update_wrists_y_deviations(points)
        self._update_shoulders_y_deviations(points)
        if self.is_chin_over_wrists_level(points):
            if self.are_shoulders_deviation_greater_than_wrists_one():
                self._inc_clean_repeats_amount()
                self._cur_phase = self._phases[2]

        elif self.is_there_initial_position(points):
            self._cur_phase = self._phases[0]
        else:
            self._define_unclean_pull_up_state(points)

    def _reset_pull_up_attempt(self):
        self._pull_up_attempt_flag = False

    def _define_unclean_pull_up_state(self, points):
        """Define unclean pull up state.

        If a current wrists-chin distance is less than our distance-between-chin-and-wrist-to-start-attempt we consider
        this repetition as an pull up attempt.
        If a current wrists-chin distance is greater than our distance-between-chin-and-wrist-to-finish-attempt we increase
        the unclean pull ups counter.
        """
        if not self.chin_point:
            return
        cur_distance_between_chin_and_wrists = self.find_distance_between_wrists_and_chin(points)

        if not self._pull_up_attempt_flag:
            self._pull_up_attempt_flag = cur_distance_between_chin_and_wrists <= self._distance_between_chin_and_wrist_to_start_attempt
        else:
            unclean_pull_up_is_done = cur_distance_between_chin_and_wrists > self._distance_between_chin_and_wrist_to_finish_attempt
            if unclean_pull_up_is_done and self.are_shoulders_deviation_greater_than_wrists_one():
                self._inc_unclean_repeats_amount()
                # pass to lowering phase
                self._cur_phase = self._phases[3]
                self._reset_pull_up_attempt()

    def _update_wrists_y_deviations(self, points):
        """Add a current wrists y deviation to a wrists y deviations queue."""
        cur_wrists_y = (points['LWrist'][1] + points['RWrist'][1]) / 2
        if self._prev_wrists_y:
            cur_wrists_y_deviation = abs(self._prev_wrists_y - cur_wrists_y)
            self._last_wrist_y_deviations.append(cur_wrists_y_deviation)
        self._prev_wrists_y = cur_wrists_y

    def _update_shoulders_y_deviations(self, points):
        """Add a current shoulders y deviation to a shoulders y deviations queue."""
        cur_shoulders_y = (points['LShoulder'][1] + points['RShoulder'][1]) / 2
        if self._prev_shoulders_y:
            cur_shoulders_y_deviation = abs(self._prev_shoulders_y - cur_shoulders_y)
            self._last_shoulder_y_deviations.append(cur_shoulders_y_deviation)
        self._prev_shoulders_y = cur_shoulders_y

    def _process_lowering(self, points):
        """Handle the lowering pull up phase.

        In this phase we are waiting for the next phase viz. the initial phase.
        """
        if self.is_there_initial_position(points):
            self._cur_phase = self._phases[0]

    def is_there_hang(self, points):
        """Define whether there is hanging on the bar.

        To define hanging on the bar we check the following conditions:
        1) Are wrists on the same level (y axis)?
        2) Are wrists higher than elbows?
        3) Is head between wrists (as the head we use the point of chin)?
        4) Are legs together?

        NOTE: these conditions are not enough to determine the hang exactly
        but they work in "most" cases.
        """
        wrists_are_on_same_level = self.are_wrists_on_same_level(points)
        wrists_are_higher_than_elbows = self.are_wrists_higher_than_elbows(points)
        head_is_between_wrists = self.is_head_between_wrists(points)
        legs_are_together = self.are_legs_together(points)
        return wrists_are_on_same_level and wrists_are_higher_than_elbows and head_is_between_wrists and legs_are_together

    def is_head_between_wrists(self, points):
        if not (points['LWrist'] and points['RWrist'] and self.chin_point):
            return False

        min_x_of_wrist = min(points['LWrist'][0], points['RWrist'][0])
        max_x_of_wrist = max(points['LWrist'][0], points['RWrist'][0])
        return min_x_of_wrist < self.chin_point[0] < max_x_of_wrist

    @staticmethod
    def are_wrists_higher_than_elbows(points):
        if not all((points['LWrist'], points['RWrist'], points['LElbow'], points['RElbow'])):
            return False

        left_wrist_y, right_wrist_y = points['LWrist'][1], points['RWrist'][1]
        left_elbow_y, right_elbow_y = points['LElbow'][1], points['RElbow'][1]
        return left_wrist_y < left_elbow_y and right_wrist_y < right_elbow_y

    @staticmethod
    def are_wrists_over_body(points):
        """Define whether wrists are higher than all other body parts.

        We have to compare a wrists y-coordinate with other body parts' y coordinates
        but since the coordinate system begins at the top left corner our highest
        point is actually the lowest one.
        """
        if not (points['LWrist'] and points['RWrist']):
            return False
        left_wrist_y, right_wrist_y = points['LWrist'][1], points['RWrist'][1]
        copy_points = dict(points)
        del copy_points['LWrist']
        del copy_points['RWrist']
        ys = (point[1] for point in copy_points.values() if point)
        # lowest_y is actually highest_y
        lowest_y = min(ys)
        return left_wrist_y < lowest_y and right_wrist_y < lowest_y

    def are_arms_straight(self, points):
        """Define whether arms are straight.

         We have found the angle in each arm between next points: shoulder - elbow - writs and
         then compare the angle with our arm-angle-threshold COEFF.
        """
        self._cur_left_arm_angle, self._cur_right_arm_angle = math.inf, math.inf
        if points['LWrist'] and points['LElbow'] and points['LShoulder']:
            self._cur_left_arm_angle = Utils.get_angle_between_three_points(points['LWrist'], points['LElbow'],
                                                                           points['LShoulder'])

        if points['RWrist'] and points['RElbow'] and points['RShoulder']:
            self._cur_right_arm_angle = Utils.get_angle_between_three_points(points['RWrist'], points['RElbow'],
                                                                            points['RShoulder'])

        return self._cur_left_arm_angle < self.arm_angle_threshold and self._cur_right_arm_angle < self.arm_angle_threshold

    def are_wrists_on_same_level(self, points):
        """Define whether wrists are on same level (y axis).

        To determine whether wrists are on the same level we define the angle of deviation of one wrist
        relative to another vertically and compare this angle with our wrists-level-angle_threshold COEFF.
        """
        if not (points['LWrist'] and points['RWrist']):
            return False
        left_wrist_point, right_wrist_point = points['LWrist'], points['RWrist']
        delta_y = abs(left_wrist_point[1] - right_wrist_point[1])
        delta_x = abs(left_wrist_point[0] - right_wrist_point[0])

        # prevention of division by zero
        if delta_x == 0:
            return False
        angle_in_radians = math.atan(delta_y / delta_x)
        self._cur_wrists_level_angle = int(math.degrees(angle_in_radians))
        return self._cur_wrists_level_angle <= self.wrists_level_angle_threshold

    def is_chin_over_wrists_level(self, points):
        if not (points['LWrist'] and points['RWrist'] and self._chin_point):
            return False

        left_wrist_point, right_wrist_point = points['LWrist'], points['RWrist']
        avg_wrists_y = (left_wrist_point[1] + right_wrist_point[1]) / 2
        return self.chin_point[1] <= avg_wrists_y

    def qualify_state(self, points):
        self.define_chin_point(points)
        if self.is_there_hang(points):
            self._zero_failed_phase_define_attempts()
            self._process_phase[self._cur_phase](points)
            return True
        else:
            self._inc_failed_phase_define_attempts()
            self.check_failed_state_detection_attempts_amount()
            return False

    def define_chin_point(self, points):
        """Define chin point.

        We have defined a chin point by ratio between ears/nose and neck.
        If we've got a nose point we use it to get more accurate chin point
        but if we haven't got this one (the athlete is standing with his back to the camera,
        the point is not found) we use ears points to obtain nose point in the next way:
        nose_x = (l_ear_x + r_ear_x) / 2
        nose_y = (l_ear_y + r_ear_y) / 2.
        Next we use our neck-chin-nose-ratio COEFF to define a chin point.
        """
        # define chin point by simple ratio between ears(x) and ears-neck(y)
        l_ear_point, r_ear_point, neck_point, nose_point = points['LEar'], points['REar'], points['Neck'], points[
            'Nose']
        if not ((l_ear_point and r_ear_point or nose_point) and neck_point):
            self._chin_point = None
            return

        if not nose_point:
            nose_point = (l_ear_point[0] + r_ear_point[0]) / 2, (l_ear_point[1] + r_ear_point[1]) / 2

        chin_point_x = neck_point[0] + int((nose_point[0] - neck_point[0]) * self.neck_chin_nose_ratio)
        chin_point_y = neck_point[1] + int((nose_point[1] - neck_point[1]) * self.neck_chin_nose_ratio)
        self._chin_point = [chin_point_x, chin_point_y]
