"""Backward-compatibility tests: the pre-existing app codec and settings keep working."""

from crosshair.sharecode import encode_share_code, decode_share_code  # old module, untouched
from crosshair.core import detect_crosshair_format
from crosshair.models import AppSettings
from crosshair.core.app_model import app_to_universal, universal_to_app


def test_old_custom_codec_still_round_trips():
    model = {"style": 4, "gap": 2, "length": 6.0, "thickness": 2.0, "size": 6.0,
             "outline_enabled": True, "outline_thickness": 1, "center_dot": True,
             "color": "#FF0000"}
    enc = encode_share_code(model)
    assert enc.success
    dec = decode_share_code(enc.share_code)
    assert dec.success
    assert dec.internal_model["color"] == "#FF0000"


def test_detect_app_legacy_code():
    model = {"style": 4, "gap": 3, "length": 7.0, "thickness": 2.0, "size": 5.0,
             "outline_enabled": True, "outline_thickness": 1, "center_dot": False,
             "color": "#00FF00"}
    enc = encode_share_code(model)
    assert enc.success
    d = detect_crosshair_format(enc.share_code)
    assert d.valid
    assert d.game == "cs2"
    assert d.format == "app-legacy-v1"
    assert any("old internal" in w for w in d.warnings)


def test_old_settings_file_still_loads():
    old = {"schema_version": 1,
           "crosshair": {"gap": 9, "length": 11, "color": "#123456"},
           "overlay": {"enabled": True},
           "shortcuts": {"toggle_overlay": "F8"},
           "last_share_code": "CSGO-ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"}
    s = AppSettings.from_dict(old)
    assert s.crosshair.gap == 9
    assert s.crosshair.color == "#123456"
    assert s.selected_game == "cs2"          # new fields defaulted
    assert s.last_codes == {}
    # re-serialization keeps old keys and adds new ones without breaking old readers
    d = s.to_dict()
    assert d["crosshair"]["gap"] == 9
    assert d["schema_version"] == 1


def test_app_model_bridge_round_trip():
    from crosshair.models import CrosshairSettings
    s = CrosshairSettings(gap=4, length=9, thickness=2, color="#AABBCC",
                          center_dot=True, style=2)
    u = app_to_universal(s, "cs2")
    s2 = universal_to_app(u)
    assert s2.gap == 4 and s2.length == 9 and s2.color == "#AABBCC"
    assert s2.center_dot is True and s2.style == 2
