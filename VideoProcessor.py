import cv2
import Utils
import os
import json
from ResultsDrawer import ResultsDrawer
from os import walk
from PhaseQualifier import PhaseQualifier
from AudioProcessor import AudioProcessor


class VideoProcessor:
    """Class to handle an input video."""

    def __init__(self, input_file_name, output_file_name_with_sound, phase_definer: PhaseQualifier, required_points,
                 required_pairs):
        self.output_file_name_with_sound = output_file_name_with_sound
        self.input_file_name = input_file_name
        self.cap = cv2.VideoCapture(self.input_file_name)
        self._fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.phase_qualifier = phase_definer
        self.required_points = required_points
        self.required_pairs = required_pairs
        self._drawer = None
        self.events_labels = []
        self._prev_clean_reps_amount = 0
        self._prev_unclean_reps_amount = 0
        self._frame_num = 0

        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)

        output_file_name, output_file_extension = self.output_file_name_with_sound.split('.')
        self.output_file_name_without_sound = f'{output_file_name}_without_audio.{output_file_extension}'
        self.video_writer = cv2.VideoWriter(self.output_file_name_without_sound, cv2.VideoWriter_fourcc(*"XVID"), fps,
                                            (cap_width, cap_height))
        self.audio_writer = None

    def create_audio_writer(self):
        self.audio_writer = AudioProcessor(self.input_file_name, self.output_file_name_without_sound,
                                           self.output_file_name_with_sound)

    def delete_audio_writer(self):
        del self.audio_writer

    @staticmethod
    def show_processed_frame(frame):
        cv2.imshow('Output', frame)
        cv2.waitKey(1)

    def write_frame_to_output(self, frame):
        self.video_writer.write(frame)

    @staticmethod
    def get_json_files_from_dir(json_dir):
        """Return all file names from the specified directory.

        :param json_dir: a directory containing json files producing by OpenPose
        :return: a list of file names
        """
        json_files = []
        for _, _, f_names in walk(json_dir):
            json_files.extend(f_names)
            break
        json_files = sorted(json_files)
        return json_files

    def release_video_cap(self):
        if self.cap:
            self.cap.release()

    def release_video_writer(self):
        if self.video_writer:
            self.video_writer.release()

    def release_video_tools(self):
        cv2.destroyAllWindows()
        self.release_video_cap()
        self.release_video_writer()

    def process_video_with_net(self, op_wrapper):
        """Create a generator returning processed frames using only an input video.

        :param op_wrapper: an initialized open-pose instance to handle frames
        :return: a generator returning processed frames
        """
        from openpose import pyopenpose as op
        # pass _fps to the ResultsDrawer instance to obtain same animation effect on videos with different _fps
        self._drawer = ResultsDrawer(self._fps)
        while True:
            has_frame, frame = self.cap.read()
            if not has_frame:
                break
            self._frame_num += 1
            datum = op.Datum()
            datum.cvInputData = frame
            op_wrapper.emplaceAndPop([datum])
            # check whether datum contains person key points (25 points consisting of x, y, probability)
            if datum.poseKeypoints.size == 75:
                points = Utils.extract_required_points(datum.poseKeypoints[0], self.required_points)
                frame = self.handle_points(frame, points)
            self.handle_frame(frame)
        self.release_video_tools()
        self.overlay_audio()

    def process_video_with_raw_data(self, json_dir):
        """Create a generator returning processed frames using an input video and json key points.

        :param json_dir: a directory name containing json files with key points
        :return: a generator returning processed frames
        """
        self._drawer = ResultsDrawer(self._fps)
        json_files = self.get_json_files_from_dir(json_dir)

        for filename in json_files:
            full_filename_path = os.path.join(json_dir, filename)
            with open(full_filename_path, "r") as json_data:
                data = json.load(json_data)
                has_frame, frame = self.cap.read()
                if not has_frame:
                    return
                self._frame_num += 1
                # check whether the json file contains person key points (is a person found?)
                if data['people']:
                    points_list = data['people'][0]['pose_keypoints_2d']
                    points = Utils.extract_required_json_points(points_list, self.required_points)
                    frame = self.handle_points(frame, points)
                self.handle_frame(frame)
        self.release_video_tools()
        self.overlay_audio()

    def overlay_audio(self):
        self.create_audio_writer()
        self.create_audio_events()
        self.put_audio_on_video()
        self.delete_audio_writer()

    def handle_points(self, frame, points):
        self.phase_qualifier.qualify_state(points)
        self._update_reps_time_labels()
        return self.put_info_on_frame(frame, points)

    def handle_frame(self, frame):
        self.show_processed_frame(frame)
        self.write_frame_to_output(frame)

    def _update_reps_time_labels(self):
        if self._prev_clean_reps_amount != self.phase_qualifier.clean_repeats:
            self.events_labels.append(((self._frame_num / self._fps), True))
            self._prev_clean_reps_amount = self.phase_qualifier.clean_repeats
        elif self._prev_unclean_reps_amount != self.phase_qualifier.unclean_repeats:
            self.events_labels.append(((self._frame_num / self._fps), False))
            self._prev_unclean_reps_amount = self.phase_qualifier.unclean_repeats

    def put_info_on_frame(self, frame, points):
        """Put on the frame a pulling ups info.

        :param frame: a frame to be applied
        :param points: key points
        :return: a handled frame
        """
        new_frame = self._drawer.display_info(frame, self.phase_qualifier)
        self._drawer.display_skeleton(new_frame, points, self.required_pairs)
        self._drawer.draw_line_between_wrists(new_frame, points)
        self._drawer.draw_chin_point(new_frame, self.phase_qualifier)
        return new_frame

    def create_audio_events(self):
        for rep_time, is_clean_rep in self.events_labels:
            event = 'Complete' if is_clean_rep else 'Fail'
            self.audio_writer.add_event(event, rep_time)

    def put_audio_on_video(self):
        self.audio_writer.add_background_audio()
