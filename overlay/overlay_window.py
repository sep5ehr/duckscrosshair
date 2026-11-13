"""Transparent overlay window for crosshair display."""

import logging
from typing import Optional
from PySide6.QtCore import Qt, QRect, QPoint, QTimer, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QScreen, QGuiApplication
from PySide6.QtWidgets import QWidget

from crosshair.models import CrosshairSettings, OverlaySettings
from crosshair.renderer import CrosshairRenderer, RenderConfig
from overlay.monitor_manager import MonitorManager

logger = logging.getLogger(__name__)


class OverlayWindow(QWidget):
    """Transparent, click-through, always-on-top overlay window."""

    # Signal emitted when geometry changes (e.g., monitor change)
    geometry_changed = Signal(QRect)

    def __init__(self, monitor_manager: MonitorManager, parent=None):
        # Overlay window should be a top-level window, not a child of the application
        # Pass None as parent to QWidget, use window flags as second argument
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
                         | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.WindowTransparentForInput
                         | Qt.WindowType.WindowDoesNotAcceptFocus)

        self.monitor_manager = monitor_manager
        self.settings = OverlaySettings()
        self.crosshair_settings = CrosshairSettings()
        self.renderer = CrosshairRenderer(self.crosshair_settings)

        # Window setup - use Qt's native transparency (no Windows API layering)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setMouseTracking(False)

        # Connect monitor changes
        self.monitor_manager.monitors_changed.connect(self._on_monitors_changed)
        self.monitor_manager.primary_monitor_changed.connect(self._on_primary_monitor_changed)

        # Initial setup
        self._update_position()
        self.hide()  # Start hidden, will be shown when enabled

    def update_settings(self, overlay_settings: OverlaySettings, crosshair_settings: CrosshairSettings):
        """Update overlay and crosshair settings."""
        self.settings = overlay_settings
        self.crosshair_settings = crosshair_settings

        # Update renderer
        self.renderer.update_settings(crosshair_settings)

        # Update window flags
        self._update_window_flags()

        # Update position
        self._update_position()

        # Trigger repaint
        self.update()

    def _update_window_flags(self):
        """Update window flags based on settings."""
        flags = Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint

        if self.settings.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint

        if self.settings.click_through:
            flags |= Qt.WindowType.WindowTransparentForInput

        flags |= Qt.WindowType.WindowDoesNotAcceptFocus

        self.setWindowFlags(flags)

    def _update_position(self):
        """Update overlay position to center of selected monitor."""
        monitor = self.monitor_manager.get_selected_monitor()
        if monitor:
            geom = monitor.geometry
            self.setGeometry(geom)
            self.geometry_changed.emit(geom)
            logger.debug(f"Overlay positioned on monitor {monitor.id}: {geom}")

    def _on_monitors_changed(self):
        """Handle monitor configuration change."""
        logger.info("Monitor configuration changed, updating overlay position")
        self._update_position()

    def _on_primary_monitor_changed(self, monitor):
        """Handle primary monitor change."""
        if self.settings.monitor_id == "primary":
            self._update_position()

    def set_enabled(self, enabled: bool):
        """Enable or disable the overlay."""
        if enabled and not self.isVisible():
            self.show()
            logger.info("Overlay enabled")
        elif not enabled and self.isVisible():
            self.hide()
            logger.info("Overlay disabled")

    def set_monitor(self, monitor_id: str):
        """Change the monitor the overlay is displayed on."""
        self.settings.monitor_id = monitor_id
        self._update_position()

    def paintEvent(self, event):
        """Paint the crosshair."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Render config for overlay (no background, no zoom)
        config = RenderConfig(background="none", zoom=1.0, show_center_mark=False)

        # Paint using shared renderer
        rect = QRect(0, 0, self.width(), self.height())
        self.renderer.paint(painter, rect, config)

    def sizeHint(self) -> QSize:
        """Default size hint."""
        return QSize(1920, 1080)

    def closeEvent(self, event):
        """Clean up on close."""
        super().closeEvent(event)