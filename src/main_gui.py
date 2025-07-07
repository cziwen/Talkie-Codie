import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from src.ui.components import MainWidget
import os
import shutil

class NewMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Talkie-Codie - AI Rephrased Prompt')
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon('assets/images/Icon.png'))
        self.main_widget = MainWidget()
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        # Clear cache directory when closing window
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir, topdown=False):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except Exception:
                        pass
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if os.path.exists(dir_path) and not os.listdir(dir_path):
                            os.rmdir(dir_path)
                    except Exception:
                        pass
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NewMainWindow()
    window.show()
    sys.exit(app.exec()) 