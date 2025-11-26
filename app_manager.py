from PyQt5.QtWidgets import QApplication
from app.gui.login_window import LogandSign
from app.gui.Fillup import FillupWindow
from app.gui.MainWindow import MainWindow
from app.gui.update import updateWindow


class ApplicationManager(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.logandsign = LogandSign(app_manager=self)

        self.fillup = None
        self.mainwindow = None
        self.updatewindow = None # Initialize the update window attribute
        self.current_main_window = None


    def start(self):
        self._show_window(self.logandsign)


    # ----------------- LOGIN → FILLUP WINDOW -----------------
    def show_fillup(self, username, email, password, status):
        if not self.fillup:
            self.fillup = FillupWindow(username=username, email=email, password=password, status=status, app_manager=self)
        self._show_window(self.fillup)


    # ----------------- SHOW UPDATE WINDOW (New) -----------------
    def show_update_window(self, username, email=None, password=None, status=None):
        if not self.updatewindow:
            self.updatewindow = updateWindow(
                username=username,
                email=email,
                password=password,
                status=status,
                app_manager=self
            )
        self.updatewindow.exec_()


    # ----------------- LOGIN/UPDATE → MAIN WINDOW -----------------
    def show_mainwindow(self, username):
        """Primary method to show the main application window."""
        self.mainwindow = MainWindow(username=username, app_manager=self)
        self._show_window(self.mainwindow, maximized=True)
        # Assuming the caller (login or update) will handle its own closure
        if self.logandsign.isVisible():
            self.logandsign.close()


    # ----------------- UPDATE → MAIN WINDOW (Alias used by updateWindow.py) -----------------
    def show_main_window(self, username):
        """Alias for show_mainwindow, used for consistency with updateWindow.py calls."""
        self.show_mainwindow(username)


    # Generic window show function
    def _show_window(self, window, maximized=False):
        # We only treat non-dialogs (MainWindow, LogandSign, Fillup) as the main window
        if self.current_main_window and self.current_main_window is not window:
            self.current_main_window.hide()

        self.current_main_window = window

        if maximized:
            window.showMaximized()
        else:
            window.show()


    def show_login(self):
        if self.fillup:
            self.fillup.close()
            self.fillup = None
        if self.updatewindow:
            # We close the dialog explicitly if it was open
            self.updatewindow.close()
            self.updatewindow = None

        self._show_window(self.logandsign)