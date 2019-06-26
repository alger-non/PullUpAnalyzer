class Timer:
    def __init__(self, fps):
        self._frames_count = 0
        self._cur_time = 0
        self._stored_time = 0
        self.fps = fps

    def inc(self):
        self._frames_count += 1
        self._cur_time = self._frames_count / self.fps

    def store_time(self):
        self._stored_time = self._cur_time

    def get_stored_time(self):
        return self._stored_time

    def get_time(self):
        return self._cur_time

    def reset(self):
        self._frames_count = 0
        self._cur_time = 0
        self._stored_time = 0
