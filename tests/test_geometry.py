"""Tests for geometry and monitor handling."""

import pytest
from PySide6.QtCore import QRect, QPoint
from overlay.monitor_manager import MonitorManager, MonitorInfo


def test_monitor_center():
    """Test monitor center calculation."""
    monitor = MonitorInfo(
        id="test",
        name="Test Monitor",
        geometry=QRect(0, 0, 1920, 1080),
        available_geometry=QRect(0, 0, 1920, 1040),
        device_pixel_ratio=1.0,
        is_primary=True
    )
    center = monitor.center()
    # QRect.center() returns (x + (width-1)/2, y + (height-1)/2) for 0-indexed coordinates
    assert center == QPoint(959, 539)


def test_monitor_center_with_offset():
    """Test monitor center with offset (multi-monitor)."""
    monitor = MonitorInfo(
        id="test",
        name="Test Monitor",
        geometry=QRect(1920, 0, 1920, 1080),
        available_geometry=QRect(1920, 0, 1920, 1040),
        device_pixel_ratio=1.0,
        is_primary=False
    )
    center = monitor.center()
    assert center == QPoint(2879, 539)


def test_rect_center():
    """Test QRect center."""
    rect = QRect(100, 100, 200, 200)
    center = rect.center()
    assert center == QPoint(199, 199)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
