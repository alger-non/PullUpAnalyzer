from moviepy.editor import *
import ResultsDrawer

class AudioProcessor:

    def __init__(self, input_source_video_with_sound, input_source_video_without_sound, output_source_video, output_source_audio='Sound/background.mp3'):
        self._input_source_video = input_source_video_with_sound
        self._input_source_processed_video = input_source_video_without_sound
        self._output_source_video = output_source_video
        self._output_source_audio = output_source_audio
        self._events_list = dict()

    def get_audio(self):
        video = VideoFileClip(self._input_source_video)
        return video.audio.write_audiofile(self._output_source_audio)

    def add_background_audio(self, fps=25):
        video = VideoFileClip(self._input_source_processed_video)
        video.write_videofile(self._output_source_video, audio=self._output_source_audio, codec='libx264', fps=fps)

    def add_events(self):
        audio = AudioFileClip(self._output_source_audio)
        self._events_list = ResultsDrawer.events_list
        for key, value in self._events_list.items():
            audio = self.add_event(value, float(key), audio)

        audio.write_audiofile(self._output_source_audio, fps=44100)


    def add_event(self, event_type, event_time, audio: AudioFileClip):
        if event_type == "Complete":
            event_audio = AudioFileClip('Sound/Complete_event.wav').subclip(0, 0.5)
        else:
            event_audio = AudioFileClip('Sound/Fail_event.wav')


        return CompositeAudioClip([audio, event_audio.volumex(1.5).set_start(event_time)])