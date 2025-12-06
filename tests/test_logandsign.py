#  pytest -v tests/test_logandsign.py
import sys
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton

######################### path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from app.gui.login_window import LogandSign

######################### mock app
app = QApplication([])


class TestLoginWindow:
    def setup_method(self):
        self.window = LogandSign(app_manager=None)

        self.window.usernamefield = QLineEdit()
        self.window.emailfield = QLineEdit()
        self.window.passwordfield = QLineEdit()
        self.window.passwordfield_2 = QLineEdit()

        self.window.username = QLineEdit()
        self.window.password = QLineEdit()

    ######################### password toggle test
    def test_toggle_password_visibility(self):
        btn = QPushButton()
        field = QLineEdit()

        self.window.toggle_password_visibility(btn, field)
        assert btn in self.window.password_states
        assert self.window.password_states[btn] is False

        self.window.toggle_password_visibility(btn, field)
        assert self.window.password_states[btn] is True

    ######################### signup empty field test
    def test_signup_empty_fields(self):
        self.window.usernamefield.setText("")
        self.window.emailfield.setText("")
        self.window.passwordfield.setText("")
        self.window.passwordfield_2.setText("")

        result = self.window.handle_signup()
        assert result is None

    ######################### login empty field test
    def test_login_empty_fields(self):
        self.window.username.setText("")
        self.window.password.setText("")

        result = self.window.handle_login()
        assert result is None
