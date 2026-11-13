"""Monitor management for multi-monitor overlay positioning."""

import logging
from dataclasses import dataclass
from typing import Optional, List
from PySide6.QtCore import QObject, QTimer, Signal, QRect, QPoint
from PySide6.QtGui import QGuiApplication, QScreen

logger = logging.getLogger(__name__)


@dataclass
class MonitorInfo:
    """Information about a monitor."""
    id: str
    name: str
    geometry: QRect
    available_geometry: QRect
    device_pixel_ratio: float
    is_primary: bool

    def center(self) -> QPoint:
        """Get center point of the monitor."""
        return self.geometry.center()

    def __str__(self):
        return f"Monitor({self.id}: {self.name}, {self.geometry.width()}x{self.geometry.height()}, primary={self.is_primary})"


class MonitorManager(QObject):
    """Manages monitor detection and selection for overlay positioning."""

    monitors_changed = Signal()
    primary_monitor_changed = Signal(object)  # MonitorInfo

    def __init__(self, parent=None):
        super().__init__(parent)
        self._monitors: List[MonitorInfo] = []
        self._selected_monitor_id: str = "primary"
        self._refresh_timer = QTimer()
        self._refresh_timer.setInterval(2000)  # 2 seconds
        self._refresh_timer.timeout.connect(self._check_monitors)
        self._refresh_timer.start()

        # Initial scan
        self._scan_monitors()

    def _scan_monitors(self):
        """Scan for connected monitors."""
        screens = QGuiApplication.screens()
        new_monitors = []

        for i, screen in enumerate(screens):
            geom = screen.geometry()
            avail = screen.availableGeometry()
            dpr = screen.devicePixelRatio()
            is_primary = screen == QGuiApplication.primaryScreen()

            monitor_id = f"monitor_{i}"
            if is_primary:
                monitor_id = "primary"

            monitor = MonitorInfo(
                id=monitor_id,
                name=screen.name(),
                geometry=geom,
                available_geometry=avail,
                device_pixel_ratio=dpr,
                is_primary=is_primary,
            )
            new_monitors.append(monitor)

        # Check if monitors changed
        if self._monitors_changed(new_monitors):
            self._monitors = new_monitors
            logger.info(f"Monitors updated: {len(self._monitors)} monitor(s)")
            for m in self._monitors:
                logger.debug(f"  {m}")
            self.monitors_changed.emit()

            # Update primary monitor signal
            primary = self.get_primary_monitor()
            if primary:
                self.primary_monitor_changed.emit(primary)

    def _monitors_changed(self, new_monitors: List[MonitorInfo]) -> bool:
        """Check if monitor configuration changed."""
        if len(new_monitors) != len(self._monitors):
            return True
        for new, old in zip(new_monitors, self._monitors):
            if (new.id != old.id or
                new.geometry != old.geometry or
                new.available_geometry != old.available_geometry or
                abs(new.device_pixel_ratio - old.device_pixel_ratio) > 0.01):
                return True
        return False

    def _check_monitors(self):
        """Periodic check for monitor changes."""
        self._scan_monitors()

    def get_monitors(self) -> List[MonitorInfo]:
        """Get list of all monitors."""
        return self._monitors.copy()

    def get_primary_monitor(self) -> Optional[MonitorInfo]:
        """Get the primary monitor."""
        for m in self._monitors:
            if m.is_primary:
                return m
        return self._monitors[0] if self._monitors else None

    def get_monitor_by_id(self, monitor_id: str) -> Optional[MonitorInfo]:
        """Get monitor by ID."""
        if monitor_id == "primary":
            return self.get_primary_monitor()
        for m in self._monitors:
            if m.id == monitor_id:
                return m
        return self.get_primary_monitor()

    def set_selected_monitor(self, monitor_id: str):
        """Set the selected monitor for overlay."""
        monitor = self.get_monitor_by_id(monitor_id)
        if monitor:
            self._selected_monitor_id = monitor_id
            logger.info(f"Selected monitor: {monitor_id} ({monitor.name})")
        else:
            logger.warning(f"Monitor not found: {monitor_id}, using primary")
            self._selected_monitor_id = "primary"

    def get_selected_monitor(self) -> Optional[MonitorInfo]:
        """Get the currently selected monitor."""
        return self.get_monitor_by_id(self._selected_monitor_id)

    def get_selected_monitor_id(self) -> str:
        """Get the selected monitor ID."""
        return self._selected_monitor_id

    def get_overlay_geometry(self, monitor_id: str = None) -> QRect:
        """Get the geometry for overlay positioning on a monitor."""
        monitor = self.get_monitor_by_id(monitor_id or self._selected_monitor_id)
        if monitor:
            return monitor.geometry
        # Fallback to primary screen
        primary = QGuiApplication.primaryScreen()
        if primary:
            return primary.geometry()
        return QRect(0, 0, 1920, 1080)

    def get_center_point(self, monitor_id: str = None) -> QPoint:
        """Get center point for overlay on a monitor."""
        monitor = self.get_monitor_by_id(monitor_id or self._selected_monitor_id)
        if monitor:
            return monitor.center()
        primary = QGuiApplication.primaryScreen()
        if primary:
            return primary.geometry().center()
        return QPoint(960, 540)

    def stop(self):
        """Stop monitor monitoring."""
        self._refresh_timer.stop()