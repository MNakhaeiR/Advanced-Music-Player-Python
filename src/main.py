from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys, os


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("src/resources/icon.ico")))  # Set here
    from ui.main_window import MainWindow

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
