from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
import sys
from PyQt5.QtGui import QIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("resources/icon.png"))
    app.setApplicationName("Advanced Music Player")
    app.setApplicationVersion("0.1.0")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
