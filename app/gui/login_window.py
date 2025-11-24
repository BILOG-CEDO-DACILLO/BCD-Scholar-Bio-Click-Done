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

# ---------------- Main Dialog ----------------
class LogandSign(MyWindow):
    def __init__(self, app_manager=None):
        super().__init__()
        self.app_manager = app_manager
        self.setup_paths_and_icons()
        self.setup_ui()
        self.setup_fonts()
        self.setup_shadows()
        self.setup_connections()

        #-------------------------------------------- This setups the paths ----------------
    def setup_paths_and_icons(self):
        current_file_path = Path(__file__).resolve()
        self.project_root = current_file_path.parent.parent
        asset_paths = {
            'view_icon': self.project_root / 'assets' / 'view.png',
            'hidden_icon': self.project_root / 'assets' / 'hide.png',
            'ui': self.project_root / 'assets' / 'logandsignUI.ui',
            'isb_font': self.project_root / 'assets' / 'InclusiveSans-Bold.ttf',
            'isr_font': self.project_root / 'assets' / 'InclusiveSans-Regular.ttf'
        }
        for key, path in asset_paths.items():
            if not path.exists():
                raise FileNotFoundError(f"Required file not found: {path}")
            setattr(self, f"{key}_path", path)
        self.icon1 = QIcon(str(self.view_icon_path))
        self.icon2 = QIcon(str(self.hidden_icon_path))

        self.password_states = {}

        #-------------------------------------------- This setups the UI ----------------

        #-------------------------------------------- This setups the UI -------------------

    def setup_ui(self):
        uic.loadUi(self.ui_path, self)
        self.database = Database()

        self.viewpass.setIcon(self.icon1)
        self.viewpass2.setIcon(self.icon1)
        self.viewpass3.setIcon(self.icon1)

########################################## STYLE AREA ###############################################

        #-------------------------------------------- This setups the stylized fonts ----------------
    def setup_fonts(self):

        self.largelabel_font = load_font(self.isb_font_path, 32, bold=True)
        self.mediumlabel_font = load_font(self.isb_font_path, 14, bold=True)
        self.field_font = load_font(self.isr_font_path, 10, bold=False)

        font_map = {
            self.largelabel_font: [self.signuplbl, self.loginlbl],
            self.mediumlabel_font: [self.registerbtn, self.loginbtn, self.loginswitch],
            self.field_font: [self.usernamefield, self.username, self.emailfield,
            self.passwordfield, self.passwordfield_2, self.password, self.forgotpass, self.switchlabel]
        }
        for font, widgets in font_map.items():
            for widget in widgets:
                widget.setFont(font)


        #-------------------------------------------- This setups the hover shadows ----------------
    def setup_shadows(self):

        widgets_to_shadow = [
            self.registerbtn, self.loginbtn, self.loginswitch,
            self.usernamefield, self.emailfield, self.passwordfield,
            self.username, self.password, self.forgotpass, self.passwordfield_2
        ]
        for widget in widgets_to_shadow:
            HoverShadow(widget)

        #-------------------------------------------- This setups the button functions ----------------
    def setup_connections(self):
        self.loginswitch.clicked.connect(self.switchtologin)
        self.exitbtn.clicked.connect(self.close)
        self.registerbtn.clicked.connect(self.handle_signup)
        self.loginbtn.clicked.connect(self.handle_login)
        self.viewpass.clicked.connect(lambda: self.toggle_password_visibility(self.viewpass, self.passwordfield))
        self.viewpass2.clicked.connect(lambda: self.toggle_password_visibility(self.viewpass2, self.password))
        self.viewpass3.clicked.connect(lambda: self.toggle_password_visibility(self.viewpass3, self.passwordfield_2))

    def animate_widget(self, widget, end_point, duration=1000):
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(widget.pos())
        anim.setEndValue(end_point)
        anim.setEasingCurve(QtCore.QEasingCurve.OutQuint)
        anim.start()
        return anim
    def switchtologin(self):
        if self.loginswitch.text() == "Login":
            self.loginswitch.setText("Sign Up")
            self.anim = self.animate_widget(self.switchwidget, QPoint(-280, 0))
            self.anim2 = self.animate_widget(self.innerwidget, QPoint(280, 0))
            self.anim3 = self.animate_widget(self.exitbtn, QPoint(320, 30))
            self.usernamefield.setText("")
            self.emailfield.setText("")
            self.passwordfield.setText("")
            self.passwordfield_2.setText("")
        else:
            self.loginswitch.setText("Login")
            self.anim = self.animate_widget(self.switchwidget, QPoint(560, 0))
            self.anim2 = self.animate_widget(self.innerwidget, QPoint(70, 0))
            self.anim3 = self.animate_widget(self.exitbtn, QPoint(560, 30))
            self.username.setText("")
            self.password.setText("")

########################################### FUNCTIONS ################################################
    def toggle_password_visibility(self, button, field):
        if button not in self.password_states:
            self.password_states[button] = True

        if self.password_states[button]:
            self.password_states[button] = False
            button.setIcon(self.icon1)
            field.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_states[button] = True
            button.setIcon(self.icon2)
            field.setEchoMode(QtWidgets.QLineEdit.Password)

    def handle_signup(self):
        username = self.usernamefield.text().strip()
        email = self.emailfield.text().strip()
        password = self.passwordfield.text()
        password2 = self.passwordfield_2.text()
        status = "NON-SCHOLAR"
        address = "@bcd.scholarship.edu.ph"

        if not username or not email or not password or not password2:
            QMessageBox.warning(self, "Warning", "Fill all fields below.", QMessageBox.Ok)
            return
        elif password != password2:
            QMessageBox.warning(self, "Warning", "Passwords don't match, Try again!", QMessageBox.Ok)
            return

        elif not email.endswith("@bcd.scholarship.edu.ph"):
            QMessageBox.warning(self, "Warning", "Please use the given domain address.", QMessageBox.Ok)
            return

        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to sign up using this username, email, and password?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        result = database.handle_signup_data(username, email, password, status)

        if result is True:
            QMessageBox.information(self, "Success", "Sign up successful!", QMessageBox.Ok)
            self.app_manager.show_fillup()
        else:
            _, reason = result
            QMessageBox.critical(self, "Sign up failed", reason, QMessageBox.Ok)

    def handle_login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Warning", "Fill all fields below.", QMessageBox.Ok)
            return

        user = database.handle_login_data(username, password)
        if user == False:
            QMessageBox.warning(self, "Error", f"Failed to log in, wrong username or password. Maybe account does not exist?", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "Success", "Login successful!", QMessageBox.Ok)
            self.app_manager.show_mainwindow(username)


        #-------------------------------------------- Open the signup dialog via the manager ----------
    def show_fillup(self):
        self.app_manager.show_fillup()


# ---------------- Main ----------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = LogandSign(app_manager)
    dialog.show()
    sys.exit(app.exec_())
