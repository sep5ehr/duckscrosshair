"""Tests for the VALORANT native profile code codec (real game codes)."""

import pytest

from crosshair.codecs.valorant import (
    decode_valorant_crosshair, encode_valorant_crosshair, VALORANT_CODEC,
)
from crosshair.codecs.valorant.parser import parse_code, serialize_code
from tests.fixtures import VALORANT_CODES, VALORANT_INVALID


@pytest.mark.parametrize("code", VALORANT_CODES)
def test_decode_real_codes(code):
    result = decode_valorant_crosshair(code)
    assert result.success, (code, result.error)
    assert result.game == "valorant"
    assert result.format == "valorant-native"
    assert "profile" in result.settings
    assert result.metadata["original_code"] == code


@pytest.mark.parametrize("code", VALORANT_CODES)
def test_lossless_token_round_trip(code):
    """decode -> encode reproduces the exact original code."""
    result = decode_valorant_crosshair(code)
    assert result.success
    reencoded = encode_valorant_crosshair(result.settings)
    assert reencoded.success, reencoded.error
    assert reencoded.code == code


@pytest.mark.parametrize("code", VALORANT_CODES)
def test_semantic_round_trip(code):
    """encode(profile) -> decode yields the same profile."""
    result = decode_valorant_crosshair(code)
    assert result.success
    encoded = encode_valorant_crosshair({"profile": result.settings["profile"]})
    assert encoded.success, encoded.error
    decoded2 = decode_valorant_crosshair(encoded.code)
    assert decoded2.success
    assert decoded2.settings["profile"] == result.settings["profile"], (
        code, encoded.code)


def test_parse_task_example_sections_and_values():
    code = VALORANT_CODES[0]
    result = decode_valorant_crosshair(code)
    assert result.success
    profile = result.settings["profile"]
    p = profile["primary"]
    assert p["color_preset"] == 5
    assert p["outline"]["enabled"] is False          # h;0
    assert p["inner_lines"]["length"] == 5           # 0l;5
    assert p["inner_lines"]["offset"] == 2           # 0o;2
    assert p["inner_lines"]["opacity"] == 1          # 0a;1
    assert p["inner_lines"]["firing_error"] is False # 0f;0
    assert p["outer_lines"]["show"] is False         # 1b;0
    sniper = profile["sniper"]
    assert sniper["color_preset"] == 4               # S;c;4
    assert sniper["opacity"] == 1                    # S;o;1
    assert profile["advanced_options"] is True       # s;1


def test_custom_color_preserved():
    code = "0;s;1;P;c;7;u;FF0000FF;h;0;0l;20;0o;0;0a;1;0f;0;1b;0"
    result = decode_valorant_crosshair(code)
    assert result.success
    p = result.settings["profile"]["primary"]
    assert p["color_preset"] == 8
    assert p["custom_color"] == "FF0000FF"
    encoded = encode_valorant_crosshair({"profile": result.settings["profile"]})
    assert encoded.success
    decoded2 = decode_valorant_crosshair(encoded.code)
    assert decoded2.settings["profile"]["primary"]["custom_color"] == "FF0000FF"


def test_ads_and_sniper_sections():
    code = VALORANT_CODES[2]  # has A and S sections
    result = decode_valorant_crosshair(code)
    assert result.success
    profile = result.settings["profile"]
    assert profile["ads_copy_primary"] is False       # p;0
    assert profile["ads"]["center_dot"]["enabled"] is True
    assert profile["sniper"]["thickness"] == 0.75    # S;s;0.75


def test_unknown_keys_preserved_losslessly():
    code = "0;s;1;P;c;5;xyz;7;0l;2"
    result = decode_valorant_crosshair(code)
    assert result.success
    assert any("xyz" in w for w in result.warnings)
    reencoded = encode_valorant_crosshair(result.settings)
    assert reencoded.code == code


@pytest.mark.parametrize("code", VALORANT_INVALID)
def test_invalid_codes_rejected(code):
    result = decode_valorant_crosshair(code)
    assert not result.success
    assert result.error


def test_parser_trailing_separator():
    parsed = parse_code("0;s;1;")
    assert parsed.ok
    assert parsed.code.trailing_separator is True
    assert serialize_code(parsed.code) == "0;s;1;"


def test_default_format():
    assert VALORANT_CODEC.default_format == "valorant-native"
