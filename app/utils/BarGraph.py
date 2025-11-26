import traceback
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QRectF, QRect


class AnimatedBarChartWidget(QWidget):

    BASE_COLORS = [
        QColor("#2ECC71"),
        QColor("#E74C3C"),
        QColor("#3498DB"),
        QColor("#F1C40F"),
        QColor("#9B59B6"),
        QColor("#1ABC9C"),
        QColor("#E67E22"),
        QColor("#34495E"),
    ]

    def __init__(self, data, title="Bar Chart", colors=None, parent=None):
        super().__init__(parent)

        self.data = data
        self.title = title
        self.custom_colors = colors  # ← NEW
        self.margin = 40
        self.bar_group_width_ratio = 0.8

        self.bg_color = QColor(240, 240, 240)
        self.bar_radius = 5
        self.hover_color_diff = 30

        self.font = QFont("Poppins", 9)
        self.title_font = QFont("Poppins", 11, QFont.Bold)
        self.legend_font = QFont("Poppins", 8)

        self.setMinimumSize(500, 350)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Dynamic data processing
        self.bar_types, self.colors, self.max_value = self._process_data(data)
        self.n_types = len(self.bar_types)

        # Animation
        self._current_height_scale = 0.0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_step = 0.05
        self.start_animation()

        self._hovered_bar_index = -1
        self._hovered_bar_type = None

    def _process_data(self, data):
        unique_types = set()
        max_val = 1

        for town_data in data.values():
            for bar_type, value in town_data.items():
                unique_types.add(bar_type)
                if value > max_val:
                    max_val = value

        bar_types = sorted(list(unique_types))

        # NEW: Allow custom colors
        palette = (
            [QColor(c) for c in self.custom_colors]
            if self.custom_colors else
            self.BASE_COLORS
        )

        colors = {}
        for i, bar_type in enumerate(bar_types):
            colors[bar_type] = palette[i % len(palette)]

        return bar_types, colors, max_val

    # ---------------- Animation ----------------

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

    # ---------------- Hover color ----------------

    def _get_hover_color(self, color):
        r, g, b, a = color.getRgb()
        return QColor(
            max(0, r - self.hover_color_diff),
            max(0, g - self.hover_color_diff),
            max(0, b - self.hover_color_diff),
            a
        )

    # ---------------- Painting ----------------

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
            W, H = self.width(), self.height()

            # Title
            painter.setFont(self.title_font)
            painter.setPen(QColor("#333"))
            painter.drawText(0, 10, W, self.margin, Qt.AlignCenter, self.title)

            municipalities = list(self.data.keys())
            n_groups = len(municipalities)

            if n_groups == 0 or self.n_types == 0:
                return

            # Geometry
            chart_top = self.margin + 40
            chart_bottom = H - self.margin
            chart_left = self.margin
            chart_right = W - self.margin
            chart_height = chart_bottom - chart_top
            chart_width = chart_right - chart_left

            max_value = self.max_value
            bar_group_unit = chart_width / n_groups
            bar_width = (bar_group_unit * self.bar_group_width_ratio) / self.n_types
            bar_height_unit = chart_height / max_value
            y0 = chart_bottom

            # Y grid
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.setFont(self.font)
            y_label_count = 5
            step = max(1, max_value // y_label_count)

            for i in range(0, max_value + step, step):
                y = y0 - i * bar_height_unit
                painter.drawLine(chart_left, int(y), chart_right, int(y))
                painter.setPen(QColor("#555"))
                painter.drawText(
                    0, int(y) - 7, self.margin - 10, 15,
                    Qt.AlignRight | Qt.AlignVCenter, str(i)
                )
                painter.setPen(QPen(QColor(200, 200, 200), 1))

            # Legend
            legend_x = chart_left
            legend_y = self.margin + 5
            current_x = legend_x

            painter.setFont(self.legend_font)
            metrics = painter.fontMetrics()

            for bar_type in self.bar_types:
                text_display = bar_type.replace("_", " ").title()
                text_width = metrics.horizontalAdvance(text_display)
                required_width = 10 + 5 + text_width + 15

                if current_x + required_width > chart_right:
                    break

                self._draw_legend_item(
                    painter, current_x, legend_y,
                    text_display, required_width, self.colors[bar_type]
                )

                current_x += required_width

            # Bars
            painter.setPen(Qt.NoPen)

            for i, town in enumerate(municipalities):
                x_group_center = chart_left + i * bar_group_unit + bar_group_unit / 2
                x_start = x_group_center - (bar_width * self.n_types) / 2

                for j, bar_type in enumerate(self.bar_types):
                    bar_val = self.data[town].get(bar_type, 0)
                    bar_h = bar_val * bar_height_unit * self._current_height_scale
                    x_bar = x_start + j * bar_width

                    hovered = (
                        self._hovered_bar_index == i and
                        self._hovered_bar_type == bar_type
                    )

                    color = (
                        self._get_hover_color(self.colors[bar_type])
                        if hovered else self.colors[bar_type]
                    )

                    painter.setBrush(color)
                    self._draw_rounded_bar(painter, x_bar, y0, bar_width, bar_h, hovered)

                    if hovered and self._current_height_scale == 1.0:
                        self._draw_tooltip_safe(
                            painter,
                            x_bar,
                            y0 - bar_h,
                            bar_width,
                            bar_val
                        )

                painter.setPen(QColor("#555"))
                painter.drawText(
                    int(x_start), y0 + 15,
                    int(bar_width * self.n_types), 20,
                    Qt.AlignCenter, town
                )

        except Exception as e:
            print("PaintEvent error:", e)
            traceback.print_exc()

    # ---------------- Legend ----------------

    def _draw_legend_item(self, painter, x, y, text, width, color):
        try:
            size = 10
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(x, y, size, size)
            painter.setPen(QColor("#333"))
            painter.setFont(self.legend_font)
            painter.drawText(x + size + 5, y, width - size - 5, size,
                             Qt.AlignLeft | Qt.AlignVCenter, text)
        except:
            pass

    # ---------------- Bars ----------------

    def _draw_rounded_bar(self, painter, x, y0, w, h, hovered):
        if h <= 0:
            return

        path = QPainterPath()
        rect = QRectF(x, y0 - h, w, h)
        r = self.bar_radius

        path.moveTo(rect.bottomLeft())
        path.arcTo(rect.left(), rect.top(), 2 * r, 2 * r, 180, -90)
        path.lineTo(rect.right() - r, rect.top())
        path.arcTo(rect.right() - 2 * r, rect.top(), 2 * r, 2 * r, 90, -90)
        path.lineTo(rect.bottomRight())
        path.closeSubpath()

        painter.setPen(QPen(QColor(0, 0, 0, 50), 1) if hovered else Qt.NoPen)
        painter.drawPath(path)

    # ---------------- Tooltip ----------------

    def _draw_tooltip_safe(self, painter, x, y, w, value):
        try:
            tooltip_w, tooltip_h = 50, 25

            tx = x + w / 2 - tooltip_w / 2
            ty = y - tooltip_h - 5

            tx = max(5.0, min(tx, self.width() - tooltip_w - 5.0))
            ty = max(5.0, ty)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 200))
            painter.drawRoundedRect(int(tx), int(ty), tooltip_w, tooltip_h, 5, 5)

            painter.setPen(Qt.white)
            painter.setFont(self.font)
            painter.drawText(
                int(tx), int(ty), tooltip_w, tooltip_h,
                Qt.AlignCenter, str(value)
            )
        except:
            pass

    # ---------------- Hover Events ----------------

    def _get_bar_rect(self, x, y0, w, h):
        return QRect(int(x), int(y0 - h), int(w), int(h))

    def mouseMoveEvent(self, event):
        if self._current_height_scale < 1.0 or self.n_types == 0:
            return

        try:
            pos = event.pos()
            municipalities = list(self.data.keys())
            n_groups = len(municipalities)

            chart_top = self.margin + 40
            chart_bottom = self.height() - self.margin
            chart_left = self.margin
            chart_right = self.width() - self.margin
            chart_height = chart_bottom - chart_top
            chart_width = chart_right - chart_left

            max_value = self.max_value
            bar_group_unit = chart_width / n_groups
            bar_width = (bar_group_unit * self.bar_group_width_ratio) / self.n_types
            bar_height_unit = chart_height / max_value
            y0 = chart_bottom

            new_index, new_type = -1, None

            for i, town in enumerate(municipalities):
                x_center = chart_left + i * bar_group_unit + bar_group_unit / 2
                x_start = x_center - (bar_width * self.n_types) / 2

                for j, bar_type in enumerate(self.bar_types):
                    bar_val = self.data[town].get(bar_type, 0)
                    bar_h = bar_val * bar_height_unit
                    x_bar = x_start + j * bar_width

                    rect = self._get_bar_rect(x_bar, y0, bar_width, bar_h)

                    if rect.contains(pos):
                        new_index, new_type = i, bar_type
                        break

                if new_index != -1:
                    break

            if (new_index, new_type) != (self._hovered_bar_index, self._hovered_bar_type):
                self._hovered_bar_index = new_index
                self._hovered_bar_type = new_type
                self.update()

        except Exception as e:
            print("Hover error:", e)
            traceback.print_exc()

    def leaveEvent(self, event):
        self._hovered_bar_index = -1
        self._hovered_bar_type = None
        self.update()


# ---------------- Utility ----------------

def create_bar_chart_widget(data, title="Bar Chart", colors=None, parent=None):
    return AnimatedBarChartWidget(data, title, colors, parent)

