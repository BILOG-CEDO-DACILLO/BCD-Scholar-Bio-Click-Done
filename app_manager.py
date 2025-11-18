from PyQt5.QtWidgets import QApplication

from app.gui.login_window import LogandSign
from app.gui.Fillup import FillupWindow


class ApplicationManager(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        self.logandsign = LogandSign()
        self.fillup = FillupWindow()

        self.logandsign.app_manager = self
        self.fillup.app_manager = self

        self.current_main_window = None

    def start(self):
        self._show_main_window(self.logandsign)

    def _show_main_window(self, new_window):
        if self.current_main_window:
            self.current_main_window.hide()
        self.current_main_window = new_window
        new_window.show()

    def show_fillup(self):
        self._show_main_window(self.fillup)

    def show_login(self):
        self._show_main_window(self.logandsign)
