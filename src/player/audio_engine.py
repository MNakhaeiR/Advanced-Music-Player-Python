import sounddevice as sd
import soundfile as sf
import threading
from PyQt5.QtCore import QObject, pyqtSignal


class AudioEngine(QObject):
    playback_finished = pyqtSignal()

    def __init__(self, playlist=None):
        super().__init__()
        self.playlist = playlist
        self.stream = None
        self.data = None
        self.samplerate = None
        self.position = 0
        self.playing = False
        self.lock = threading.Lock()
        self.callback = None  # For visualizer
        self.volume = 1.0

    def play(self, path, callback=None):
        self.stop()
        self.data, self.samplerate = sf.read(path, dtype="float32")
        self.position = 0
        self.playing = True
        self.callback = callback
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.data.shape[1] if len(self.data.shape) > 1 else 1,
            callback=self.audio_callback,
            blocksize=1024,
        )
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        with self.lock:
            if not self.playing:
                outdata[:] = 0
                return
            end = self.position + frames
            chunk = self.data[self.position : end]
            if len(chunk) < frames:
                outdata[: len(chunk)] = chunk * self.volume
                outdata[len(chunk) :] = 0
                self.playing = False
                self.stream.stop()
                self.playback_finished.emit()
            else:
                outdata[:] = chunk * self.volume
            if self.callback:
                self.callback(chunk)
            self.position = end

    def pause(self):
        with self.lock:
            if self.stream:
                self.playing = not self.playing

    def stop(self):
        with self.lock:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            self.playing = False
            self.position = 0

    def set_volume(self, value):
        self.volume = value

    def seek(self, position):
        """Set playback position (in samples)."""
        with self.lock:
            if self.data is not None:
                self.position = max(0, min(position, len(self.data) - 1))
