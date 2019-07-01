from moviepy.editor import *

class AudioProcessor:

    def __init__(self, input_source_video_with_sound, input_source_video_without_sound, output_source_video):
        self._input_source_video = input_source_video_with_sound
        self._input_source_processed_video = input_source_video_without_sound
        self._output_source_video = output_source_video
        self._output_background_audio = os.path.join(os.path.dirname(output_source_video), 'background.mp3')
        self.video = None
        self.audio_fps = None
        self.get_audio()
        self.video_fps = None

    def get_audio(self):
        self.video = VideoFileClip(self._input_source_video)
        self.video_fps = self.video.fps
        self.audio_fps = self.video.audio.fps

    def add_background_audio(self, fps=29):
        video = VideoFileClip(self._input_source_processed_video)
        video.write_videofile(self._output_source_video, audio=self._output_background_audio, codec='libx264',
                              fps=self.video_fps, audio_fps=self.audio_fps, audio_codec='libmp3lame')

    def add_event(self, event_type, event_time):
        if event_type == "Complete":
            event_audio = AudioFileClip('sounds/Complete_event.wav')
        else:
            event_audio = AudioFileClip('sounds/Fail_event.wav')
        self.video.audio = CompositeAudioClip([self.video.audio, event_audio.set_start(event_time)])
        self.video.audio.write_audiofile(self._output_background_audio, fps=self.audio_fps)
