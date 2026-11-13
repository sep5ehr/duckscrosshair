"""System tray icon for the application."""

import logging
from pathlib import Path
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QStyle

logger = logging.getLogger(__name__)


def create_crosshair_icon(size: int = 32, color: str = "#00FF00", outline_color: str = "#000000") -> QIcon:
    """Create a simple crosshair icon for the tray (fallback)."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    center = size // 2
    gap = max(2, size // 10)
    length = max(4, size // 5)
    thickness = max(1, size // 16)

    # Outline
    pen = QPen(QColor(outline_color))
    pen.setWidth(thickness + 2)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(pen)

    painter.drawLine(center - gap - length, center, center - gap, center)  # Left
    painter.drawLine(center + gap, center, center + gap + length, center)  # Right
    painter.drawLine(center, center - gap - length, center, center - gap)  # Top
    painter.drawLine(center, center + gap, center, center + gap + length)  # Bottom

    # Main
    pen = QPen(QColor(color))
    pen.setWidth(thickness)
    pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(pen)

    painter.drawLine(center - gap - length, center, center - gap, center)
    painter.drawLine(center + gap, center, center + gap + length, center)
    painter.drawLine(center, center - gap - length, center, center - gap)
    painter.drawLine(center, center + gap, center, center + gap + length)

    painter.end()
    return QIcon(pixmap)


def load_app_icon() -> QIcon:
    """Load the application icon from resources."""
    # Try to load the ICO file first (best for Windows)
    icons_dir = Path(__file__).parent.parent.parent / "resources" / "icons"
    ico_path = icons_dir / "duck_icon.ico"
    png_path = icons_dir / "duck_icon.png"

    if ico_path.exists():
        return QIcon(str(ico_path))
    elif png_path.exists():
        return QIcon(str(png_path))
    else:
        # Fallback to generated icon
        return create_crosshair_icon()


class TrayIcon(QSystemTrayIcon):
    """System tray icon with menu."""

    # Signals
    show_settings = Signal()
    toggle_overlay = Signal()
    quit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay_enabled = True

        # Create icon from resource files
        self._icon = load_app_icon()
        self.setIcon(self._icon)
        self.setToolTip("DucksCrosshair")

        # Create menu
        self._menu = QMenu()
        self._create_menu()
        self.setContextMenu(self._menu)

        # Connect signals
        self.activated.connect(self._on_activated)

    def _create_menu(self):
        """Create the tray context menu."""
        # Show settings
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.show_settings.emit)
        self._menu.addAction(self.settings_action)

        # Toggle overlay
        self.toggle_action = QAction("Disable Overlay", self)
        self.toggle_action.triggered.connect(self.toggle_overlay.emit)
        self._menu.addAction(self.toggle_action)

        self._menu.addSeparator()

        # Quit
        self.quit_action = QAction("Exit", self)
        self.quit_action.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(self.quit_action)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - show settings
            self.show_settings.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - toggle overlay
            self.toggle_overlay.emit()

    def set_overlay_enabled(self, enabled: bool):
        """Update overlay state in menu."""
        self._overlay_enabled = enabled
        if enabled:
            self.toggle_action.setText("Disable Overlay")
        else:
            self.toggle_action.setText("Enable Overlay")

    def update_icon(self, color: str = "#00FF00", outline_color: str = "#000000"):
        """Update tray icon with new colors."""
        self._icon = create_crosshair_icon(32, color, outline_color)
        self.setIcon(self._icon)