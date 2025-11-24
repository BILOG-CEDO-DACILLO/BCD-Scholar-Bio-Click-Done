import sys
from pathlib import Path
from io import BytesIO
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import (QPropertyAnimation, QPoint, QObject, QEvent, Qt)
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QIcon, QImage, QPixmap, QPainter, QBrush)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox
import sqlite3
from app.assets import res_rc
from app.database.DBloginsignup import (Database, database)
from app.utils.util import (MyWindow, HoverShadow, load_font, DesignShadow, get_rounded_stretched_pixmap)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, username=None, email=None, app_manager=None):
        super().__init__()
        self.username = username
        self.app_manager = app_manager
        self.setup_paths_and_icons()
        self.setup_ui()
        self.setup_fonts()
        self.setup_shadows()
        self.setup_sidebar()
        self.setup_user_info()
        self.bsu_scholarshipBTN()
        #-------------------------------------------- This setups the paths ----------------
    def setup_paths_and_icons(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
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
        self.applylogo.setHidden(True)
        self.nextbtn_2.setDisabled(True)
        self.information.setDisabled(True)
        self.appform.setDisabled(True)
        self.requirements.setDisabled(True)
        self.finish.setDisabled(True)

########################################## STYLE AREA ###############################################

        #-------------------------------------------- This setups the stylized fonts ----------------
    def setup_fonts(self):
        self.largelabel_font = load_font(self.isb_font_path, 36, bold=True)
        self.medlar_font = load_font(self.isb_font_path, 20, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.small_font = load_font(self.isb_font_path, 16, bold=False)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)


        font_map = {
            self.largelabel_font: [self.welcome_lbl],
            self.medlar_font: [self.bsutext, self.userprofilename],
            self.mediumlabel_font: [self.applybtn, self.applybtn2, self.applybtn3, self.applybtn4, self.applybtn5,
                                    self.applybtn6, self.financialLabel, self.bcdLabel, self.educLabel, self.lll_2,
                                    self.acad_2, self.dost_2, self.settings2, self.dashboard2, self.scholar2, self.exit2,
                                    self.profile2, self.home2, self.bsutext2, self.TP, self.nextbtn, self.nextbtn_2],
            self.small_font: [],
            self.field_font: [self.financialLabel2, self.financialLabel3, self.bcdLabel2, self.bcdLabel3, self.educLabel2,
                              self.educLabel3, self.lll2, self.lll3, self.acad2, self.acad3, self.dost2, self.dost3,self.bsutext3,
                              self.bsutext3_2, self.terms, self.cpy, self.useremail],
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
        self.home.clicked.connect(lambda: (self.stacks.setCurrentIndex(1), self.uppertop.setVisible(True), self.applylogo.setHidden(True)))
        self.home2.clicked.connect(lambda: (self.stacks.setCurrentIndex(1), self.uppertop.setVisible(True), self.applylogo.setHidden(True)))
        self.profile.clicked.connect(lambda: (self.stacks.setCurrentIndex(0), self.applylogo.setHidden(True)))
        self.profile2.clicked.connect(lambda: (self.stacks.setCurrentIndex(0), self.applylogo.setHidden(True)))
        self.dashboard.clicked.connect(lambda: (self.uppertop.setVisible(True), self.stacks.setCurrentIndex(2), self.applylogo.setHidden(True)))
        self.dashboard2.clicked.connect(lambda: (self.uppertop.setVisible(True), self.stacks.setCurrentIndex(2), self.applylogo.setHidden(True)))
        self.scholar.clicked.connect(lambda: (self.uppertop.setVisible(True), self.stacks.setCurrentIndex(3), self.applylogo.setHidden(True)))
        self.scholar2.clicked.connect(lambda: (self.uppertop.setVisible(True), self.stacks.setCurrentIndex(3), self.applylogo.setHidden(True)))
        self.applybtn.clicked.connect(lambda: (self.stacks.setCurrentIndex(4),self.bsustacks.setCurrentIndex(0), self.applylogo.setVisible(True)))

    def bsu_scholarshipBTN(self):
        self.nextbtn_2.setDisabled(True)
        self.terms_and_policy.clicked.connect(lambda: self.bsustacks.setCurrentIndex(1))
        self.nextbtn.clicked.connect(lambda: self.bsustacks.setCurrentIndex(1))
        self.information.clicked.connect(lambda: self.bsustacks.setCurrentIndex(2))
        self.nextbtn_2.clicked.connect(lambda: self.bsustacks.setCurrentIndex(2))
        self.appform.clicked.connect(lambda: self.bsustacks.setCurrentIndex(3))
        self.nextbtn_3.clicked.connect(lambda: self.bsustacks.setCurrentIndex(3))

    def setup_user_info(self):
        self.user_info = database.handle_information_data(username=self.username)
        fullname = " ".join([self.user_info[2], self.user_info[4], self.user_info[3], self.user_info[5]])
        self.userprofilename.setText(fullname)
        cpy = " - ".join([self.user_info[11], self.user_info[13], self.user_info[12]])
        self.cpy.setText(cpy)
        self.useremail.setText(self.user_info[-1])

        if self.user_info:
            profile_blob = self.user_info[1]

            if profile_blob:
                # Apply rounded stretched pixmap to each label
                for label in [self.userProfile, self.userProfile2, self.userProfile3]:
                    w, h = label.width(), label.height()
                    pixmap = get_rounded_stretched_pixmap(profile_blob, w, h)
                    if pixmap:
                        label.setPixmap(pixmap)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())