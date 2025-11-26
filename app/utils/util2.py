# safe_admin_lists.py
from functools import partial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QMessageBox

# ---------- SAFE DESIGN SHADOW (optional) ----------
def DesignShadow(widget, blur_radius=12, offset=(0,0), color=QColor(0,0,0,120)):
    # If you suspect the shadow causes issues, comment out body temporarily.
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur_radius)
    shadow.setOffset(*offset)
    shadow.setColor(color)
    widget.setGraphicsEffect(shadow)

# ---------- UTIL ----------

def init_scroll_area(scroll_area: QtWidgets.QScrollArea) -> QtWidgets.QVBoxLayout:
    """
    Ensure the scroll area has a widget and a QVBoxLayout; return that layout.
    """
    if scroll_area.widget() is None:
        scroll_area.setWidget(QtWidgets.QWidget())
        scroll_area.widget().setObjectName("admin_scroll_widget")
        scroll_area.setWidgetResizable(True)
    content = scroll_area.widget()
    if content.layout() is None:
        content.setLayout(QtWidgets.QVBoxLayout())
    layout = content.layout()
    layout.setSpacing(15)
    layout.setContentsMargins(0, 20, 0, 20)
    layout.setAlignment(QtCore.Qt.AlignTop)
    return layout

def safe_remove_widget(widget: QtWidgets.QWidget):
    """
    Remove widget from its parent/layout safely and schedule deletion.
    """
    if widget is None:
        return
    widget.setParent(None)  # removes immediately from layout
    # schedule actual deletion after control returns to event loop
    QtCore.QTimer.singleShot(0, widget.deleteLater)

def clear_scroll_layout(scroll_layout: QtWidgets.QLayout):
    """
    Remove only widget items from layout (ignore nested layouts).
    """
    # iterate reversed so indices remain valid
    for i in reversed(range(scroll_layout.count())):
        item = scroll_layout.itemAt(i)
        w = item.widget()
        if w:
            safe_remove_widget(w)
        else:
            # if item is a layout (rare in our usage), try to clear it recursively then delete
            inner = item.layout()
            if inner:
                clear_scroll_layout(inner)
                # no direct delete of layouts necessary; they are owned by parent.

def add_empty_message(scroll_layout: QtWidgets.QLayout, text: str):
    lbl = QtWidgets.QLabel(text)
    lbl.setAlignment(QtCore.Qt.AlignCenter)
    lbl.setStyleSheet("font-size:18px; color:#555; padding:18px;")
    scroll_layout.addWidget(lbl, alignment=QtCore.Qt.AlignHCenter)

# ---------- DATA VALIDATION ----------

def validate_record_for_display(rec):
    """
    Ensure record has exactly 14 fields in expected order:
    (id, username, first_name, last_name, middle_name, email,
     municipality, college, program, year_level, scholarship_name, status, gwa, suffix)
    """
    if not rec:
        return False, "Empty record"
    if not isinstance(rec, (list, tuple)):
        return False, f"Record is not tuple/list: {type(rec)}"
    if len(rec) != 14:
        return False, f"Expected 14 fields but got {len(rec)}"
    return True, None

# ---------- CARD CREATION ----------

