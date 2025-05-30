from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QLinearGradient,
    QBrush,
    QPen,
    QPainterPath,
    QFont,
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
import numpy as np


class FFTWorker(QThread):
    spectrum_ready = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = np.zeros(1024)
        self.running = True

    def run(self):
        while self.running:
            spectrum = np.abs(np.fft.rfft(self.data * np.hanning(len(self.data))))
            spectrum = spectrum / (np.max(spectrum) + 1e-6)
            self.spectrum_ready.emit(spectrum)
            self.msleep(30)

    def update_data(self, data):
        self.data = data.copy() if data is not None else np.zeros(1024)

    def stop(self):
        self.running = False
        self.wait()


class VisualizerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self.setMaximumHeight(200)
        self.setStyleSheet("background-color: #181c24; border-radius: 10px;")
        self.spectrum = np.zeros(513)
        self.peak = np.zeros(513)
        self.fft_worker = FFTWorker()
        self.fft_worker.spectrum_ready.connect(self.update_spectrum)
        self.fft_worker.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)

    def set_waveform(self, waveform):
        if waveform is not None and len(waveform) > 0:
            waveform = waveform.flatten()
            if len(waveform) > 1024:
                waveform = waveform[:1024]
            else:
                waveform = np.pad(waveform, (0, 1024 - len(waveform)), "constant")
            self.fft_worker.update_data(waveform)
        else:
            self.fft_worker.update_data(np.zeros(1024))

    @pyqtSlot(np.ndarray)
    def update_spectrum(self, spectrum):
        # Smooth animation by interpolating
        alpha = 0.5
        if len(spectrum) != len(self.spectrum):
            self.spectrum = np.zeros_like(spectrum)
            self.peak = np.zeros_like(spectrum)
        self.spectrum = alpha * spectrum + (1 - alpha) * self.spectrum
        self.peak = np.maximum(self.peak * 0.96, self.spectrum)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bar_count = min(w // 4, len(self.spectrum))
        bar_width = w / bar_count
        max_height = h - 20

        for i in range(bar_count):
            value = self.spectrum[i] if i < len(self.spectrum) else 0
            peak_value = self.peak[i] if i < len(self.peak) else 0
            bar_height = int(value * max_height)
            peak_height = int(peak_value * max_height)
            x = int(i * bar_width)
            # Gradient for each bar
            grad = QLinearGradient(x, h - bar_height, x, h)
            grad.setColorAt(0.0, QColor(0, 255, 255, 220))
            grad.setColorAt(0.5, QColor(0, 128, 255, 180))
            grad.setColorAt(1.0, QColor(0, 0, 64, 0))
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.NoPen)
            # Draw bar with rounded top
            rect = (x + 1, h - bar_height, int(bar_width) - 2, bar_height)
            painter.drawRoundedRect(*rect, 3, 6)
            # Draw peak indicator
            painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
            painter.drawLine(
                x + 1, h - peak_height, x + int(bar_width) - 2, h - peak_height
            )

        # Optional: Add a subtle glow at the bottom
        glow = QLinearGradient(0, h - 10, 0, h)
        glow.setColorAt(0, QColor(0, 255, 255, 80))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, h - 10, w, 10)

    def closeEvent(self, event):
        self.fft_worker.stop()
        super().closeEvent(event)
