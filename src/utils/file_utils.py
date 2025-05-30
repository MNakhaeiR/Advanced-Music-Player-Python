import os


def is_audio_file(filename):
    return filename.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"))
