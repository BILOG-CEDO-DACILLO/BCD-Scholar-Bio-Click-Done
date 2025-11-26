# pytest -v tests/test_updateWindow_basic.py
import sys
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication, QLineEdit, QComboBox, QPushButton, QLabel

######################### QApplication
app = QApplication.instance() or QApplication([])

sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.gui.update import updateWindow


class MockAppManager:
    def show_main_window(self, username):
        pass

    def show_login(self):
        pass


class TestUpdateWindowBasic:
    def setup_method(self):
        self.window = updateWindow(
            username="testuser",
            email="test@test.com",
            password="123",
            status="STUDENT",
            app_manager=MockAppManager()
        )

        for name in [
            "firstname", "lastname", "mi", "suffix", "civilstatus", "sex", "age",
            "studentID", "college", "yearlevel", "program", "municipality",
            "phoneno", "birthday", "profilephoto", "adminbtn", "studentbtn", "savebtn"
        ]:
            setattr(self.window, name, QLabel() if "photo" in name else QLineEdit())


    def test_window_initializes(self):
        assert self.window is not None

    def test_select_profile_photo_runs(self):
        try:
            self.window.select_profile_photo()
            success = True
        except Exception:
            success = False
        assert success