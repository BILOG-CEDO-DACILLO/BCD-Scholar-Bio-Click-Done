from PyQt5.QtWidgets import QApplication

# Import the window classes
from app.gui.login_window import LogandSign
from app.utils.util import MyWindow


# --- 5. Application Manager (Handles Window Switching) ---
class ApplicationManager(QApplication):
    """
    Manages the lifecycle and switching between QMainWindow and QDialog screens.
    """
    def __init__(self, argv):
        super().__init__(argv)
        # Initialize all windows, passing a reference to the manager
        self.logandsign = LogandSign()


        # Keep track of the currently active main window
        self.current_main_window = None

    def start(self):
        """Starts the application by showing the login screen."""
        self.logandsign.show()

