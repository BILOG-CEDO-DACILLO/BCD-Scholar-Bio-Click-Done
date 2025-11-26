# pytest -v tests/test_fillupwindow.py
import sys
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication, QLineEdit, QRadioButton, QComboBox, QDateEdit
from PyQt5.QtCore import QDate

######################### path setup
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.gui.Fillup import FillupWindow

######################### mock app
app = QApplication([])

class TestFillupWindow:

    ######################### setup
    def setup_method(self):
        self.window = FillupWindow(
            username="testuser",
            email="test@test.com",
            password="password",
            status="NON-SCHOLAR",
            app_manager=None
        )

        ######################### mock input fields
        self.window.firstname = QLineEdit()
        self.window.lastname = QLineEdit()
        self.window.mi = QLineEdit()
        self.window.suffix = QLineEdit()
        self.window.civilstatus = QComboBox()
        self.window.sex = QComboBox()
        self.window.birthday = QDateEdit()
        self.window.age = QLineEdit()
        self.window.studentID = QLineEdit()
        self.window.college = QComboBox()
        self.window.yearlevel = QComboBox()
        self.window.program = QComboBox()
        self.window.municipality = QComboBox()
        self.window.phoneno = QLineEdit()
        self.window.profile_manager = type("MockProfile", (), {"current_path": "dummy_path"})()

        ######################### mock buttons
        self.window.adminbtn = QRadioButton()
        self.window.studentbtn = QRadioButton()
        self.window.adminbtn.isChecked = lambda: True
        self.window.studentbtn.isChecked = lambda: False

    ######################### TEST 1: dataInfo required fields
    def test_dataInfo_required_fields(self):
        ######################### fill required fields
        self.window.firstname.setText("John")
        self.window.lastname.setText("Doe")
        self.window.mi.setText("A")
        self.window.suffix.setText("Jr")
        # Add items to comboboxes before setting text
        self.window.civilstatus.addItems(["Single", "Married"])
        self.window.civilstatus.setCurrentText("Single")
        self.window.sex.addItems(["Male", "Female"])
        self.window.sex.setCurrentText("Male")
        self.window.birthday.setDate(QDate(2000, 1, 1))
        self.window.age.setText("23")
        self.window.municipality.addItems(["Balayan", "Calaca"])
        self.window.municipality.setCurrentText("Balayan")
        self.window.phoneno.setText("1234567890")

        ######################### call dataInfo
        self.window.dataInfo()

        ######################### check required_fields values, handle QLineEdit and QDateEdit
        required_values = []
        for f in self.window.required_fields:
            if isinstance(f, QLineEdit):
                required_values.append(f.text().strip())
            elif isinstance(f, QDateEdit):
                required_values.append(f.date().toString("MM/dd/yyyy"))
            else:
                required_values.append(f)  # for combo values
        assert all(required_values)

    ######################### TEST 2: handleForm with empty fields
    def test_handleForm_empty_fields(self, qtbot):
        ######################### empty firstname
        self.window.firstname.setText("")
        result = self.window.handleForm()
        assert result is None

    ######################### TEST 3: handleForm with all fields filled
    def test_handleForm_filled_fields(self, qtbot):
        ######################### fill all fields
        self.window.firstname.setText("John")
        self.window.lastname.setText("Doe")
        self.window.mi.setText("A")
        self.window.suffix.setText("Jr")
        self.window.civilstatus.setCurrentText("Single")
        self.window.sex.setCurrentText("Male")
        self.window.birthday.setDate(QDate(2000, 1, 1))
        self.window.age.setText("23")
        self.window.municipality.setCurrentText("Balayan")
        self.window.phoneno.setText("1234567890")

        result = self.window.handleForm()
        ######################### handleForm returns None if everything passes
        assert result is None
