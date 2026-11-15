"""Tests for automatic format detection and cross-game conversion."""

import pytest

from crosshair.core import detect_crosshair_format, convert_crosshair, decode_to_universal
from tests.fixtures import (
    CS2_LEGACY_V1, CS2_V1, VALORANT_CODES, DEADLOCK_CODES,
)


def test_detect_cs2_legacy():
    d = detect_crosshair_format(CS2_LEGACY_V1[0][0])
    assert d.valid and d.game == "cs2" and d.format == "legacy-v1"
    assert d.settings


def test_detect_cs2_native():
    d = detect_crosshair_format(CS2_V1[0][0])
    assert d.valid and d.game == "cs2" and d.format == "cs2-v1"


def test_detect_valorant():
    d = detect_crosshair_format(VALORANT_CODES[0])
    assert d.valid and d.game == "valorant" and d.format == "valorant-native"


def test_detect_deadlock():
    d = detect_crosshair_format(DEADLOCK_CODES[0])
    assert d.valid and d.game == "deadlock" and d.format == "deadlock-reticle"


@pytest.mark.parametrize("code", [
    "", "garbage", "CSGO-12345-12345-12345-12345-12345",
    "CSkSCHQKunGr2yPsJr2U3RTd8ycMA2pEs9jWnxK5KjMmWL",  # bad checksum
    "0;s", "DL.!!!", "1;s;1",
])
def test_detect_invalid(code):
    d = detect_crosshair_format(code)
    assert not d.valid
    assert d.error


def test_version_number_alone_does_not_determine_format():
    # legacy-v1 and cs2-v1 both store version byte 1 but are different formats
    assert detect_crosshair_format(CS2_LEGACY_V1[0][0]).format == "legacy-v1"
    assert detect_crosshair_format(CS2_V1[0][0]).format == "cs2-v1"


def test_convert_cs2_to_valorant():
    r = convert_crosshair(CS2_V1[0][0], "valorant")
    assert r.success, r.error
    assert r.code.startswith("0;")
    # converted code must decode back
    from crosshair.core import detect_crosshair_format
    d = detect_crosshair_format(r.code)
    assert d.valid and d.game == "valorant"
    # report present and honest
    assert r.report.target_game == "valorant"
    assert r.report.source_game == "cs2"
    # original code preserved in metadata
    assert r.universal.metadata["original_code"] == CS2_V1[0][0]


def test_convert_valorant_to_cs2_defaults_to_cs2_v1():
    r = convert_crosshair(VALORANT_CODES[0], "cs2")
    assert r.success, r.error
    assert r.format == "cs2-v1"
    assert r.code.startswith("CS")
    d = detect_crosshair_format(r.code)
    assert d.valid and d.format == "cs2-v1"


def test_convert_cs2_legacy_to_cs2_native():
    r = convert_crosshair(CS2_LEGACY_V1[0][0], "cs2")
    assert r.success
    assert r.format == "cs2-v1"
    d = detect_crosshair_format(r.code)
    assert d.valid and d.format == "cs2-v1"
    # color carried over
    assert d.settings["red"] == 175 and d.settings["green"] == 81


def test_convert_to_deadlock_without_deadlock_source_reports_unrepresentable():
    r = convert_crosshair(VALORANT_CODES[0], "deadlock")
    assert not r.success
    assert r.report.unrepresentable  # honest: cannot fabricate a DL. payload


def test_convert_deadlock_round_trip_preserves_code():
    r = convert_crosshair(DEADLOCK_CODES[0], "deadlock")
    assert r.success
    assert r.code == DEADLOCK_CODES[0]  # lossless


def test_conversion_report_contents():
    r = convert_crosshair(CS2_V1[0][0], "valorant")
    assert r.report.converted
    assert r.report.source_format == "cs2-v1"
    assert r.report.target_format == "valorant-native"


def test_decode_to_universal_keeps_metadata():
    det, u, report = decode_to_universal(CS2_V1[0][0])
    assert det.valid
    assert u.metadata["source_game"] == "cs2"
    assert u.metadata["source_format"] == "cs2-v1"
    assert u.metadata["original_code"] == CS2_V1[0][0]
    assert u.color == "#FF0000"
    assert u.center_dot.enabled is True
