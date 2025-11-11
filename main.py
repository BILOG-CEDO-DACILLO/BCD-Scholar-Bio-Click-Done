import sys
from PyQt5 import QtWidgets
from app.gui.login_window import LoginWindow, SignUpWindow


class MainApp(QtWidgets.QStackedWidget):
    def __init__(self):
        super().__init__()


        self.login_window = LoginWindow()
        self.signup_window = SignUpWindow()

        self.addWidget(self.login_window)
        self.addWidget(self.signup_window)

        self.setFixedSize(800, 600)
        self.setWindowTitle("BUYTASTIC")

        self.login_window.sign_up.clicked.connect(self.show_signup)

    def show_signup(self):
        self.setCurrentIndex(1)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = MainApp()
    widget.show()
    sys.exit(app.exec_())
