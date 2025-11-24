from PyQt5.QtWidgets import QApplication

from app.gui.login_window import LogandSign
from app.gui.Fillup import FillupWindow
from app.gui.MainWindow import MainWindow


class ApplicationManager(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Only instantiate login at startup
        self.logandsign = LogandSign(app_manager=self)

        self.fillup = None
        self.mainwindow = None

        self.current_main_window = None


    def start(self):
        self._show_window(self.logandsign)


    # ----------------- LOGIN → MAIN WINDOW (WITH USERNAME) -----------------
    def show_mainwindow(self, username):
        # Create MainWindow with username
        self.mainwindow = MainWindow(username=username, app_manager=self)

        # Show it maximized
        self._show_window(self.mainwindow, maximized=True)

        # Close login window
        self.logandsign.close()


    # ----------------- LOGIN → FILLUP WINDOW -----------------
    def show_fillup(self):
        if not self.fillup:
            self.fillup = FillupWindow(app_manager=self)
        self._show_window(self.fillup)


    # Generic window show function
    def _show_window(self, window, maximized=False):
        if self.current_main_window:
            self.current_main_window.hide()

        self.current_main_window = window

        if maximized:
            window.showMaximized()
        else:
            window.show()


    # Return to login screen
    def show_login(self):
        self._show_window(self.logandsign)
