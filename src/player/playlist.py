import os
import random


class Playlist:
    def __init__(self):
        self.tracks = []
        self.index = 0
        self.shuffle_mode = False
        self.repeat_mode = False
        self._shuffled_indices = []

    def add_files(self, files):
        self.tracks.extend(files)
        self._reset_shuffle()

    def get_filenames(self):
        return [os.path.basename(f) for f in self.tracks]

    def set_index(self, idx):
        if 0 <= idx < len(self.tracks):
            self.index = idx

    def current(self):
        if self.tracks:
            return self.tracks[self.index]
        return None

    def next(self):
        if not self.tracks:
            return None
        if self.shuffle_mode:
            if not self._shuffled_indices:
                self._reset_shuffle()
            self.index = self._shuffled_indices.pop(0)
        else:
            self.index += 1
            if self.index >= len(self.tracks):
                if self.repeat_mode:
                    self.index = 0
                else:
                    self.index = len(self.tracks) - 1
        return self.tracks[self.index]

    def prev(self):
        if not self.tracks:
            return None
        if self.shuffle_mode:
            if not self._shuffled_indices:
                self._reset_shuffle()
            self.index = self._shuffled_indices.pop(0)
        else:
            self.index -= 1
            if self.index < 0:
                if self.repeat_mode:
                    self.index = len(self.tracks) - 1
                else:
                    self.index = 0
        return self.tracks[self.index]

    def set_shuffle(self, enabled):
        self.shuffle_mode = enabled
        self._reset_shuffle()

    def set_repeat(self, enabled):
        self.repeat_mode = enabled

    def _reset_shuffle(self):
        if self.shuffle_mode and self.tracks:
            indices = list(range(len(self.tracks)))
            random.shuffle(indices)
            self._shuffled_indices = indices
        else:
            self._shuffled_indices = []
