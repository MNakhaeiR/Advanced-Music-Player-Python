from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QFileDialog,
    QLabel,
    QSlider,
    QToolButton,
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon
from player.audio_engine import AudioEngine
from player.playlist import Playlist
from utils.metadata_utils import get_metadata_and_album_art
from ui.visualizer import VisualizerWidget
from pydub import AudioSegment
import numpy as np
import os


def resource_path(relative_path):
    # For PyInstaller compatibility
    import sys

    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Music Player")
        self.setWindowIcon(QIcon(resource_path("src/resources/icon.ico")))
        self.setGeometry(100, 100, 700, 500)

        self.playlist = Playlist()
        self.audio_engine = AudioEngine(self.playlist)
        self.audio_engine.playback_finished.connect(self.on_playback_finished)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Add theme switch button
        self.btn_theme = QPushButton("Switch Theme")
        self.btn_theme.setCheckable(True)
        self.btn_theme.clicked.connect(self.toggle_theme)

        # Set default theme
        self.set_dark_theme()

        # Album Art and Metadata
        meta_layout = QHBoxLayout()
        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(120, 120)
        self.album_art_label.setStyleSheet("border: 1px solid #ccc;")
        self.meta_info_label = QLabel("No track loaded")
        self.meta_info_label.setWordWrap(True)
        meta_layout.addWidget(self.album_art_label)
        meta_layout.addWidget(self.meta_info_label)
        layout.addLayout(meta_layout)

        # Visualizer
        self.visualizer = VisualizerWidget()
        layout.addWidget(self.visualizer)

        # Seek Bar
        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self.seek_audio)
        layout.addWidget(self.seek_slider)

        # Timer for updating seek bar
        self.seek_timer = QTimer(self)
        self.seek_timer.timeout.connect(self.update_seek_bar)
        self.seek_timer.start(200)  # Update every 200 ms

        # Playlist
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.list_widget)

        # Controls
        controls = QHBoxLayout()

        icon_size = QSize(32, 32)

        self.btn_prev = QToolButton()
        self.btn_prev.setIcon(QIcon(resource_path("src/resources/icons/prev.png")))
        self.btn_prev.setIconSize(icon_size)
        self.btn_prev.clicked.connect(self.prev_track)

        self.btn_play = QToolButton()
        self.btn_play.setIcon(QIcon(resource_path("src/resources/icons/play.png")))
        self.btn_play.setIconSize(icon_size)
        self.btn_play.clicked.connect(self.play_track)

        self.btn_pause = QToolButton()
        self.btn_pause.setIcon(QIcon(resource_path("src/resources/icons/pause.png")))
        self.btn_pause.setIconSize(icon_size)
        self.btn_pause.clicked.connect(self.pause_track)

        self.btn_stop = QToolButton()
        self.btn_stop.setIcon(QIcon(resource_path("src/resources/icons/stop.png")))
        self.btn_stop.setIconSize(icon_size)
        self.btn_stop.clicked.connect(self.stop_track)

        self.btn_next = QToolButton()
        self.btn_next.setIcon(QIcon(resource_path("src/resources/icons/next.png")))
        self.btn_next.setIconSize(icon_size)
        self.btn_next.clicked.connect(self.next_track)

        self.chk_shuffle = QToolButton()
        self.chk_shuffle.setIcon(
            QIcon(resource_path("src/resources/icons/shuffle.png"))
        )
        self.chk_shuffle.setCheckable(True)
        self.chk_shuffle.setIconSize(icon_size)
        self.chk_shuffle.toggled.connect(self.toggle_shuffle)

        self.chk_repeat = QToolButton()
        self.chk_repeat.setIcon(QIcon(resource_path("src/resources/icons/repeat.png")))
        self.chk_repeat.setCheckable(True)
        self.chk_repeat.setIconSize(icon_size)
        self.chk_repeat.toggled.connect(self.toggle_repeat)

        self.chk_repeat_one = QToolButton()
        self.chk_repeat_one.setIcon(
            QIcon(resource_path("src/resources/icons/repeat_one.png"))
        )
        self.chk_repeat_one.setCheckable(True)
        self.chk_repeat_one.setIconSize(icon_size)
        self.chk_repeat_one.toggled.connect(self.toggle_repeat_one)

        self.btn_load = QPushButton("Open")
        self.btn_load.clicked.connect(self.load_files)

        controls.addWidget(self.btn_prev)
        controls.addWidget(self.btn_play)
        controls.addWidget(self.btn_pause)
        controls.addWidget(self.btn_stop)
        controls.addWidget(self.btn_next)
        controls.addWidget(self.btn_load)
        controls.addWidget(self.chk_shuffle)
        controls.addWidget(self.chk_repeat)
        controls.addWidget(self.chk_repeat_one)
        controls.addWidget(self.btn_theme)
        layout.addLayout(controls)

        # Volume
        volume_layout = QHBoxLayout()
        self.lbl_volume = QLabel("Volume")
        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setValue(50)
        self.slider_volume.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.lbl_volume)
        volume_layout.addWidget(self.slider_volume)
        layout.addLayout(volume_layout)

        central_widget.setLayout(layout)

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Open Music Files",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a *.aac)",
        )
        if files:
            self.playlist.add_files(files)
            self.list_widget.clear()
            self.list_widget.addItems(self.playlist.get_filenames())

    def play_selected(self, item):
        self.visualizer.set_waveform(np.zeros(1024))
        index = self.list_widget.row(item)
        self.playlist.set_index(index)
        self.play_track()

    def play_track(self):
        path = self.playlist.current()
        if path:
            self.audio_engine.play(path, callback=self.visualizer.set_waveform)
            self.update_metadata(path)

    def pause_track(self):
        self.audio_engine.pause()

    def stop_track(self):
        self.audio_engine.stop()

    def next_track(self):
        self.visualizer.set_waveform(np.zeros(1024))
        path = self.playlist.next()
        if path:
            self.list_widget.setCurrentRow(self.playlist.index)
            self.audio_engine.play(path, callback=self.visualizer.set_waveform)
            self.update_metadata(path)

    def prev_track(self):
        self.visualizer.set_waveform(np.zeros(1024))
        path = self.playlist.prev()
        if path:
            self.list_widget.setCurrentRow(self.playlist.index)
            self.audio_engine.play(path, callback=self.visualizer.set_waveform)
            self.update_metadata(path)

    def set_volume(self, value):
        self.audio_engine.set_volume(value / 100)

    def toggle_shuffle(self, checked):
        self.playlist.set_shuffle(checked)

    def toggle_repeat(self, checked):
        self.playlist.set_repeat(checked)
        if checked:
            self.chk_repeat_one.setChecked(False)
            self.playlist.set_repeat_one(False)

    def toggle_repeat_one(self, checked):
        self.playlist.set_repeat_one(checked)
        if checked:
            self.chk_repeat.setChecked(False)
            self.playlist.set_repeat(False)

    def update_metadata(self, path):
        meta, art = get_metadata_and_album_art(path)
        text = (
            f"<b>Title:</b> {meta.get('title', 'Unknown')}<br>"
            f"<b>Artist:</b> {meta.get('artist', 'Unknown')}<br>"
            f"<b>Album:</b> {meta.get('album', 'Unknown')}"
        )
        self.meta_info_label.setText(text)
        if art:
            pixmap = QPixmap()
            pixmap.loadFromData(art)
            self.album_art_label.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
        else:
            self.album_art_label.setPixmap(QPixmap())
        self.update_visualizer(path)

    def update_visualizer(self, path):
        try:
            audio = AudioSegment.from_file(path)
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples[::2]  # Take one channel for stereo
            samples = samples / np.max(np.abs(samples))
            downsampled = samples[:: max(1, len(samples) // 512)]
            self.visualizer.set_waveform(downsampled[:512])
        except Exception as e:
            self.visualizer.set_waveform(np.zeros(512))

    def update_seek_bar(self):
        if self.audio_engine.data is not None and self.audio_engine.samplerate:
            pos = self.audio_engine.position
            total = len(self.audio_engine.data)
            if total > 0:
                value = int(pos / total * 1000)
                self.seek_slider.blockSignals(True)
                self.seek_slider.setValue(value)
                self.seek_slider.blockSignals(False)

    def seek_audio(self, value):
        if self.audio_engine.data is not None:
            total = len(self.audio_engine.data)
            pos = int(value / 1000 * total)
            self.audio_engine.seek(pos)

    def set_dark_theme(self):
        dark_stylesheet = """
        QWidget { background-color: #181c24; color: #f0f0f0; }
        QPushButton { background-color: #222; color: #fff; border-radius: 5px; }
        QSlider::groove:horizontal { background: #444; height: 6px; border-radius: 3px; }
        QSlider::handle:horizontal { background: #00cfff; width: 14px; border-radius: 7px; }
        QListWidget { background: #23283a; color: #fff; }
        """
        self.setStyleSheet(dark_stylesheet)

    def set_light_theme(self):
        light_stylesheet = """
        QWidget { background-color: #f5f5f5; color: #222; }
        QPushButton { background-color: #e0e0e0; color: #222; border-radius: 5px; }
        QSlider::groove:horizontal { background: #bbb; height: 6px; border-radius: 3px; }
        QSlider::handle:horizontal { background: #0078d7; width: 14px; border-radius: 7px; }
        QListWidget { background: #fff; color: #222; }
        """
        self.setStyleSheet(light_stylesheet)

    def toggle_theme(self):
        if self.btn_theme.isChecked():
            self.set_light_theme()
            self.btn_theme.setText("Dark Mode")
        else:
            self.set_dark_theme()
            self.btn_theme.setText("Light Mode")

    def on_playback_finished(self):
        # Handle repeat one and repeat all logic
        if self.playlist.repeat_one:
            self.play_track()
        elif self.playlist.repeat_mode:
            self.next_track()
        # else: do nothing (stop at end of playlist)
