import sys
from pathlib import Path
from functools import partial
from PyQt5 import QtWidgets, uic,QtCore
from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtGui import QFont, QFontDatabase, QColor, QRegion, QPixmap
from PyQt5.QtWidgets import (QLabel, QGraphicsDropShadowEffect, QLineEdit, QPushButton, QComboBox, QGraphicsOpacityEffect)
from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QRegion, QImage, QPainter, QBrush
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QVBoxLayout
from app.assets import res_rc

def add_chart_to_dashboard(container_widget, chart_widget, start_animation=True, delay=100):
    """
    Reusable utility to add a chart (or any widget) to a dashboard container.

    Args:
        container_widget (QWidget): The parent widget that holds the layout (e.g., self.dashboard1).
        chart_widget (QWidget): The chart widget to add (e.g., DonutChartWidget).
        start_animation (bool): Whether to start the chart's animation automatically (if it has one).
        delay (int): Delay in milliseconds before starting animation.
    """
    # Ensure the container has a layout
    if not container_widget.layout():
        container_widget.setLayout(QVBoxLayout())

    layout = container_widget.layout()

    # Clear existing widgets
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

    # Add the new chart
    layout.addWidget(chart_widget)

    # Optionally start animation
    if start_animation and hasattr(chart_widget, "start_animation"):
        QTimer.singleShot(delay, chart_widget.start_animation)

