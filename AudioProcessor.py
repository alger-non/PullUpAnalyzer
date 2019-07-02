from moviepy.editor import *


class AudioProcessor:
    sounds_dir = 'sounds'

    def __init__(self, input_source_video_with_sound, input_source_video_without_sound, output_source_video):
        self._input_source_video = input_source_video_with_sound
        self._input_source_processed_video = input_source_video_without_sound
        self._output_source_video = output_source_video
        self._output_background_audio = os.path.join(os.path.dirname(output_source_video), 'background.mp3')
        self.audio = None
        self.audio_fps = None
        self.get_audio()
        self.clean_rep_event_audio = AudioFileClip(os.path.join(AudioProcessor.sounds_dir, 'Complete_event.wav'))
        self.unclean_rep_event_audio = AudioFileClip(os.path.join(AudioProcessor.sounds_dir, 'Fail_event.wav'))

    def get_audio(self):
        video = VideoFileClip(self._input_source_video)
        self.audio = video.audio
        self.audio_fps = self.audio.fps
        video.close()

    def add_background_audio(self):
        video = VideoFileClip(self._input_source_processed_video)
        video = video.set_duration(self.audio.duration, change_end=False)
        video = video.set_audio(self.audio)
        video.write_videofile(self._output_source_video, audio=True, codec='libx264')
        video.close()

    def add_event(self, event_type, event_time):
        if event_type == "Complete":
            event_audio = self.clean_rep_event_audio
        else:
            event_audio = self.unclean_rep_event_audio
        self.audio = CompositeAudioClip([self.audio, event_audio.set_start(event_time)])
