import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QPropertyAnimation, QPoint, QObject, QEvent
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QIcon)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
import sqlite3
from app.assets import res_rc
from app.database.DBloginsignup import Database, database
from app.utils.util import (MyWindow, HoverShadow, load_font)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.setup_paths_and_icons()
        self.setup_ui()


        #-------------------------------------------- This setups the paths ----------------
    def setup_paths_and_icons(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
            'view_icon': self.project_root / 'assets' / 'view.png',
            'hidden_icon': self.project_root / 'assets' / 'hide.png',
            'ui': self.project_root / 'assets' / 'MainWindow.ui',
            'isb_font': self.project_root / 'assets' / 'InclusiveSans-Bold.ttf',
            'isr_font': self.project_root / 'assets' / 'InclusiveSans-Regular.ttf'
        }
        for key, path in asset_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {path}")
            setattr(self, f"{key}_path", path)

        # -------------------------------------------- This setups the UI ----------------
    def setup_ui(self):
        uic.loadUi(self.ui_path, self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())