def display_scholarships_admin(scroll_area, database):
    scroll_content = scroll_area.widget()
    scroll_layout = scroll_content.layout()

    if scroll_layout is None:
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)

    scroll_layout.setSpacing(15)
    scroll_layout.setContentsMargins(0, 20, 0, 20)
    scroll_layout.setAlignment(QtCore.Qt.AlignTop)

    # Clear previous items
    while scroll_layout.count():
        item = scroll_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

    scholarships = database.get_user_info_for_admin()

    # Filter pending scholarships
    pending_scholarships = [rec for rec in scholarships if rec[11] not in ("ACCEPTED", "REJECTED")]

    # Stylesheet
    qss = """
        QScrollArea {
            background: transparent;
            border: none;
        }

        QScrollArea > QWidget {
            background: transparent;
            border: none;
        }
    
        QFrame#scholarship_card {
            background-color: rgba(255, 255, 255, 220);
            border-radius: 15px;
            border: 1px solid rgba(200,200,200,0.5);
        }
        QLabel#scholarship_name {
            font-weight: 700;
            font-size: 16px;
            color: #1f3a5f;
        }
        QLabel#id_label {
            font-size: 14px;
            color: #555;
        }
        QLabel#name_label {
            font-weight: 600;
            font-size: 18px;
            color: #334e68;
        }
        QLabel#detail_label {
            font-weight: 500;
            font-size: 14px;
            color: #586c87;
        }
        QLabel#status_label {
            font-weight: 700;
            font-size: 16px;
            color: white;
            border-radius: 10px;
            padding: 8px 12px;
            min-width: 100px;
            text-align: center;
        }
        QPushButton#accept_btn {
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 8px 16px;
        }
        QPushButton#accept_btn:hover { background-color: #388E3C; }
        QPushButton#reject_btn {
            background-color: #FF5252;
            color: white;
            font-weight: 600;
            border-radius: 10px;
            padding: 8px 16px;
        }
        QPushButton#reject_btn:hover { background-color: #D32F2F; }
    """
    scroll_area.setStyleSheet(qss)

    def add_empty_message():
        lbl = QtWidgets.QLabel("No pending scholarship applications found.")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setStyleSheet("font-size: 18px; color: #555;")
        scroll_layout.addWidget(lbl)

    if pending_scholarships:
        for record in pending_scholarships:
            (scholar_id, username, first_name, last_name, middle_name, email,
             municipality, college, program, year_level, scholar_name,
             status, gwa, suffix) = record

            # Card container
            container = QtWidgets.QFrame()
            container.setObjectName("scholarship_card")
            container.setFixedHeight(220)
            container.setFixedWidth(900)

            # Apply shadow
            DesignShadow(container, 25, (0,0), QColor(0,0,0,80))

            # Main layout
            main_layout = QtWidgets.QHBoxLayout(container)
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(30)

            # Left Info
            info_layout = QtWidgets.QVBoxLayout()
            info_layout.setSpacing(5)
            info_layout.setAlignment(QtCore.Qt.AlignTop)

            # Title + ID
            title_layout = QtWidgets.QHBoxLayout()
            scholarship_label = QtWidgets.QLabel(f"{scholar_name}")
            scholarship_label.setObjectName("scholarship_name")
            id_label = QtWidgets.QLabel(f"(ID: {scholar_id})")
            id_label.setObjectName("id_label")
            title_layout.addWidget(scholarship_label)
            title_layout.addWidget(id_label)
            title_layout.addStretch()
            info_layout.addLayout(title_layout)

            # Full Name
            full_name = f"{first_name} {middle_name} {last_name} {suffix}".strip()
            name_label = QtWidgets.QLabel(full_name)
            name_label.setObjectName("name_label")
            info_layout.addWidget(name_label)

            # Details grid
            details_grid = QtWidgets.QGridLayout()
            details_grid.setSpacing(3)
            details_data = [
                ("Municipality:", municipality),
                ("College:", college),
                ("Program:", program),
                ("Year Level:", year_level),
                ("GWA:", gwa)
            ]
            for i, (key, value) in enumerate(details_data):
                key_lbl = QtWidgets.QLabel(key)
                key_lbl.setStyleSheet("font-weight: 600; font-size: 14px;")
                value_lbl = QtWidgets.QLabel(str(value))
                value_lbl.setObjectName("detail_label")
                details_grid.addWidget(key_lbl, i, 0)
                details_grid.addWidget(value_lbl, i, 1)
            info_layout.addLayout(details_grid)
            info_layout.addStretch()
            main_layout.addLayout(info_layout, 2)

            # Right layout (status + buttons)
            right_layout = QtWidgets.QVBoxLayout()
            right_layout.setSpacing(10)
            right_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

            status_label = QtWidgets.QLabel(status.upper())
            status_label.setObjectName("status_label")
            status_label.setAlignment(QtCore.Qt.AlignCenter)
            status_color = "#2196F3"
            status_label.setStyleSheet(f"QLabel#status_label {{ background-color: {status_color}; }}")

            # Action buttons
            action_layout = QtWidgets.QHBoxLayout()
            action_layout.setSpacing(8)
            accept_btn = QtWidgets.QPushButton("Accept")
            accept_btn.setObjectName("accept_btn")
            reject_btn = QtWidgets.QPushButton("Reject")
            reject_btn.setObjectName("reject_btn")
            action_layout.addWidget(status_label, 1)
            action_layout.addWidget(accept_btn, 1)
            action_layout.addWidget(reject_btn, 1)

            right_layout.addLayout(action_layout)
            right_layout.addStretch()
            main_layout.addLayout(right_layout, 3)

            # Handler function
            def make_handler(scholar_id, container, new_status):
                def handler():
                    database.update_scholarship_status(scholar_id, new_status)
                    container.setParent(None)
                    container.deleteLater()
                    scroll_content.adjustSize()
                    scroll_area.ensureVisible(0, 0)
                    scroll_area.repaint()

                    if scroll_layout.count() == 0:
                        add_empty_message()
                return handler

            accept_btn.clicked.connect(make_handler(scholar_id, container, "ACCEPTED"))
            reject_btn.clicked.connect(make_handler(scholar_id, container, "REJECTED"))

            # Center card
            centering_layout = QtWidgets.QHBoxLayout()
            centering_layout.addStretch()
            centering_layout.addWidget(container)
            centering_layout.addStretch()
            scroll_layout.addLayout(centering_layout)

    else:
        add_empty_message()

    scroll_content.adjustSize()
    scroll_area.ensureVisible(0, 0)
    scroll_area.repaint()

