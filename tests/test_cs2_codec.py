"""Tests for the verified CS2 codec (all four formats, real game fixtures)."""

import pytest

from crosshair.codecs.cs2 import (
    decode_cs2_crosshair, encode_cs2_crosshair, CS2_CODEC,
)
from tests.fixtures import (
    CS2_LEGACY_V1, CS2_LEGACY_V3, CS2_LEGACY_V4, CS2_V1, CS2_INVALID, CS2_CLAMP,
)

ALL_SAMPLES = CS2_LEGACY_V1 + CS2_LEGACY_V3 + CS2_LEGACY_V4 + CS2_V1


def assert_settings_equal(actual: dict, expected: dict):
    for key, value in expected.items():
        assert key in actual, "missing key %r" % key
        if isinstance(value, float):
            assert actual[key] == pytest.approx(value, abs=1e-9), key
        else:
            assert actual[key] == value, "%s: %r != %r" % (key, actual[key], value)


@pytest.mark.parametrize("code,expected", ALL_SAMPLES)
def test_decode_real_codes(code, expected):
    result = decode_cs2_crosshair(code)
    assert result.success, result.error
    assert result.game == "cs2"
    assert result.format == expected["format"]
    assert_settings_equal(result.settings, expected)
    assert result.metadata["original_code"] == code


@pytest.mark.parametrize("code,expected", ALL_SAMPLES)
def test_encode_real_codes_reproduces_exact_code(code, expected):
    result = encode_cs2_crosshair(expected, expected["format"])
    assert result.success, result.error
    assert result.code == code


@pytest.mark.parametrize("code,expected", ALL_SAMPLES)
def test_round_trip(code, expected):
    decoded = decode_cs2_crosshair(code)
    assert decoded.success
    reencoded = encode_cs2_crosshair(decoded.settings, decoded.format)
    assert reencoded.success
    assert reencoded.code == code
    decoded2 = decode_cs2_crosshair(reencoded.code)
    assert decoded2.success
    assert_settings_equal(decoded2.settings, expected)


def test_default_format_is_cs2_v1():
    assert CS2_CODEC.default_format == "cs2-v1"
    result = encode_cs2_crosshair(CS2_V1[0][1])  # no format arg
    assert result.success
    assert result.format == "cs2-v1"
    assert result.code.startswith("CS")


def test_all_four_formats_encodable():
    for fmt in ("legacy-v1", "legacy-v3", "legacy-v4", "cs2-v1"):
        sample = next(s for s in ALL_SAMPLES if s[1]["format"] == fmt)
        result = encode_cs2_crosshair(sample[1], fmt)
        assert result.success, fmt
        assert result.code == sample[0]


@pytest.mark.parametrize("code", CS2_INVALID)
def test_invalid_codes_rejected(code):
    result = decode_cs2_crosshair(code)
    assert not result.success
    assert result.error


@pytest.mark.parametrize("code,expected", CS2_CLAMP)
def test_cs2_clamps_like_the_game(code, expected):
    result = decode_cs2_crosshair(code)
    assert result.success, result.error
    for key, value in expected.items():
        if isinstance(value, float):
            assert result.settings[key] == pytest.approx(value, abs=1e-9)
        else:
            assert result.settings[key] == value


def test_unsupported_encode_format():
    result = encode_cs2_crosshair({}, "legacy-v2")
    assert not result.success


def test_legacy_v1_and_cs2_v1_are_distinct():
    # same version byte 1, different containers: must not be confused
    legacy = decode_cs2_crosshair(CS2_LEGACY_V1[0][0])
    native = decode_cs2_crosshair(CS2_V1[0][0])
    assert legacy.format == "legacy-v1"
    assert native.format == "cs2-v1"
