"""Tests for crosshair validation."""

import pytest
from crosshair.models import CrosshairSettings
from crosshair.validation import (
    validate_crosshair_settings, validate_int, validate_float,
    validate_color, clamp_value
)


def test_clamp_value():
    """Test value clamping."""
    val, clamped = clamp_value(5, 0, 10)
    assert val == 5 and not clamped

    val, clamped = clamp_value(-1, 0, 10)
    assert val == 0 and clamped

    val, clamped = clamp_value(15, 0, 10)
    assert val == 10 and clamped


def test_validate_int():
    """Test integer validation."""
    result = validate_int(5, 0, 10, "test")
    assert result.valid and result.value == 5 and not result.clamped

    result = validate_int(-1, 0, 10, "test")
    assert result.valid and result.value == 0 and result.clamped

    result = validate_int("abc", 0, 10, "test")
    assert not result.valid


def test_validate_float():
    """Test float validation."""
    result = validate_float(0.5, 0.0, 1.0, "test")
    assert result.valid and result.value == 0.5 and not result.clamped

    result = validate_float(1.5, 0.0, 1.0, "test")
    assert result.valid and result.value == 1.0 and result.clamped


def test_validate_color():
    """Test color validation."""
    result = validate_color("#FF0000", "test")
    assert result.valid and result.value == "#FF0000"

    result = validate_color("FF0000", "test")
    assert result.valid and result.value == "#FF0000"

    result = validate_color("#FF0000FF", "test")
    assert result.valid and result.value == "#FF0000FF"

    result = validate_color("#GGG", "test")
    assert not result.valid

    result = validate_color("red", "test")
    assert not result.valid


def test_validate_crosshair_settings():
    """Test full crosshair settings validation."""
    settings = CrosshairSettings(
        gap=5,
        length=10,
        thickness=2,
        size=5,
        color="#00FF00",
        opacity=1.0,
        outline_enabled=True,
        outline_color="#000000",
        outline_thickness=1,
        center_dot=False,
        t_style=False,
    )
    validated, warnings = validate_crosshair_settings(settings)
    assert validated.gap == 5
    assert len(warnings) == 0


def test_validate_crosshair_clamping():
    """Test crosshair settings clamping."""
    settings = CrosshairSettings(
        gap=100,  # Will be clamped to 50
        length=200,  # Will be clamped to 100
        thickness=50,  # Will be clamped to 20
        color="#GGGGGG",  # Invalid, will be reset
    )
    validated, warnings = validate_crosshair_settings(settings)
    assert validated.gap == 50
    assert validated.length == 100
    assert validated.thickness == 20
    assert validated.color == "#000000"
    assert len(warnings) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])