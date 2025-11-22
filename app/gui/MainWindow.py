import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QPropertyAnimation, QPoint, QObject, QEvent
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QIcon)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
import sqlite3
from app.assets import res_rc
from app.utils.util import (MyWindow, HoverShadow, load_font, DesignShadow)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.setup_paths_and_icons()
        self.setup_ui()
        self.setup_fonts()
        self.setup_shadows()
        self.setup_sidebar()


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
        self.sidebar.setHidden(True)

########################################## STYLE AREA ###############################################

        #-------------------------------------------- This setups the stylized fonts ----------------
    def setup_fonts(self):

        self.largelabel_font = load_font(self.isb_font_path, 36, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)

        font_map = {
            self.largelabel_font: [self.welcome_lbl],
            self.mediumlabel_font: [self.applybtn, self.applybtn2, self.applybtn3, self.applybtn4, self.applybtn5,
                                    self.applybtn6, self.financialLabel, self.bcdLabel, self.educLabel, self.lll_2,
                                    self.acad_2, self.dost_2, self.settings2, self.dashboard2, self.scholar2, self.exit2,
                                    self.profile2, self.home2],
            self.field_font: [self.financialLabel2, self.financialLabel3, self.bcdLabel2, self.bcdLabel3, self.educLabel2,
                              self.educLabel3, self.lll2, self.lll3, self.acad2, self.acad3, self.dost2, self.dost3]
        }
        for font, widgets in font_map.items():
            for widget in widgets:
                widget.setFont(font)

        # -------------------------------------------- This setups the hover shadows ----------------
    def setup_shadows(self):
        widgets_to_shadow = [
            self.financial_assistance, self.bcd_scholarship, self.lll, self.acad, self.educ_assistance, self.dost
        ]
        for widget in widgets_to_shadow:
            DesignShadow(widget)
        #---------------------------------------------- This functions switch screens ---------------
    def setup_sidebar(self):
        self.dashboard.clicked.connect(self.switch_to_dashboard)
        self.dashboard2.clicked.connect(self.switch_to_dashboard)
        self.home.clicked.connect(self.switch_to_home)
        self.home2.clicked.connect(self.switch_to_home)
        self.profile.clicked.connect(self.switch_to_profile)
        self.profile2.clicked.connect(self.switch_to_profile)

    def switch_to_profile(self):
        self.stacks.setCurrentIndex(0)

    def switch_to_home(self):
        self.stacks.setCurrentIndex(1)

    def switch_to_dashboard(self):
        self.stacks.setCurrentIndex(2)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())