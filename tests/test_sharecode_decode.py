"""Tests for share code decoding."""

import pytest
from crosshair.sharecode import (
    decode_share_code, encode_share_code, validate_share_code,
    DecodeResult, EncodeResult
)
from crosshair.sharecode.alphabet import encode_bytes, decode_string
from crosshair.sharecode.checksum import crc8, verify_checksum, add_checksum, validate_and_strip_checksum
from crosshair.sharecode.layouts import CS2CrosshairData, pack_fields, unpack_fields, CS2_FIELDS_V1


def test_alphabet_encode_decode():
    """Test base32 alphabet encoding/decoding."""
    test_data = b"Hello World"
    encoded = encode_bytes(test_data)
    decoded = decode_string(encoded)
    assert decoded == test_data


def test_alphabet_invalid_char():
    """Test invalid character detection."""
    with pytest.raises(Exception):  # InvalidAlphabetError
        decode_string("INVALID!")


def test_crc8_checksum():
    """Test CRC8 checksum calculation."""
    data = b"test data"
    checksum = crc8(data)
    assert isinstance(checksum, int)
    assert 0 <= checksum <= 255
    assert verify_checksum(data, checksum)


def test_add_and_validate_checksum():
    """Test adding and validating checksum."""
    data = b"payload data"
    with_checksum = add_checksum(data)
    assert len(with_checksum) == len(data) + 1

    stripped = validate_and_strip_checksum(with_checksum)
    assert stripped == data


def test_invalid_checksum():
    """Test invalid checksum detection."""
    data = b"payload data"
    with_checksum = add_checksum(data)
    # Corrupt the checksum
    corrupted = with_checksum[:-1] + bytes([(with_checksum[-1] + 1) % 256])

    with pytest.raises(Exception):  # InvalidChecksumError
        validate_and_strip_checksum(corrupted)


def test_pack_unpack_fields():
    """Test packing and unpacking CS2 fields."""
    original = CS2CrosshairData(
        version=1,
        style=4,
        gap=-2,
        length=4.0,
        thickness=1.0,
        size=4.0,
        draw_outline=1,
        outline_thickness=1.0,
        dot=0,
        color_r=0,
        color_g=255,
        color_b=0,
        dynamic_spread_limit=0.0,
        split_distance=7,
        inner_split_alpha=255,
        outer_split_alpha=255,
        split_size_ratio=0.5,
        reference_resolution=1920,
        scope_dot_scale=1.0,
        scope_dot_use_crosshair_color=0,
        t_style=0,
        sniper_width=1,
    )

    packed = pack_fields(original, CS2_FIELDS_V1)
    unpacked = unpack_fields(packed, CS2_FIELDS_V1)

    assert unpacked.version == original.version
    assert unpacked.style == original.style
    assert unpacked.gap == original.gap
    assert abs(unpacked.length - original.length) < 0.01
    assert abs(unpacked.thickness - original.thickness) < 0.01
    assert unpacked.color_r == original.color_r
    assert unpacked.color_g == original.color_g
    assert unpacked.color_b == original.color_b


def test_decode_invalid_prefix():
    """Test decoding code without CSGO- prefix."""
    result = decode_share_code("INVALIDCODE")
    assert not result.success
    assert "must start with 'CSGO-'" in result.error


def test_decode_empty_code():
    """Test decoding empty code."""
    result = decode_share_code("")
    assert not result.success


def test_decode_valid_format_structure():
    """Test that a properly structured code can be decoded."""
    # Create a valid CS2 crosshair data
    data = CS2CrosshairData(
        version=1,
        style=4,
        gap=-2,
        length=4.0,
        thickness=1.0,
        size=4.0,
        draw_outline=1,
        outline_thickness=1.0,
        dot=0,
        color_r=0,
        color_g=255,
        color_b=0,
        dynamic_spread_limit=0.0,
        split_distance=7,
        inner_split_alpha=255,
        outer_split_alpha=255,
        split_size_ratio=0.5,
        reference_resolution=1920,
        scope_dot_scale=1.0,
        scope_dot_use_crosshair_color=0,
        t_style=0,
        sniper_width=1,
    )

    # Encode it
    encode_result = encode_share_code(data.to_internal_model())
    assert encode_result.success

    # Decode it back
    decode_result = decode_share_code(encode_result.share_code)
    assert decode_result.success
    assert decode_result.internal_model is not None
    assert decode_result.internal_model["gap"] == 2  # Positive in internal


if __name__ == "__main__":
    pytest.main([__file__, "-v"])