import sys
from pathlib import Path
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QRegion, QPixmap
from PyQt5.QtWidgets import (QLabel, QGraphicsDropShadowEffect, QLineEdit, QPushButton, QComboBox, QGraphicsOpacityEffect)

from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QRegion, QImage, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget  # Needed for QFileDialog context

def get_rounded_stretched_pixmap(blob, width, height):
    """
    Convert an image blob to a rounded (circular) pixmap that stretches to fit the label.

    Args:
        blob (bytes): Image data.
        width (int): Width of the target QLabel.
        height (int): Height of the target QLabel.

    Returns:
        QPixmap: Rounded, stretched pixmap.
    """
    if not blob:
        return None

    # Convert blob to QPixmap
    image = QImage.fromData(blob)
    pixmap = QPixmap.fromImage(image)

    # Stretch the pixmap to fit the label
    pixmap = pixmap.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    # Make a rounded mask
    size = min(width, height)
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(pixmap))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    painter.end()

    return rounded

class setup_profile(QLabel):

    def __init__(self, target_label: QLabel, default_path: str):

        self.label = target_label
        self.default_path = default_path
        self._current_path = self.default_path

        self._set_profile_photo_internal(self.default_path)

        self.setup_click_handler()

    def setup_click_handler(self):
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.mousePressEvent = lambda event: self.change_profile_photo()

    def change_profile_photo(self):

        print("DEBUG: Profile change method triggered.")

        try:
            parent_widget = self.label.parentWidget()

            file_dialog = QFileDialog(parent_widget)
            file_path, _ = file_dialog.getOpenFileName(
                parent_widget,
                "Select New Profile Picture",
                "",
                "Image Files (*.png *.jpg *.jpeg *.webp)"
            )
            if file_path:
                self._set_profile_photo_internal(file_path)
                self._current_path = file_path
        except Exception as e:
            print(f"ERROR: Failed to open file dialog or load image: {e}")

    @property
    def current_path(self):
        return self._current_path

    def _set_profile_photo_internal(self, image_path: str):

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print("Error: Invalid image or file path.")
            return

        size = self.label.width()
        label_size = self.label.size()
        radius = size // 2

        if size == 0:
            size = self.label.geometry().width()
            label_size = self.label.geometry().size()
            radius = size // 2

            if size == 0:
                print("Warning: Profile photo size is zero. Make sure it's sized correctly in Qt Designer.")
                return

        scaled_pixmap = pixmap.scaled(label_size,
                                      Qt.KeepAspectRatioByExpanding,
                                      Qt.SmoothTransformation)

        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        self.label.setStyleSheet(f"""
            QLabel#{self.label.objectName()} {{
                border-radius: {radius}px;
                border: 3px solid transparent; 
                background-color: transparent;
            }}
        """)

        self.label.setMask(QRegion(0, 0, size, size, QRegion.Ellipse))

class setupComboBox:
    def __init__(self, combobox: QComboBox, item_list: list, placeholder: str):
        self.combobox = combobox
        self.placeholder_text = placeholder
        self.combobox.clear()
        self.combobox.addItem(self.placeholder_text)
        self.combobox.addItems(item_list)
        self.combobox.setCurrentIndex(0)

    def get_selected_value(self) -> str:
        if self.combobox.currentIndex() == 0:
            return None
        return self.combobox.currentText()

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

class DesignShadow:
    def __init__(self, widget, blur=50, offset=(0, 20), color=QColor(0, 0, 0, 180)):
        # QGraphicsDropShadowEffect requires the parent or widget for context
        shadow = QGraphicsDropShadowEffect(widget)

        # Set the permanent shadow properties
        shadow.setBlurRadius(blur)
        shadow.setOffset(*offset)
        shadow.setColor(color)

        # Apply the permanent effect
        widget.setGraphicsEffect(shadow)

class HoverShadow(QObject):
    def __init__(self, lineedit: QLineEdit, blur=25, offset_x=0, offset_y=0, color=QColor(0, 0, 0, 160)):
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

def opac(self, label, opacity_value):
    opacity_effect = QGraphicsOpacityEffect()
    opacity_effect.setOpacity(opacity_value)
    label.setGraphicsEffect(opacity_effect)