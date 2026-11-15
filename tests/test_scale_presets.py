"""Tests for crosshair scale, saved presets, and preview background sync."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from crosshair.models import CrosshairSettings, AppSettings
from crosshair.validation import validate_crosshair_settings
from crosshair.core.app_model import app_to_universal, universal_to_app


# ---------------- scale ----------------

def test_scale_default_and_backward_compat():
    s = CrosshairSettings()
    assert s.scale == 1.0
    old = CrosshairSettings.from_dict({"gap": 3})  # no scale key in old files
    assert old.scale == 1.0
    assert CrosshairSettings.from_dict({"scale": 3.0}).scale == 3.0


def test_scale_validated_and_clamped():
    s, warnings = validate_crosshair_settings(CrosshairSettings(scale=99.0))
    assert s.scale == 10.0
    assert any("scale" in w for w in warnings)
    s, _ = validate_crosshair_settings(CrosshairSettings(scale=0.01))
    assert s.scale == 0.1


def test_scale_serialization_round_trip():
    s = CrosshairSettings(scale=2.5, gap=4)
    s2 = CrosshairSettings.from_dict(s.to_dict())
    assert s2.scale == 2.5 and s2.gap == 4


def test_scale_carried_through_universal():
    s = CrosshairSettings(scale=1.75)
    u = app_to_universal(s, "cs2")
    assert u.scale == 1.75
    s2 = universal_to_app(u)
    assert s2.scale == 1.75


def test_app_crosshair_encodes_to_game_codes():
    # the app's own crosshair can be turned into a share code for any game
    from crosshair.core import encode_universal, detect_crosshair_format
    s = CrosshairSettings(gap=3, length=8, thickness=2, color="#FF0000", scale=1.5)
    u = app_to_universal(s, "cs2")
    r = encode_universal(u, "cs2")
    assert r.success and r.code.startswith("CS")
    d = detect_crosshair_format(r.code)
    assert d.valid and d.settings["red"] == 255 and d.settings["gap"] == 3
    r = encode_universal(u, "valorant")
    assert r.success and r.code.startswith("0;")
    d = detect_crosshair_format(r.code)
    assert d.valid and d.game == "valorant"


# ---------------- presets / settings ----------------

def test_saved_crosshairs_backward_compatible():
    a = AppSettings.from_dict({"schema_version": 1, "crosshair": {"gap": 1}})
    assert a.saved_crosshairs == []
    assert a.preview_background == "checkerboard"
    a.saved_crosshairs.append({"name": "x", "settings": CrosshairSettings().to_dict()})
    a2 = AppSettings.from_dict(a.to_dict())
    assert a2.saved_crosshairs[0]["name"] == "x"


# ---------------- UI ----------------

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


def test_scale_control_in_crosshair_tab(settings_window):
    cc = settings_window.crosshair_controls
    assert cc.scale_control.value() == 1.0
    cc.scale_control.set_value(2.5)
    assert cc.get_settings().scale == 2.5


def test_preset_save_load_delete(settings_window):
    w = settings_window
    gw = w.games_widget
    gw.preset_name_edit.setText("TestPreset")
    gw._on_save_preset()
    assert [p["name"] for p in w._settings.saved_crosshairs] == ["TestPreset"]
    assert gw.presets_list.count() == 1
    # modify current, then load preset back
    w.crosshair_controls.gap_control.set_value(9)
    gw.presets_list.setCurrentRow(0)
    gw._on_load_preset()
    assert w._settings.crosshair.gap == 2  # preset had default gap
    # delete
    gw.presets_list.setCurrentRow(0)
    gw._on_delete_preset()
    assert w._settings.saved_crosshairs == []


def test_preview_background_syncs_all_sidebars(settings_window):
    w = settings_window
    w.preview_controls.bg_combo.setCurrentText("Dark")
    assert w.preview_widget.config.background == "dark"
    assert w.games_preview.config.background == "dark"
    assert w.shortcuts_preview.config.background == "dark"
    assert w._settings.preview_background == "dark"
    w.preview_controls.bg_combo.setCurrentText("Light")
    assert w.games_preview.config.background == "light"
