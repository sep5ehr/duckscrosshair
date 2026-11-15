"""Tests for share code encoding."""

import pytest
from crosshair.sharecode import encode_share_code, decode_share_code, EncodeResult
from crosshair.models import CrosshairSettings
from crosshair.conversion import internal_to_sharecode, export_share_code


def test_encode_basic():
    """Test basic encoding."""
    model = {
        "style": 4,
        "gap": 2,
        "length": 6.0,
        "thickness": 2.0,
        "size": 6.0,
        "outline_enabled": True,
        "outline_thickness": 1.0,
        "center_dot": False,
        "color": "#00FF00",
        "dynamic_spread_limit": 0.0,
        "split_distance": 7,
        "inner_split_alpha": 255,
        "outer_split_alpha": 255,
        "split_size_ratio": 0.5,
        "reference_resolution": 1920,
        "scope_dot_scale": 1.0,
        "scope_dot_use_crosshair_color": False,
        "t_style": False,
    }

    result = encode_share_code(model)
    assert result.success
    assert result.share_code is not None
    assert result.share_code.startswith("CSGO-")


def test_encode_with_center_dot():
    """Test encoding with center dot enabled."""
    model = {
        "style": 4,
        "gap": 2,
        "length": 6.0,
        "thickness": 2.0,
        "size": 6.0,
        "outline_enabled": True,
        "outline_thickness": 1.0,
        "center_dot": True,
        "color": "#FF0000",
        "dynamic_spread_limit": 0.0,
        "split_distance": 7,
        "inner_split_alpha": 255,
        "outer_split_alpha": 255,
        "split_size_ratio": 0.5,
        "reference_resolution": 1920,
        "scope_dot_scale": 1.0,
        "scope_dot_use_crosshair_color": False,
        "t_style": False,
    }

    result = encode_share_code(model)
    assert result.success

    # Decode back
    decode_result = decode_share_code(result.share_code)
    assert decode_result.success
    assert decode_result.internal_model["center_dot"] is True


def test_encode_t_style():
    """Test encoding with T-style."""
    model = {
        "style": 4,
        "gap": 2,
        "length": 6.0,
        "thickness": 2.0,
        "size": 6.0,
        "outline_enabled": True,
        "outline_thickness": 1.0,
        "center_dot": False,
        "color": "#00FF00",
        "dynamic_spread_limit": 0.0,
        "split_distance": 7,
        "inner_split_alpha": 255,
        "outer_split_alpha": 255,
        "split_size_ratio": 0.5,
        "reference_resolution": 1920,
        "scope_dot_scale": 1.0,
        "scope_dot_use_crosshair_color": False,
        "t_style": True,
    }

    result = encode_share_code(model)
    assert result.success

    decode_result = decode_share_code(result.share_code)
    assert decode_result.success
    assert decode_result.internal_model["t_style"] is True


def test_encode_custom_color():
    """Test encoding with custom color."""
    model = {
        "style": 4,
        "gap": 5,
        "length": 10.0,
        "thickness": 3.0,
        "size": 8.0,
        "outline_enabled": True,
        "outline_thickness": 2.0,
        "center_dot": True,
        "color": "#FF6600",  # Orange
        "dynamic_spread_limit": 0.5,
        "split_distance": 10,
        "inner_split_alpha": 200,
        "outer_split_alpha": 150,
        "split_size_ratio": 0.75,
        "reference_resolution": 1920,
        "scope_dot_scale": 1.5,
        "scope_dot_use_crosshair_color": True,
        "t_style": False,
    }

    result = encode_share_code(model)
    assert result.success

    decode_result = decode_share_code(result.share_code)
    assert decode_result.success
    # Color should be preserved (approximately due to quantization)
    assert decode_result.internal_model["color"] == "#FF6600"


def test_encode_invalid_version():
    """Test encoding with unsupported version."""
    model = {"style": 4, "gap": 2}
    result = encode_share_code(model, version=999)
    assert not result.success
    assert "Unsupported version" in result.error


def test_internal_to_sharecode():
    """Test conversion from internal model."""
    settings = CrosshairSettings(
        gap=3,
        length=8,
        thickness=2,
        size=5,
        color="#00FFFF",
        opacity=1.0,
        outline_enabled=True,
        outline_color="#000000",
        outline_thickness=1,
        center_dot=True,
        t_style=False,
        style=4,
        dynamic_spread_limit=0.0,
        split_distance=7,
        inner_split_alpha=255,
        outer_split_alpha=255,
        split_size_ratio=0.5,
        reference_resolution=1920,
        scope_dot_scale=1.0,
        scope_dot_use_crosshair_color=False,
    )

    model = internal_to_sharecode(settings)
    assert model["gap"] == 3
    assert model["color"] == "#00FFFF"
    assert model["center_dot"] is True

    result = encode_share_code(model)
    assert result.success


def test_export_share_code():
    """Test export_share_code convenience function."""
    settings = CrosshairSettings(
        gap=2,
        length=6,
        thickness=2,
        size=6,
        color="#00FF00",
    )

    code, warnings = export_share_code(settings)
    assert code is not None
    assert code.startswith("CSGO-")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])