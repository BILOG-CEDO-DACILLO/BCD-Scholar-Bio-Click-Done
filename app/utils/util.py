import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QLineEdit, QPushButton


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # Frameless window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._drag_pos = None

        self.container = QtWidgets.QWidget(self)
        self.container.setGeometry(0, 30, 1200, 650)  # size of your window
        self.container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 255);
            border-radius: 20px;
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

class HoverShadow(QObject):
    def __init__(self, lineedit: QLineEdit, blur=15, offset_x=0, offset_y=0, color=QColor(0, 0, 0, 160)):
        super().__init__(lineedit)
        self.lineedit = lineedit

        self.target_blur = blur
        self.target_offset_x = offset_x
        self.target_offset_y = offset_y
        self.target_color = color

        self.shadow = QGraphicsDropShadowEffect()

        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 0))

        self.lineedit.setGraphicsEffect(self.shadow)

        self.lineedit.setAttribute(Qt.WA_Hover, True)
        self.lineedit.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.lineedit:
            try:
                if event.type() == QEvent.Enter:
                    self.shadow.setBlurRadius(self.target_blur)
                    self.shadow.setOffset(self.target_offset_x, self.target_offset_y)
                    self.shadow.setColor(self.target_color)

                elif event.type() == QEvent.Leave:
                    self.shadow.setBlurRadius(0)
                    self.shadow.setOffset(0, 0)
                    self.shadow.setColor(QColor(0, 0, 0, 0))

            except Exception as e:
                print(f"HoverShadow error during state change: {e}")

        return False

def load_font(font_path, size=12, bold=False):
    font_path = Path(font_path).resolve()
    if not font_path.exists():
        print(f"⚠️ Font not found: {font_path}")
        return QFont()

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    families = QFontDatabase.applicationFontFamilies(font_id)
    if not families:
        return QFont()

    font = QFont(families[0], size)
    if bold:
        font.setWeight(QFont.Weight.Bold)
    else:
        font.setWeight(QFont.Weight.Normal)
    return font
