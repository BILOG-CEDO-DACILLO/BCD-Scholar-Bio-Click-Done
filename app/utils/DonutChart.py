import traceback
from math import cos, sin, radians, atan2
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QParallelAnimationGroup,
    QObject, pyqtProperty as Property, QRectF, QEasingCurve
)
from app.utils.util import DesignShadow

class AnimatedSlice(QObject):
    def __init__(self, value, color, label, target_angle, start_angle, parent=None):
        super().__init__(parent)
        self.value = value
        self.color = color
        self.label = label
        self.target_angle = target_angle
        self.start_angle_offset = start_angle
        self._current_span_angle = 0.0

    def get_current_span_angle(self):
        return self._current_span_angle

    def set_current_span_angle(self, angle):
        self._current_span_angle = angle
        if self.parent():
            self.parent().update()

    current_span_angle = Property(float, get_current_span_angle, set_current_span_angle)


class DonutChartWidget(QWidget):
    def __init__(self, data: dict, title="", colors=None, parent=None):
        super().__init__(parent)
        self._data_raw = data
        self.title = title
        self.colors = colors

        # Fonts
        self.title_font = QFont("Poppins", 10, QFont.Bold)
        self.label_font = QFont("Poppins", 8, QFont.Bold)
        self.donut_thickness_ratio = 0.20

        # Animations
        self.slices = []
        self.animation_group = QParallelAnimationGroup(self)
        self.animation_duration = 1300

        # Hover
        self.hovered_slice = None
        self.setMouseTracking(True)

        self._prepare_slices()
        self.setMinimumSize(320, 260)

    # ---------- Slice preparation ----------
    def _get_default_colors(self):
        if self.colors:
            return [QColor(c) for c in self.colors]
        return [
            QColor("#2ECC71"),  # Emerald Green
            QColor("#E74C3C"),  # Alizarin Red
            QColor("#3498DB"),  # Peter River Blue
            QColor("#F1C40F"),  # Sun Flower Yellow
            QColor("#9B59B6"),  # Amethyst Purple
            QColor("#1ABC9C"),  # Turquoise
            QColor("#E67E22"),  # Carrot Orange
            QColor("#34495E"),  # Wet Asphalt Dark Blue
        ]

    def _prepare_slices(self):
        total = sum(self._data_raw.values())
        if total <= 0:
            return

        self.slices.clear()
        colors = self._get_default_colors()
        angle_offset = 90 * 16
        color_i = 0

        for label, value in self._data_raw.items():
            pct = value / total
            span = round(pct * 5760)

            sl_color = colors[color_i % len(colors)]
            color_i += 1

            sl = AnimatedSlice(value, sl_color, label, span, angle_offset, parent=self)
            self.slices.append(sl)

            anim = QPropertyAnimation(sl, b"current_span_angle")
            anim.setDuration(self.animation_duration)
            anim.setStartValue(0.0)
            anim.setEndValue(float(span))
            anim.setEasingCurve(QEasingCurve.OutCubic)
            self.animation_group.addAnimation(anim)

            angle_offset += span

    # ---------- Animation ----------
    def start_animation(self):
        try:
            self.animation_group.start()
        except Exception:
            traceback.print_exc()

    # ---------- Hover (Logic remains the same to detect hover) ----------
    def mouseMoveEvent(self, event):
        pos = event.pos()
        W, H = self.width(), self.height()

        # Recalculate size to match paintEvent logic
        available_chart_height = H - 40  # Reserve 40px for legend
        chart_size = min(W, available_chart_height) * 0.75
        donut_thickness = chart_size * self.donut_thickness_ratio
        chart_rect = QRectF(
            (W - chart_size) / 2,
            (available_chart_height - chart_size) / 2 - 10,  # Shifted up slightly
            chart_size,
            chart_size
        )
        radius = chart_size / 2
        chart_center = chart_rect.center()

        dx = pos.x() - chart_center.x()
        dy = chart_center.y() - pos.y()  # Y positive UP for atan2

        dist = (dx ** 2 + dy ** 2) ** 0.5

        self.hovered_slice = None

        # 1. Check if mouse is inside donut ring
        # Use radius and donut_thickness derived from chart_size
        if radius - donut_thickness / 2 <= dist <= radius + donut_thickness / 2:

            # Standard Cartesian angle (0 deg at 3 o'clock, CCW)
            angle_rad = atan2(dy, dx)
            angle_deg = (angle_rad * 180 / 3.14159265 + 360) % 360

            # Convert to 0 deg at top (12 o'clock), CCW (The scale used by the slice accumulation logic)
            final_hover_deg = (angle_deg - 90 + 360) % 360

            # 2. Track the cumulative angle and check against slices
            cumulative_deg = 0.0
            gap_deg = 6 / 16.0

            for sl in self.slices:
                span_deg_full = sl.current_span_angle / 16.0

                hover_start_deg = cumulative_deg
                hover_end_deg = cumulative_deg + span_deg_full - gap_deg  # Exclude gap

                if hover_start_deg < hover_end_deg:
                    if hover_start_deg <= final_hover_deg < hover_end_deg:
                        self.hovered_slice = sl
                        break
                else:  # Slice crosses 360/0
                    if final_hover_deg >= hover_start_deg or final_hover_deg < hover_end_deg:
                        self.hovered_slice = sl
                        break

                cumulative_deg += span_deg_full

        self.update()

    # ---------- Painting ----------
    def paintEvent(self, event):
        try:
            self._safe_paint(event)
        except Exception:
            traceback.print_exc()

    def _safe_paint(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        W, H = self.width(), self.height()
        if W < 50 or H < 50:
            return

        # 1. Draw Title (RE-ADDED)
        painter.setFont(self.title_font)
        painter.setPen(QColor("#333"))
        painter.drawText(0, 0, W, 40, Qt.AlignCenter | Qt.AlignVCenter, self.title)

        # 2. Calculate Chart Geometry
        # Reserve about 40px at the bottom for the legend
        available_chart_height = H - 40
        chart_size = min(W, available_chart_height) * 0.75  # Size of the bounding box for the arc
        donut_thickness = chart_size * self.donut_thickness_ratio

        # Center the chart horizontally, and shift it up slightly vertically
        # Note: Chart positioning is slightly adjusted here to account for the top margin used by the title
        chart_rect = QRectF(
            (W - chart_size) / 2,
            (40 + available_chart_height - chart_size) / 2 - 10, # Start Y adjusted for top 40px used by title
            chart_size,
            chart_size
        )
        radius = chart_size / 2
        center_x, center_y = chart_rect.center().x(), chart_rect.center().y()

        # 3. Draw slices with hover effect
        angle = 90 * 16
        gap = 100  # Gap in 1/16th of a degree
        for sl in self.slices:
            try:
                # Actual span drawn
                span = max(0, round(sl.current_span_angle - gap))

                # Hover offset logic
                offset_distance = 10 if sl == self.hovered_slice else 0
                mid_angle_deg = angle / 16 + sl.current_span_angle / 32
                rad = radians(mid_angle_deg)
                offset_x = offset_distance * cos(rad)
                offset_y = -offset_distance * sin(rad)

                pen_width = donut_thickness * 1.3 if sl == self.hovered_slice else donut_thickness
                pen_color = sl.color.lighter(150) if sl == self.hovered_slice else sl.color
                pen = QPen(pen_color, pen_width, Qt.SolidLine, Qt.FlatCap)
                painter.setPen(pen)

                # Adjusted rectangle for pop-out
                shifted_rect = QRectF(
                    chart_rect.left() + offset_x,
                    chart_rect.top() + offset_y,
                    chart_rect.width(),
                    chart_rect.height()
                )
                painter.drawArc(shifted_rect, angle, span)
                angle += round(sl.current_span_angle)
            except Exception:
                traceback.print_exc()

        # 4. Draw Legend (Horizontal, centered at the bottom)
        total_value = max(1, sum(self._data_raw.values()))

        painter.setFont(self.label_font)
        metrics = painter.fontMetrics()
        legend_spacing = 20  # Spacing between items
        swatch_size = 10

        legend_items = []
        total_legend_width = -legend_spacing  # Start with negative spacing to cancel out last item's spacing

        # Pre-calculate item properties
        for sl in self.slices:
            slice_pct = sl.value / total_value
            txt = f"{sl.label} ({slice_pct:.1%})"
            text_width = metrics.horizontalAdvance(txt)

            # Swatch (10) + padding (8) + text + gap (20)
            item_width = swatch_size + 8 + text_width + legend_spacing
            legend_items.append({'slice': sl, 'text': txt, 'width': item_width})
            total_legend_width += item_width

        # Draw the legend centered at the bottom
        current_x = (W - total_legend_width) / 2
        legend_y = H - 15

        for item in legend_items:
            sl = item['slice']
            txt = item['text']
            item_width = item['width']

            # 4a. Draw Color Swatch
            painter.setPen(Qt.NoPen)
            painter.setBrush(sl.color)
            # Center the swatch vertically around legend_y
            swatch_rect = QRectF(current_x, legend_y - swatch_size / 2, swatch_size, swatch_size)
            painter.drawEllipse(swatch_rect)

            # 4b. Draw Text
            painter.setPen(QColor("#333")) # Use a dark color for text
            text_x = current_x + swatch_size + 8
            # Align the text baseline with the center of the swatch/legend_y
            text_y_center = legend_y
            text_y_baseline = text_y_center + metrics.ascent() / 2

            painter.drawText(int(text_x), int(text_y_baseline), txt)

            current_x += item_width


# Utility factory
def create_donut_chart_widget(data: dict, title="", colors=None, parent=None):
    w = DonutChartWidget(data, title=title, colors=colors, parent=parent)
    w.start_animation()
    DesignShadow(w, blur=50, offset=(0, 0), color=QColor(0, 0, 0, 180))
    return w