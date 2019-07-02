from moviepy.editor import *


class AudioProcessor:

    def __init__(self, input_source_video_with_sound, input_source_video_without_sound, output_source_video):
        self._input_source_video = input_source_video_with_sound
        self._input_source_processed_video = input_source_video_without_sound
        self._output_source_video = output_source_video
        self._output_background_audio = os.path.join(os.path.dirname(output_source_video), 'background.mp3')
        self.audio = None
        self.audio_fps = None
        self.get_audio()

    def get_audio(self):
        self.audio = VideoFileClip(self._input_source_video).audio
        self.audio_fps = self.audio.fps

    def add_background_audio(self):
        video = VideoFileClip(self._input_source_processed_video)
        video = video.set_duration(self.audio.duration, change_end=False)
        video = video.set_audio(self.audio)
        video.write_videofile(self._output_source_video, audio=True, codec='libx264')

    def add_event(self, event_type, event_time):
        if event_type == "Complete":
            event_audio = AudioFileClip('sounds/Complete_event.wav')
        else:
            event_audio = AudioFileClip('sounds/Fail_event.wav')
        self.audio = CompositeAudioClip([self.audio, event_audio.set_start(event_time)])
