import traceback
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QRectF, QRect


class SingleSeriesBarChartWidget(QWidget):
    """
    An animated bar chart widget designed to visualize a single series of data
    (e.g., counts per college).

    Each bar is assigned a distinct color from a defined palette.
    """

    def __init__(self, data: dict, title="Bar Chart", parent=None):
        super().__init__(parent)
        self.data = data
        self.title = title
        self.margin = 40
        self.bar_group_width_ratio = 0.6

        # --- Color Palette (New) ---
        self.color_palette = [
            QColor("#2ECC71"),  # Emerald Green
            QColor("#E74C3C"),  # Alizarin Red
            QColor("#3498DB"),  # Peter River Blue
            QColor("#F1C40F"),  # Sun Flower Yellow
            QColor("#9B59B6"),  # Amethyst Purple
            QColor("#1ABC9C"),  # Turquoise
            QColor("#E67E22"),  # Carrot Orange
            QColor("#34495E"),  # Wet Asphalt Dark Blue
        ]

        # General appearance
        self.bg_color = QColor(240, 240, 240)
        self.chart_bg_radius = 20
        self.bar_radius = 5
        self.hover_color_diff = 30  # How much to darken the color on hover

        self.font = QFont("Poppins", 9)
        self.title_font = QFont("Poppins", 11, QFont.Bold)

        self.setMinimumSize(500, 350)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Animation
        self._current_height_scale = 0.0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_step = 0.05
        self.start_animation()

        # Hover
        self._hovered_bar_index = -1

    # --- Animation ---
    def start_animation(self):
        self._current_height_scale = 0.0
        self.animation_timer.start(45)

    def update_animation(self):
        if self._current_height_scale < 1.0:
            self._current_height_scale += self.animation_step
            if self._current_height_scale >= 1.0:
                self._current_height_scale = 1.0
                self.animation_timer.stop()
            self.update()

    # --- Hover color ---
    # Calculates a darker version of the input color
    def _get_hover_color(self, color):
        r, g, b, a = color.getRgb()
        return QColor(max(0, r - self.hover_color_diff),
                      max(0, g - self.hover_color_diff),
                      max(0, b - self.hover_color_diff),
                      a)

    # --- Painting ---
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
            W, H = self.width(), self.height()

            # Title
            painter.setFont(self.title_font)
            painter.setPen(QColor("#333"))
            painter.drawText(0, 10, W, self.margin, Qt.AlignCenter, self.title)

            categories = list(self.data.keys())
            n_bars = len(categories)
            if n_bars == 0:
                return

            chart_top = self.margin + 40
            chart_bottom = H - self.margin
            chart_left = self.margin
            chart_right = W - self.margin
            chart_height = chart_bottom - chart_top
            chart_width = chart_right - chart_left

            # Calculate max value for scaling
            max_value = max(self.data.values()) or 1
            max_value_buffered = max_value * 1.1

            bar_group_unit = chart_width / n_bars
            bar_width = bar_group_unit * self.bar_group_width_ratio
            bar_height_unit = chart_height / max_value_buffered
            y0 = chart_bottom

            # Y-Axis grid lines & labels
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.setFont(self.font)
            y_label_count = 5
            step = max(1, int(max_value / y_label_count))
            for i in range(0, max_value + step, step):
                y = y0 - i * bar_height_unit
                painter.drawLine(chart_left, int(y), chart_right, int(y))
                painter.setPen(QColor("#555"))
                painter.drawText(0, int(y) - 7, self.margin - 10, 15,
                                 Qt.AlignRight | Qt.AlignVCenter, str(i))
                painter.setPen(QPen(QColor(200, 200, 200), 1))

            # Draw bars
            painter.setPen(Qt.NoPen)
            for i, (college, value) in enumerate(self.data.items()):
                # Calculate x position for the single bar, centered in its unit
                x_group_center = chart_left + i * bar_group_unit + bar_group_unit / 2
                x0 = x_group_center - bar_width / 2

                # Bar dimensions
                bar_height = value * bar_height_unit * self._current_height_scale
                is_hovered = self._hovered_bar_index == i

                # --- Use unique color for each bar, cycling through the palette ---
                bar_color = self.color_palette[i % len(self.color_palette)]

                # Draw Bar
                painter.setBrush(
                    self._get_hover_color(bar_color) if is_hovered else bar_color
                )
                self._draw_rounded_bar(painter, x0, y0, bar_width, bar_height, is_hovered)

                # Draw tooltip only when animation is done and hovered
                if is_hovered and self._current_height_scale == 1.0:
                    self._draw_tooltip_safe(painter, x0, y0 - bar_height, bar_width, value)

                # X-Axis labels (Centered under the single bar)
                painter.setPen(QColor("#555"))
                painter.drawText(int(x0), y0 + 15, int(bar_width), 20, Qt.AlignCenter, college)
        except Exception as e:
            traceback.print_exc()

    # Rounded bar (Helper is correct)
    def _draw_rounded_bar(self, painter, x, y0, w, h, is_hovered):
        if h <= 0: return
        path = QPainterPath()
        rect = QRectF(x, y0 - h, w, h)
        r = self.bar_radius

        # Draw path for rounded top and sharp bottom
        path.moveTo(rect.bottomLeft())
        path.lineTo(rect.left(), rect.top() + r)
        path.arcTo(rect.left(), rect.top(), 2 * r, 2 * r, 180, -90)
        path.lineTo(rect.right() - r, rect.top())
        path.arcTo(rect.right() - 2 * r, rect.top(), 2 * r, 2 * r, 90, -90)
        path.lineTo(rect.bottomRight())
        path.closeSubpath()

        painter.setPen(QPen(QColor(0, 0, 0, 50), 1) if is_hovered else Qt.NoPen)
        painter.drawPath(path)

    # Tooltip with error handling (Kept original logic for drawing tooltip)
    def _draw_tooltip_safe(self, painter, x, y, w, value):
        try:
            tooltip_w, tooltip_h = 50, 25

            # Calculate coordinates (results in floats)
            tx = x + w / 2 - tooltip_w / 2
            ty = y - tooltip_h - 5

            # Constrain coordinates
            tx = max(5.0, min(tx, self.width() - tooltip_w - 5.0))
            ty = max(5.0, ty)

            # Convert all drawing coordinates to integers
            tx_int = int(tx)
            ty_int = int(ty)
            w_int = int(tooltip_w)
            h_int = int(tooltip_h)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 200))

            painter.drawRoundedRect(tx_int, ty_int, w_int, h_int, 5, 5)

            painter.setPen(Qt.white)
            painter.setFont(self.font)
            painter.drawText(tx_int, ty_int, w_int, h_int, Qt.AlignCenter, str(value))

        except Exception:
            traceback.print_exc()

    # Mouse geometry helper (Helper is correct)
    def _get_bar_rect(self, x, y0, w, h):
        return QRect(int(x), int(y0 - h), int(w), int(h))

    # --- Mouse hover ---
    def mouseMoveEvent(self, event):
        if self._current_height_scale < 1.0:
            return

        try:
            pos = event.pos()
            categories = list(self.data.keys())
            n_bars = len(categories)
            chart_top = self.margin + 40
            chart_bottom = self.height() - self.margin
            chart_left = self.margin
            chart_right = self.width() - self.margin
            chart_height = chart_bottom - chart_top
            chart_width = chart_right - chart_left

            max_value = max(self.data.values()) or 1
            max_value_buffered = max_value * 1.1
            bar_group_unit = chart_width / n_bars
            bar_width = bar_group_unit * self.bar_group_width_ratio
            bar_height_unit = chart_height / max_value_buffered
            y0 = chart_bottom

            new_index = -1
            for i, (college, value) in enumerate(self.data.items()):
                x_group_center = chart_left + i * bar_group_unit + bar_group_unit / 2
                x0 = x_group_center - bar_width / 2

                bar_full_height = value * bar_height_unit
                bar_rect = self._get_bar_rect(x0, y0, bar_width, bar_full_height)

                if bar_rect.contains(pos):
                    new_index = i
                    break

            if new_index != self._hovered_bar_index:
                self._hovered_bar_index = new_index
                self.update()
        except Exception:
            traceback.print_exc()

    def leaveEvent(self, event):
        self._hovered_bar_index = -1
        self.update()


# Utility function to create the widget
def create_bar_chart_widget2(data: dict, title="Bar Chart", parent=None):
    return SingleSeriesBarChartWidget(data, title, parent)