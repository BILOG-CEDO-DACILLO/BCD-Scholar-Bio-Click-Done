import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QPropertyAnimation, QPoint, QObject, QEvent, Qt  # Import Qt for alignment/scaling
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QIcon, QPixmap, QRegion)  # Added QPixmap and QRegion
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox, QComboBox, QFileDialog  # Added QFileDialog
import sqlite3

from lxml.html.formfill import fill_form

from app.assets import res_rc
from app.database.DBuserfillup import DBuserfillup, database
from app.utils.util import (MyWindow, HoverShadow, setup_profile, load_font, setupComboBox, opac)


class FillupWindow(MyWindow):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.setup_paths()
        self.setup_ui()

        # --- NEW PROFILE PHOTO SETUP ---
        self.profile_manager = setup_profile(self.profilephoto, str(self.profilelabel_path))
        # -------------------------------

        self.Set_up_comboBox()
        self.setupFontsandICons()
        self.setup_shadows()
        self.submitbtn.clicked.connect(self.handleForm)

    # -------------------------------------------- This setups the paths ----------------
    def setup_paths(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
            'ui': self.project_root / 'assets' / 'signupform.ui',
            'isb_font': self.project_root / 'assets' / 'InclusiveSans-Bold.ttf',
            'isr_font': self.project_root / 'assets' / 'InclusiveSans-Regular.ttf',
            'profilelabel': self.project_root / 'assets' / 'profilephoto.png'
        }
        for key, path in asset_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {path}")
            setattr(self, f"{key}_path", path)

    # -------------------------------------------- This setups the UI -------------------
    def setup_ui(self):
        uic.loadUi(self.ui_path, self)
        self.database = DBuserfillup()
        opac(self, self.label, 0.75)

    ########################################## STYLE AREA ###############################################
    # -------------------------------------------- This setups the stylized fonts ----------------
    def setupFontsandICons(self):
        self.largelabel_font = load_font(self.isb_font_path, 32, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)

        font_map = {
            self.largelabel_font: [self.Title],
            self.mediumlabel_font: [self.submitbtn],
            self.field_font: [self.firstname, self.lastname, self.mi, self.suffix, self.civilstatus, self.sex,
                              self.birthday, self.age, self.studentID, self.college, self.yearlevel, self.program,
                              self.municipality, self.phoneno, self.textlabel]
        }
        for font, widgets in font_map.items():
            for widget in widgets:
                widget.setFont(font)

    # -------------------------------------------- This setups the hover shadows ----------------
    def setup_shadows(self):
        widgets_to_shadow = [
            self.firstname, self.lastname, self.mi, self.suffix, self.civilstatus, self.sex,
            self.birthday, self.age, self.studentID, self.college, self.yearlevel, self.program,
            self.municipality, self.phoneno, self.submitbtn, self.profilephoto
        ]
        for widget in widgets_to_shadow:
            HoverShadow(widget)

    # -------------------------------------------- This setups the ComboBox ---------------------
    def Set_up_comboBox(self):
        self.civilstatuses = ["Single", "Married", "Divorced/Annulled", "Widowed"]
        self.genders = ["Male", "Female", "Other"]
        self.colleges = ["CICS", "BSN", "CAS", "CABEIHM", "CJE"]
        self.years = ["1st - Year", "2nd - Year", "3rd - Year", "4th - Year"]
        self.municipalities = ["Balayan", "Calaca", "Calatagan", "Lemery", "Nasugbu", "Tuy"]

        self.program_data = {
            "CICS": ["BSIT", "COMENG", "COMSCI"],
            "BSN": ["NURSING", "CRIM", "MASSCOM"],
            "CAS": ["PSYCH", "SOCIOLOGY"],
            "CABEIHM": ["BSED", "BEED"],
            "CJE": ["LAW", "POLSCI"]
        }

        self.civil_status_setup = setupComboBox(self.civilstatus, self.civilstatuses, "Civil Status")
        self.sex_setup = setupComboBox(self.sex, self.genders, "Gender")
        self.college_setup = setupComboBox(self.college, self.colleges, "College")
        self.program_setup = setupComboBox(self.program, [], "Program")
        self.yearlevel_setup = setupComboBox(self.yearlevel, self.years, "Year Level")
        self.municipality_setup = setupComboBox(self.municipality, self.municipalities, "Municipality")
        self.college.currentTextChanged.connect(self.updateProgramComboBox)
        self.program.setEnabled(False)

    def updateProgramComboBox(self, selected_college_name: str):
        programs_list = self.program_data.get(selected_college_name)
        self.program.clear()

        if programs_list:
            self.program.setEnabled(True)
            setupComboBox(self.program, programs_list, "Program")
        else:
            self.program.setEnabled(False)
            self.program.addItem("Program")
            self.program.setCurrentIndex(0)

    def dataInfo(self):
        self.userfirstname = self.firstname.text().strip()
        self.userlastname = self.lastname.text().strip()
        self.usermiddlename = self.mi.text().strip()
        self.usersuffix = self.suffix.text().strip()

        self.usercivilstatus = self.civilstatus.currentText()
        self.usergender = self.sex.currentText()
        self.userbirthday = self.birthday.text().strip()
        self.userage = self.age.text().strip()
        self.userstudentID = self.studentID.text().strip()
        self.usercollege = self.college.currentText()
        self.useryearlevel = self.yearlevel.currentText()
        self.userprogram = self.program.currentText()
        self.usermunicipality = self.municipality.currentText()
        self.userphoneno = self.phoneno.text().strip()

        self.userprofilephoto = self.profile_manager.current_path

        self.required_fields = [
            self.userfirstname, self.userlastname, self.usercivilstatus,
            self.usergender, self.userbirthday, self.userage,
            self.userstudentID, self.usercollege, self.useryearlevel,
            self.userprogram, self.usermunicipality, self.userphoneno
        ]

    def handleForm(self):
        self.dataInfo()

        invalid_placeholders = {
            "Civil Status", "Gender", "College",
            "Program", "Year Level", "Municipality"
        }

        # Check empty fields
        if any(f == "" for f in self.required_fields):
            QMessageBox.critical(self, "Error", "Please fill all required fields.")
            return

        # Check invalid dropdown selections
        if (self.usercivilstatus in invalid_placeholders or
                self.usergender in invalid_placeholders or
                self.usercollege in invalid_placeholders or
                self.userprogram in invalid_placeholders or
                self.useryearlevel in invalid_placeholders or
                self.usermunicipality in invalid_placeholders):
            QMessageBox.critical(self, "Error", "Please select a valid option from the dropdowns.")
            return

        # Insert to DB
        result = database.fillform(
            self.userprofilephoto,
            self.userfirstname,
            self.userlastname,
            self.usermiddlename,
            self.usersuffix,
            self.usercivilstatus,
            self.usergender,
            self.userbirthday,
            self.userage,
            self.userstudentID,
            self.usercollege,
            self.useryearlevel,
            self.userprogram,
            self.usermunicipality,
            self.userphoneno
        )

        if result:
            QMessageBox.information(self, "Success", "Record saved successfully.")
            self.app_manager.show_login()
        else:
            QMessageBox.critical(self, "Error", "Failed to save the record.")

    def show_login(self):
        self.app_manager.show_login()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = FillupWindow()
    dialog.show()
    sys.exit(app.exec_())