def create_card_widget(record, scroll_layout, database, status_type="ACCEPTED"):
    ok, err = validate_record_for_display(record)
    if not ok:
        add_empty_message(scroll_layout, f"Invalid record: {err}")
        return None

    # safe unpack (we already validated length)
    (scholar_id, username, first_name, last_name, middle_name, email,
     municipality, college, program, year_level, scholar_name,
     status, gwa, suffix) = record

    card = QtWidgets.QFrame()
    card.setObjectName("scholarship_card")
    card.setFixedHeight(300)
    card.setFixedWidth(900)

    card.setStyleSheet("""
        QFrame#scholarship_card {
            background-color: white;
            border-radius: 18px;
            border: 1px solid rgba(0,0,0,0.08);
        }
    """)

    try:
        DesignShadow(card, 18, (0, 0), QColor(0, 0, 0, 90))
    except Exception:
        pass

    # layout & contents
    main_layout = QtWidgets.QHBoxLayout(card)
    main_layout.setContentsMargins(18, 18, 18, 18)
    main_layout.setSpacing(18)

    # LEFT: text info
    info_layout = QtWidgets.QVBoxLayout()
    info_layout.setAlignment(QtCore.Qt.AlignTop)

    # Title row
    title_row = QtWidgets.QHBoxLayout()
    lbl_scholar = QtWidgets.QLabel(str(scholar_name))
    lbl_scholar.setFont(QFont("Segoe UI", 14, QFont.Bold))
    lbl_id = QtWidgets.QLabel(f"(ID: {scholar_id})")
    lbl_id.setFont(QFont("Segoe UI", 10))
    title_row.addWidget(lbl_scholar)
    title_row.addWidget(lbl_id)
    title_row.addStretch()
    info_layout.addLayout(title_row)

    # Full name
    full_name = f"{first_name} {middle_name or ''} {last_name} {suffix or ''}".strip()
    lbl_full = QtWidgets.QLabel(full_name)
    lbl_full.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
    info_layout.addWidget(lbl_full)

    # grid details
    grid = QtWidgets.QGridLayout()
    details = [
        ("Municipality:", municipality),
        ("College:", college),
        ("Program:", program),
        ("Year Level:", year_level),
        ("GWA:", gwa)
    ]
    for i, (k, v) in enumerate(details):
        k_lbl = QtWidgets.QLabel(k)
        k_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        v_lbl = QtWidgets.QLabel(str(v) if v is not None else "")
        v_lbl.setFont(QFont("Segoe UI", 10))
        grid.addWidget(k_lbl, i, 0)
        grid.addWidget(v_lbl, i, 1)
    info_layout.addLayout(grid)

    main_layout.addLayout(info_layout, 2)

    # RIGHT: status + optional buttons
    right_layout = QtWidgets.QVBoxLayout()
    right_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
    status_lbl = QtWidgets.QLabel(status_type.upper())
    status_lbl.setAlignment(QtCore.Qt.AlignCenter)
    status_lbl.setFixedWidth(150)
    status_lbl.setFixedHeight(100)
    # assign color per status
    if status_type == "ACCEPTED":
        bg = "#4CAF50"
    elif status_type == "REJECTED":
        bg = "#FF5252"
    else:
        bg = "#795548"
    status_lbl.setStyleSheet(f"background:{bg}; color:white; padding:6px; border-radius:8px;")
    right_layout.addWidget(status_lbl)

    # Drop button only for accepted
    if status_type == "ACCEPTED":
        drop_btn = QtWidgets.QPushButton("Drop")
        drop_btn.setCursor(QtCore.Qt.PointingHandCursor)
        drop_btn.setFixedWidth(150)
        drop_btn.setFixedHeight(100)
        drop_btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                padding: 6px 14px;
                border-radius: 6px;
                border: none;
            }

            QPushButton:hover {
                background-color: #B71C1C;
            }

            QPushButton:pressed {
                background-color: #9A0007;
                padding-top: 8px;   /* animation: button sinks */
                padding-bottom: 4px;
            }
        """)

        # connect using partial with safe handler
        drop_btn.clicked.connect(partial(safe_drop_handler, database, scholar_id, card, scroll_layout))
        right_layout.addWidget(drop_btn)

    right_layout.addStretch()
    main_layout.addLayout(right_layout, 3)

    # finally add card into layout centered horizontally
    scroll_layout.addWidget(card, alignment=QtCore.Qt.AlignHCenter)
    return card

# ---------- DROP HANDLER ----------

def safe_drop_handler(database, scholar_id, card_widget, scroll_layout):
    """
    Called when admin clicks 'Drop' on an accepted scholar.
    This safely updates DB and removes card from UI.
    """
    try:
        ok = database.update_scholarship_status(scholar_id, "DROPPED")
        if not ok:
            QMessageBox.critical(None, "Error", "Failed to update database status.")
            return
    except Exception as e:
        QMessageBox.critical(None, "Error", f"DB error: {e}")
        return

    # remove from UI safely
    safe_remove_widget(card_widget)

    # if layout is empty after removal, show empty message
    # schedule a tiny delay so layout bookkeeping finishes
    def maybe_add_empty():
        if scroll_layout.count() == 0:
            add_empty_message(scroll_layout, "No accepted scholarship applications found.")
    QtCore.QTimer.singleShot(10, maybe_add_empty)

# ---------- DISPLAY FUNCTIONS (public) ----------

def display_accepted_scholarships_admin(scroll_area, database):
    layout = init_scroll_area(scroll_area)
    clear_scroll_layout(layout)

    try:
        scholarships = database.get_user_info_for_admin()
    except Exception as e:
        add_empty_message(layout, f"DB Error: {e}")
        return

    accepted = []
    try:
        accepted = [r for r in scholarships if len(r) >= 12 and r[11] and str(r[11]).upper() == "ACCEPTED"]
    except Exception as e:
        add_empty_message(layout, f"Data parse error: {e}")
        return

    if not accepted:
        add_empty_message(layout, "No accepted scholarship applications found.")
        return

    for rec in accepted:
        create_card_widget(rec, layout, database, "ACCEPTED")


def display_rejected_scholarships_admin(scroll_area, database):
    layout = init_scroll_area(scroll_area)
    clear_scroll_layout(layout)

    try:
        scholarships = database.get_user_info_for_admin()
    except Exception as e:
        add_empty_message(layout, f"DB Error: {e}")
        return

    rejected = []
    try:
        rejected = [r for r in scholarships if len(r) >= 12 and r[11] and str(r[11]).upper() == "REJECTED"]
    except Exception as e:
        add_empty_message(layout, f"Data parse error: {e}")
        return

    if not rejected:
        add_empty_message(layout, "No rejected scholarship applications found.")
        return

    for rec in rejected:
        create_card_widget(rec, layout, database, "REJECTED")


def display_dropped_scholarships_admin(scroll_area, database):
    layout = init_scroll_area(scroll_area)
    clear_scroll_layout(layout)

    try:
        scholarships = database.get_user_info_for_admin()
    except Exception as e:
        add_empty_message(layout, f"DB Error: {e}")
        return

    dropped = []
    try:
        dropped = [r for r in scholarships if len(r) >= 12 and r[11] and str(r[11]).upper() == "DROPPED"]
    except Exception as e:
        add_empty_message(layout, f"Data parse error: {e}")
        return

    if not dropped:
        add_empty_message(layout, "No dropped scholarship applications found.")
        return

    for rec in dropped:
        create_card_widget(rec, layout, database, "DROPPED")
