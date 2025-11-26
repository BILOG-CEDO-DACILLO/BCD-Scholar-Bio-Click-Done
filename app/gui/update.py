import sys
import hashlib
from pathlib import Path
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import (QPropertyAnimation, QPoint, QObject, QEvent, Qt, QDate, QByteArray)
from PyQt5.QtGui import (QFont, QFontDatabase, QColor, QPixmap, QRegion)
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect, QMessageBox, QComboBox, QFileDialog)
import sqlite3
from app.database.database import Database, database
from app.utils.util import (HoverShadow, setup_profile, load_font, setupComboBox, opac)


class updateWindow(QtWidgets.QDialog):
    def __init__(self, username=None, email=None, password=None, status=None, app_manager=None):
        try:
            super().__init__()
            self.status = status
            self.username = username
            self.email = email
            self.password = password
            self.app_manager = app_manager
            self.new_photo_path = None
            self.existing_photo_blob = None

            if not self.username:
                QMessageBox.critical(self, "Error", "Username is required to edit the profile.")
                QtCore.QTimer.singleShot(0, self.close)
                return

            self.setup_paths()
            self.setup_ui()

            self.profile_manager = setup_profile(self.profilephoto, str(self.profilelabel_path))

            self.Set_up_comboBox()
            self.setupFontsandICons()
            self.setup_shadows()

            self.load_existing_user_data()
            self.savebtn.clicked.connect(self.save_updated_user_details)

        except FileNotFoundError as fnf:
            QMessageBox.critical(None, "Initialization Error",
                                 f"Failed to start: A required asset file was not found. {fnf}")
            QtCore.QTimer.singleShot(0, self.close)
        except Exception as e:
            QMessageBox.critical(None, "Initialization Error",
                                 f"Failed to start the update window due to a system error: {e}")
            QtCore.QTimer.singleShot(0, self.close)
    ########################################################################################## set-up paths ############
    def setup_paths(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
            'ui': self.project_root / 'assets' / 'update.ui',
            'isb_font': self.project_root / 'assets' / 'InclusiveSans-Bold.ttf',
            'isr_font': self.project_root / 'assets' / 'InclusiveSans-Regular.ttf',
            'profilelabel': self.project_root / 'assets' / 'profilephoto.png'
        }
        for key, path in asset_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {path}")
            setattr(self, f"{key}_path", path)

    ########################################################################################## set-up uis ##############
    def setup_ui(self):
        try:
            uic.loadUi(self.ui_path, self)
            self.studentbtn.setDisabled(True)
            self.adminbtn.setDisabled(True)

            try:
                self.birthday.setDisplayFormat("MM/dd/yyyy")
            except AttributeError:
                pass

            self.profilephoto.installEventFilter(self)

        except Exception as e:
            QMessageBox.critical(self, "UI Setup Error", f"Failed to load or configure UI elements: {e}")
            raise

    def eventFilter(self, source, event):
        if source is self.profilephoto and event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self.select_profile_photo()
            return True
        return super().eventFilter(source, event)

    ########################################################################################## update profile ##########
    def select_profile_photo(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Select New Profile Photo",
                str(Path.home()),
                "Image Files (*.png *.jpg *.jpeg)"
            )

            if filename:
                pixmap = QPixmap(filename)
                if pixmap.isNull():
                    return

                self.profilephoto.setPixmap(pixmap.scaled(
                    self.profilephoto.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                ))

                self.new_photo_path = filename
                self.existing_photo_blob = None

                if hasattr(self.profile_manager, 'current_path'):
                    self.profile_manager.current_path = filename
                else:
                    print("Warning: Profile manager does not have 'current_path' attribute.")


        except Exception as e:
            pass

    ########################################################################################## set-up fonts & icons ####
    def setupFontsandICons(self):
        self.largelabel_font = load_font(self.isb_font_path, 32, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)

        font_map = {
            self.largelabel_font: [],
            self.mediumlabel_font: [],
            self.field_font: [self.firstname, self.lastname, self.mi, self.suffix, self.civilstatus, self.sex,
                              self.age, self.studentID, self.college, self.yearlevel, self.program,
                              self.municipality, self.phoneno, self.adminbtn, self.studentbtn]
        }

        for font, widgets in font_map.items():
            for widget in widgets:
                try:
                    widget.setFont(font)
                except AttributeError:
                    pass

    def setup_shadows(self):
        widgets_to_shadow = [
            self.firstname, self.lastname, self.mi, self.suffix, self.civilstatus, self.sex,
            self.birthday, self.age, self.studentID, self.college, self.yearlevel, self.program,
            self.municipality, self.phoneno, self.profilephoto, self.adminbtn, self.studentbtn
        ]

        for widget in widgets_to_shadow:
            try:
                HoverShadow(widget, blur=10, offset_x=0, offset_y=0, color=QColor(0, 0, 0, 160))
            except AttributeError:
                pass

    def Set_up_comboBox(self):
        self.civilstatuses = ["Single", "Married", "Divorced", "Widowed"]
        self.genders = ["Male", "Female", "Other"]
        self.colleges = ["CICS", "CTE", "CHS", "CAS", "CABEIHM", "CCJE"]
        self.years = ["1st - Year", "2nd - Year", "3rd - Year", "4th - Year"]
        self.municipalities = ["Balayan", "Calaca", "Calatagan", "Lemery", "Lian", "Nasugbu", "Tuy"]

        self.program_data = {
            "CICS": ["BSIT", "BSIT-BA", "BSIT-NT"],
            "CAS": ["BA Comm", "BSFT", "BSP", "BSFAS"],
            "CABEIHM": ["BSA", "BSMA", "BSBA - FM", "BSBA - MM", "BSBA - HRM", "BSHM", "BSTM"],
            "CCJE": ["BSCrim"],
            "CTE": ["BEED", "BSEd - English", "BSEd - Math", "BSEd - Sciences", "BSEd - Filipino",
                    "BSEd - Social Studies", "BPEd"],
            "CHS": ["BSN", "BSND"]
        }

        setupComboBox(self.civilstatus, self.civilstatuses, "Civil Status")
        setupComboBox(self.sex, self.genders, "Gender")
        setupComboBox(self.college, self.colleges, "College")
        setupComboBox(self.program, [], "Program")
        setupComboBox(self.yearlevel, self.years, "Year Level")
        setupComboBox(self.municipality, self.municipalities, "Municipality")

        self.college.currentTextChanged.connect(self.updateProgramComboBox)
        self.program.setEnabled(False)

        self.adminbtn.toggled.connect(lambda: self._toggle_student_fields(self.studentbtn.isChecked()))
        self.studentbtn.toggled.connect(lambda: self._toggle_student_fields(self.studentbtn.isChecked()))

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

    def _toggle_student_fields(self, enable):
        try:
            self.studentID.setEnabled(enable)
            self.college.setEnabled(enable)
            self.yearlevel.setEnabled(enable)
            self.program.setEnabled(enable and self.college.currentText() != "College")

            if not enable:
                self.studentID.setText("none")
                if self.college.count() > 0: self.college.setCurrentText("College")
                if self.yearlevel.count() > 0: self.yearlevel.setCurrentText("Year Level")
                if self.program.count() > 0: self.program.setCurrentText("Program")
                self.program.setEnabled(False)
        except AttributeError:
            pass
    ########################################################################################## set-up existing user data
    def load_existing_user_data(self):
        try:
            user_data = database.handle_information_data(usernameoremail=self.username)

            if not user_data:
                QMessageBox.warning(self, "Data Error", "Could not retrieve existing user information.")
                return

            self.firstname.setText(user_data[6] or "")
            self.lastname.setText(user_data[7] or "")
            self.mi.setText(user_data[8] or "")
            self.suffix.setText(user_data[9] or "")
            self.age.setText(str(user_data[13]) if user_data[13] is not None else "")
            self.studentID.setText(user_data[14] or "")
            self.phoneno.setText(user_data[19] or "")

            db_date_string = user_data[12]
            if db_date_string:
                date_obj = QDate.fromString(db_date_string, "MM/dd/yyyy")
                if date_obj.isValid():
                    self.birthday.setDate(date_obj)

            acctype = user_data[1]
            is_student = (acctype == "STUDENT")
            if acctype == "ADMIN":
                self.adminbtn.setChecked(True)
            else:
                self.studentbtn.setChecked(True)

            setupComboBox(self.civilstatus, self.civilstatuses, user_data[10] or "Civil Status")
            setupComboBox(self.sex, self.genders, user_data[11] or "Gender")
            setupComboBox(self.yearlevel, self.years, user_data[16] or "Year Level")
            setupComboBox(self.municipality, self.municipalities, user_data[18] or "Municipality")

            college_name = user_data[15] or "College"
            program_name = user_data[17] or "Program"

            setupComboBox(self.college, self.colleges, college_name)

            if college_name in self.program_data:
                self.updateProgramComboBox(college_name)
                if program_name in self.program_data[college_name]:
                    self.program.setCurrentText(program_name)

            self._toggle_student_fields(is_student)

            profile_blob = user_data[5]
            if profile_blob:
                pixmap = QPixmap()
                pixmap.loadFromData(profile_blob)
                self.profilephoto.setPixmap(pixmap.scaled(
                    self.profilephoto.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                self.existing_photo_blob = profile_blob
                self.new_photo_path = None

        except Exception as e:
            QMessageBox.critical(self, "Data Load Error",
                                 f"An unexpected error occurred while loading profile data. Details: {e}")

    def dataInfo(self):
        acctype = "STUDENT" if self.studentbtn.isChecked() else "ADMIN"

        self._toggle_student_fields(acctype == "STUDENT")

        self.acctype = acctype
        self.userfirstname = self.firstname.text().strip()
        self.userlastname = self.lastname.text().strip()
        self.usermiddlename = self.mi.text().strip()
        self.usersuffix = self.suffix.text().strip()

        self.usercivilstatus = self.civilstatus.currentText()
        self.usergender = self.sex.currentText()
        self.userbirthday = self.birthday.date().toString("MM/dd/yyyy")
        self.userage = self.age.text().strip()

        self.userstudentID = self.studentID.text().strip()
        self.usercollege = self.college.currentText()
        self.useryearlevel = self.yearlevel.currentText()
        self.userprogram = self.program.currentText()

        self.usermunicipality = self.municipality.currentText()
        self.userphoneno = self.phoneno.text().strip()


        self.userprofilephoto = self.new_photo_path

        if acctype == "ADMIN":
            self.required_fields = [
                self.userfirstname, self.userlastname, self.usercivilstatus,
                self.usergender, self.userbirthday, self.userage,
                self.usermunicipality, self.userphoneno
            ]
        else:
            self.required_fields = [
                self.userfirstname, self.userlastname, self.usercivilstatus,
                self.usergender, self.userbirthday, self.userage,
                self.userstudentID, self.usercollege, self.useryearlevel,
                self.userprogram, self.usermunicipality, self.userphoneno
            ]

    def save_updated_user_details(self):
        try:
            self.dataInfo()

            invalid_placeholders = {
                "Civil Status", "Gender", "College",
                "Program", "Year Level", "Municipality"
            }

            if any(f == "" for f in self.required_fields if isinstance(f, str) and f not in ["none"]):
                QMessageBox.critical(self, "Error", "Please fill all required profile fields.")
                return

            is_valid = True
            if self.acctype == "ADMIN":
                if (self.usercivilstatus in invalid_placeholders or
                        self.usergender in invalid_placeholders or
                        self.usermunicipality in invalid_placeholders):
                    is_valid = False
            else:
                if (self.usercivilstatus in invalid_placeholders or
                        self.usergender in invalid_placeholders or
                        self.usercollege in invalid_placeholders or
                        self.userprogram in invalid_placeholders or
                        self.useryearlevel in invalid_placeholders or
                        self.usermunicipality in invalid_placeholders):
                    is_valid = False

            if not is_valid:
                QMessageBox.critical(self, "Error", "Please select a valid option from all dropdowns.")
                return

            try:
                user_age = int(self.userage)
            except ValueError:
                QMessageBox.critical(self, "Error", "Age must be a valid number.")
                return

            success_profile = False
            success_password = True


            photo_to_save = self.new_photo_path

            try:
                success_profile = database.update_user_info(
                    username=self.username,
                    acctype=self.acctype,
                    profile_photo_path=photo_to_save,
                    first_name=self.userfirstname,
                    last_name=self.userlastname,
                    middle_initial=self.usermiddlename,
                    suffix=self.usersuffix,
                    civil_status=self.usercivilstatus,
                    gender=self.usergender,
                    date_of_birth=self.userbirthday,
                    age=user_age,
                    student_id=self.userstudentID,
                    college=self.usercollege,
                    year_level=self.useryearlevel,
                    program=self.userprogram,
                    municipality=self.usermunicipality,
                    phone_number=self.userphoneno
                )
            except AttributeError:
                QMessageBox.critical(self, "DB Error", "The required database.update_user_info method is missing.")
                return

            if success_profile and success_password:
                QMessageBox.information(self, "Success", "Profile updated successfully.")

                if self.app_manager:
                    self.app_manager.show_main_window(self.username)

                self.close()
            else:
                msg = "Failed to update the profile record."
                QMessageBox.critical(self, "Error", msg)

        except Exception as e:
            QMessageBox.critical(self, "Save Error",
                                 f"An unexpected error occurred while saving profile changes. Details: {e}")

    def show_login(self):
        if self.app_manager:
            self.app_manager.show_login()
        else:
            print("Error: App manager not available to show login window.")