def display_scholarships_util(username, scroll_area, database):

    scroll_content = scroll_area.widget()
    scroll_layout = scroll_content.layout()

    if scroll_layout is None:
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_content.setLayout(scroll_layout)

    # Force top alignment
    scroll_layout.setAlignment(QtCore.Qt.AlignTop)

    # Clear previous items
    while scroll_layout.count():
        item = scroll_layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()

    scholarships = database.get_user_scholar_status(username)

    if scholarships:
        for scholarname, status in scholarships:
            # Container card
            container = QtWidgets.QFrame()
            container.setObjectName("container")
            container.setFixedHeight(150)

            container.setStyleSheet("""
                #container {
                    background: white;
                    border: 1.5px solid #74c69d;
                    padding: 10px;
                }

                QLabel#name_label {
                    color: black;
                    font-weight: 600;
                    font-size: 16px;
                    padding-left: 10px;
                }
                
                QLabel#info_label {
                    color: black;
                    font-weight: 400;
                    font-size: 12px;
                    padding-left: 10px;
                }

                QLabel#status_label {
                    background-color: #5bc26a;
                    color: white;
                    font-weight: 700;
                    font-size: 14px;
                    border-radius: 20px;
                    padding: 8px 20px;
                    max-width: 150px;
                    max-height: 50px;
                    text-align: center;
                }
            """)

            layout = QtWidgets.QHBoxLayout(container)
            layout.setContentsMargins(20, 20, 20, 20)

            vlayout = QtWidgets.QVBoxLayout()
            vlayout.setContentsMargins(0, 0, 0, 0)

            logo = QLabel("")
            logo.setMaximumSize(100, 100)
            logo.setScaledContents(True)

            if scholarname == "BSU FINANCIAL ASSISTANCE":
                logo.setPixmap(QPixmap(":/images/bsutrans.png"))
            elif scholarname == "BCD SCHOLARSHIP":
                logo.setPixmap(QPixmap(":/images/altlogo.png"))
            elif scholarname == "DSWD EDUCATIONAL ASSISTANCE":
                logo.setPixmap(QPixmap(":/images/educ.png"))

            name_label = QLabel(scholarname)
            name_label.setObjectName("name_label")

            info_label = QLabel("Amount - Php. 7,000.00\nDeadline - 23/11/26")
            info_label.setObjectName("info_label")

            status_label = QLabel(status)
            status_label.setObjectName("status_label")
            status_label.setAlignment(QtCore.Qt.AlignCenter)

            status_color = (
                "#2196f3" if status == "PENDING"
                else "#4caf50" if status == "ACCEPTED"
                else "#f44336"
            )

            status_label.setStyleSheet(
                f"background-color: {status_color}; color: white; border-radius: 20px; padding: 6px 15px;"
            )

            vlayout.addWidget(name_label)
            vlayout.addWidget(info_label)

            layout.addWidget(logo)
            layout.addLayout(vlayout)
            layout.addWidget(status_label)

            scroll_layout.addWidget(container)


    else:
        lbl = QLabel("No scholarship available.")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        scroll_layout.addWidget(lbl)

    # Force layout refresh
    scroll_content.adjustSize()
    scroll_area.ensureVisible(0, 0)
    scroll_area.repaint()

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
    def __init__(self, target_label: QLabel, default_path: str, parent=None):
        # ✔ Correct super() — pass parent properly
        super().__init__(target_label.parent())

        self.label = target_label
        self.default_path = default_path
        self._current_path = self.default_path

        # Apply the default image safely
        self._set_profile_photo_internal(self.default_path)

        # Enable clicking
        self.setup_click_handler()

    def setup_click_handler(self):
        """Make the QLabel clickable."""
        self.label.setCursor(Qt.PointingHandCursor)

        def click_handler(event):
            self.change_profile_photo()

        self.label.mousePressEvent = click_handler

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

        # ✔ REAL FIX: Handle label-size=0 BEFORE applying mask or scaling
        if size == 0:
            size = self.label.geometry().width()
            label_size = self.label.geometry().size()

        if size == 0:
            print("Warning: Profile photo size is zero. Make sure it's sized correctly in Qt Designer.")
            return

        radius = size // 2

        # ✔ FIX: Prevent weird stretching — always expand then crop
        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        self.label.setStyleSheet(f"""
            QLabel#{self.label.objectName()} {{
                border-radius: {radius}px;
                border: 3px solid transparent;
                background-color: transparent;
            }}
        """)

        self.label.setMask(
            QRegion(0, 0, label_size.width(), label_size.height(), QRegion.Ellipse)
        )

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