class PlayerControls:
    def __init__(self, audio_engine, playlist):
        self.audio_engine = audio_engine
        self.playlist = playlist

    def play(self):
        path = self.playlist.current()
        if path:
            self.audio_engine.play(path)

    def pause(self):
        self.audio_engine.pause()

    def stop(self):
        self.audio_engine.stop()

    def next_track(self):
        path = self.playlist.next()
        if path:
            self.audio_engine.play(path)

    def prev_track(self):
        path = self.playlist.prev()
        if path:
            self.audio_engine.play(path)

    def set_volume(self, value):
        self.audio_engine.set_volume(value)

    def toggle_shuffle(self, enabled):
        self.playlist.set_shuffle(enabled)

    def toggle_repeat(self, enabled):
        self.playlist.set_repeat(enabled)

    def seek(self, seconds):
        # Implement seeking if your audio engine supports it
        pass
