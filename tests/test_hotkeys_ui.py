"""Tests for version, force-close shortcut, mouse/system-button hotkey binding, and tab layout."""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from app.constants import APP_VERSION, DefaultShortcuts
from crosshair.models import ShortcutSettings


def test_version_is_1_2_0():
    assert APP_VERSION == "1.2.0"


def test_shortcut_settings_force_close_default():
    s = ShortcutSettings()
    assert s.force_close == DefaultShortcuts.force_close == "Ctrl+Shift+Q"
    d = s.to_dict()
    assert d["force_close"] == "Ctrl+Shift+Q"


def test_shortcut_settings_backward_compatible():
    # old settings files have no force_close key
    old = {"toggle_overlay": "F8", "toggle_settings": "F9"}
    s = ShortcutSettings.from_dict(old)
    assert s.force_close == "Ctrl+Shift+Q"
    assert s.toggle_overlay == "F8"


def test_parse_keyboard_hotkeys(qapp):
    from winplatform.hotkeys import get_hotkey_manager
    m = get_hotkey_manager()
    key, mods, mouse = m.parse_hotkey_string_ex("Ctrl+Shift+Q")
    assert key == ord("Q") and mouse is None
    assert mods & 0x0002 and mods & 0x0004  # MOD_CONTROL | MOD_SHIFT
    key, mods, mouse = m.parse_hotkey_string_ex("F8")
    assert key == 0x77 and mouse is None


def test_parse_mouse_button_hotkeys(qapp):
    from winplatform.hotkeys import get_hotkey_manager
    m = get_hotkey_manager()
    assert m.parse_hotkey_string_ex("MouseLeft")[2] == "MouseLeft"
    assert m.parse_hotkey_string_ex("Ctrl+MouseRight") == (0, 0x0002, "MouseRight")
    assert m.parse_hotkey_string_ex("Mouse4")[2] == "MouseX1"
    assert m.parse_hotkey_string_ex("Mouse5")[2] == "MouseX2"
    assert m.parse_hotkey_string_ex("Shift+MouseMiddle")[2] == "MouseMiddle"
    assert m.is_mouse_hotkey("MouseLeft")
    assert not m.is_mouse_hotkey("F9")


def test_parse_system_keys(qapp):
    from winplatform.hotkeys import get_hotkey_manager
    m = get_hotkey_manager()
    assert m.parse_hotkey_string_ex("PgUp")[0] == 0x21
    assert m.parse_hotkey_string_ex("PrintScreen")[0] == 0x2C
    assert m.parse_hotkey_string_ex("Left")[0] == 0x25
    assert m.parse_hotkey_string_ex("Num5")[0] == 0x65


@pytest.fixture()
def settings_window(qapp, tmp_path, monkeypatch):
    import storage.settings_store as ss
    monkeypatch.setattr(
        ss.SettingsStore, "_init_settings_path",
        lambda self: setattr(self, "_settings_path", tmp_path / "settings.json"))
    from storage.settings_store import SettingsStore
    from overlay.monitor_manager import MonitorManager
    from ui.settings_window import SettingsWindow
    w = SettingsWindow(MonitorManager(), SettingsStore())
    yield w
    w.close()
    w.deleteLater()


def test_cs2_code_tab_removed(settings_window):
    tabs = [settings_window.tabs.tabText(i) for i in range(settings_window.tabs.count())]
    assert "CS2 Code" not in tabs
    assert "Games" in tabs


def test_force_close_row_exists(settings_window):
    assert settings_window.force_close_edit.text() == "Ctrl+Shift+Q"
    assert hasattr(settings_window, "force_close_requested")


def test_mouse_button_binding_updates_settings(settings_window):
    from PySide6.QtCore import QEvent, Qt, QPointF
    from PySide6.QtGui import QMouseEvent
    w = settings_window
    ev = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(1, 1),
                     Qt.MouseButton.BackButton, Qt.MouseButton.BackButton,
                     Qt.KeyboardModifier.ControlModifier)
    w.eventFilter(w.force_close_edit, ev)
    assert w.force_close_edit.text() == "Ctrl+MouseX1"
    assert w._settings.shortcuts.force_close == "Ctrl+MouseX1"


def test_keyboard_binding_updates_settings(settings_window):
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent
    w = settings_window
    ev = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_F10, Qt.KeyboardModifier.NoModifier)
    w.eventFilter(w.toggle_overlay_edit, ev)
    assert w.toggle_overlay_edit.text() == "F10"
    assert w._settings.shortcuts.toggle_overlay == "F10"


def test_register_hotkeys_includes_force_close(settings_window, monkeypatch):
    calls = []
    monkeypatch.setattr(settings_window.hotkey_manager, "register_hotkey",
                        lambda s, cb, desc="": calls.append((s, desc)) or 1)
    settings_window._register_hotkeys()
    descs = [d for _s, d in calls]
    assert "Force Close" in descs
    assert any(s == "Ctrl+Shift+Q" for s, _d in calls)
