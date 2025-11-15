import sys
from PyQt5 import QtWidgets, QtGui
from app_manager import ApplicationManager
# --- Main Application Entry Point ---


if __name__ == "__main__":
    # Initialize the ApplicationManager (which is a subclass of QApplication)
    app = ApplicationManager(sys.argv)
    app.setWindowIcon(QtGui.QIcon("logo.png"))

    # Start the application flow (this will show the LoginWindow first)
    app.start()

    # Start the main event loop, waiting for user interactions
    sys.exit(app.exec_())