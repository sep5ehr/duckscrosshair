"""Tests for the Deadlock `DL.` reticle share code codec.

NOTE: no verified reference implementation / game-generated fixture set for
the DL. payload semantics was available, so tests cover what is verified:
prefix + base64url validation, lossless byte-level round-trip, and rejection
of malformed codes. Semantic field decoding is intentionally NOT claimed.
"""

import pytest

from crosshair.codecs.deadlock import (
    decode_deadlock_crosshair, encode_deadlock_crosshair, DEADLOCK_CODEC,
)
from tests.fixtures import DEADLOCK_CODES, DEADLOCK_INVALID


@pytest.mark.parametrize("code", DEADLOCK_CODES)
def test_decode_real_code(code):
    result = decode_deadlock_crosshair(code)
    assert result.success, result.error
    assert result.game == "deadlock"
    assert result.format == "deadlock-reticle"
    assert result.settings["raw_hex"]
    assert result.metadata["original_code"] == code
    # semantic uncertainty must be reported, not hidden
    assert any("unverified" in w or "wire" in w for w in result.warnings)


@pytest.mark.parametrize("code", DEADLOCK_CODES)
def test_lossless_round_trip(code):
    decoded = decode_deadlock_crosshair(code)
    assert decoded.success
    reencoded = encode_deadlock_crosshair(decoded.settings)
    assert reencoded.success, reencoded.error
    assert reencoded.code == code
    decoded2 = decode_deadlock_crosshair(reencoded.code)
    assert decoded2.success
    assert decoded2.settings["raw_hex"] == decoded.settings["raw_hex"]


@pytest.mark.parametrize("code", DEADLOCK_INVALID)
def test_invalid_codes_rejected(code):
    result = decode_deadlock_crosshair(code)
    assert not result.success


def test_encode_requires_payload():
    result = encode_deadlock_crosshair({})
    assert not result.success


def test_default_format():
    assert DEADLOCK_CODEC.default_format == "deadlock-reticle"
