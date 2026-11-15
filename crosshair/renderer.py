"""Crosshair rendering logic shared by preview and overlay."""

from dataclasses import dataclass
from typing import Optional
from PySide6.QtCore import Qt, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PySide6.QtWidgets import QWidget

from crosshair.models import CrosshairSettings
from crosshair.validation import validate_crosshair_settings


@dataclass
class RenderConfig:
    """Configuration for rendering."""
    background: str = "checkerboard"  # "light", "dark", "checkerboard"
    zoom: float = 1.0
    show_center_mark: bool = False


class CrosshairRenderer:
    """Renders crosshair using QPainter. Shared by preview widget and overlay window."""

    def __init__(self, settings: Optional[CrosshairSettings] = None):
        self.settings = settings or CrosshairSettings()
        self._validated_settings, _ = validate_crosshair_settings(self.settings)

    def update_settings(self, settings: CrosshairSettings) -> list[str]:
        """Update settings and return validation warnings."""
        self._validated_settings, warnings = validate_crosshair_settings(settings)
        self.settings = settings
        return warnings

    @property
    def validated_settings(self) -> CrosshairSettings:
        return self._validated_settings

    def paint(self, painter: QPainter, rect: QRectF, config: Optional[RenderConfig] = None):
        """Paint the crosshair into the given rectangle."""
        config = config or RenderConfig()
        s = self._validated_settings

        # Save painter state
        painter.save()

        # Apply zoom
        if config.zoom != 1.0:
            painter.scale(config.zoom, config.zoom)
            # Adjust rect for zoom
            rect = QRectF(rect.x() / config.zoom, rect.y() / config.zoom,
                          rect.width() / config.zoom, rect.height() / config.zoom)

        # Enable antialiasing
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw background
        self._draw_background(painter, rect, config.background)

        # Calculate center
        center_x = rect.center().x()
        center_y = rect.center().y()

        # Parse colors with opacity
        main_color = QColor(s.color)
        main_color.setAlphaF(s.opacity)

        outline_color = QColor(s.outline_color)
        outline_color.setAlphaF(s.opacity)

        # Calculate dimensions (global scale multiplies everything)
        scale = getattr(s, "scale", 1.0) or 1.0
        gap = s.gap * scale
        length = s.length * scale
        thickness = s.thickness * scale
        outline_thickness = (s.outline_thickness if s.outline_enabled else 0) * scale

        # Draw crosshair lines
        self._draw_crosshair_lines(
            painter, center_x, center_y,
            gap, length, thickness, outline_thickness,
            main_color, outline_color, s.t_style
        )

        # Draw center dot
        if s.center_dot:
            self._draw_center_dot(painter, center_x, center_y, s.size * scale, main_color, outline_color, outline_thickness)

        # Draw center mark for preview alignment
        if config.show_center_mark:
            self._draw_center_mark(painter, center_x, center_y)

        painter.restore()

    def _draw_background(self, painter: QPainter, rect: QRectF, background: str):
        """Draw the preview background."""
        if background == "light":
            painter.fillRect(rect, QColor(240, 240, 240))
        elif background == "dark":
            painter.fillRect(rect, QColor(30, 30, 30))
        elif background == "checkerboard":
            self._draw_checkerboard(painter, rect)
        # "none" or any other value: draw nothing (transparent)

    def _draw_checkerboard(self, painter: QPainter, rect: QRectF, square_size: int = 20):
        """Draw a checkerboard pattern for transparency visualization."""
        light = QColor(200, 200, 200)
        dark = QColor(160, 160, 160)

        start_x = int(rect.left())
        start_y = int(rect.top())
        end_x = int(rect.right())
        end_y = int(rect.bottom())

        for y in range(start_y, end_y, square_size):
            for x in range(start_x, end_x, square_size):
                color = light if ((x // square_size) + (y // square_size)) % 2 == 0 else dark
                painter.fillRect(x, y, square_size, square_size, color)

    def _draw_crosshair_lines(self, painter: QPainter, cx: float, cy: float,
                               gap: int, length: int, thickness: int, outline_thickness: int,
                               main_color: QColor, outline_color: QColor, t_style: bool):
        """Draw the four crosshair lines (or three for T-style) - proper cross."""
        half_thickness = thickness / 2.0
        total_outline = outline_thickness * 2

        # Line definitions: (x1, y1, x2, y2) relative to center
        # Horizontal lines have y1=y2=0, Vertical lines have x1=x2=0
        # Left horizontal line
        left_line = (-gap - length, 0, -gap, 0)
        # Right horizontal line
        right_line = (gap, 0, gap + length, 0)
        # Top vertical line
        top_line = (0, -gap - length, 0, -gap)
        # Bottom vertical line
        bottom_line = (0, gap, 0, gap + length)

        lines = [left_line, right_line, top_line, bottom_line]

        if t_style:
            lines = lines[:3]  # Remove bottom line

        # Draw outline first (if enabled) - draw as rectangles for proper thickness
        if outline_thickness > 0:
            pen = QPen(outline_color)
            pen.setWidth(thickness + total_outline)
            pen.setCapStyle(Qt.FlatCap)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            for x1, y1, x2, y2 in lines:
                painter.drawLine(
                    QPointF(cx + x1, cy + y1),
                    QPointF(cx + x2, cy + y2)
                )

        # Draw main lines
        pen = QPen(main_color)
        pen.setWidth(thickness)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)

        for x1, y1, x2, y2 in lines:
            painter.drawLine(
                QPointF(cx + x1, cy + y1),
                QPointF(cx + x2, cy + y2)
            )

    def _draw_center_dot(self, painter: QPainter, cx: float, cy: float,
                          size: int, main_color: QColor, outline_color: QColor, outline_thickness: int):
        """Draw the center dot."""
        radius = size / 2.0

        # Draw outline
        if outline_thickness > 0:
            pen = QPen(outline_color)
            pen.setWidth(outline_thickness * 2)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), radius + outline_thickness, radius + outline_thickness)

        # Draw main dot
        painter.setPen(Qt.NoPen)
        painter.setBrush(main_color)
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

    def _draw_center_mark(self, painter: QPainter, cx: float, cy: float):
        """Draw a subtle center mark for alignment."""
        pen = QPen(QColor(128, 128, 128, 100))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(cx - 10, cy), QPointF(cx + 10, cy))
        painter.drawLine(QPointF(cx, cy - 10), QPointF(cx, cy + 10))


class PreviewWidget(QWidget):
    """Live preview widget for the settings window."""

    def __init__(self, renderer: CrosshairRenderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.config = RenderConfig()
        self.setMinimumSize(200, 200)
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Expanding
        )

    def set_background(self, background: str):
        """Set preview background type."""
        if background in ("light", "dark", "checkerboard"):
            self.config.background = background
            self.update()

    def set_zoom(self, zoom: float):
        """Set preview zoom level."""
        self.config.zoom = max(0.5, min(5.0, zoom))
        self.update()

    def set_show_center_mark(self, show: bool):
        """Show/hide center alignment mark."""
        self.config.show_center_mark = show
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(self.rect())
        self.renderer.paint(painter, rect, self.config)

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(300, 300)