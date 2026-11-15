"""Tests for share code round-trip encoding/decoding."""

import pytest
from crosshair.sharecode import encode_share_code, decode_share_code
from crosshair.conversion import import_share_code, export_share_code
from crosshair.models import CrosshairSettings


def test_round_trip_basic():
    """Test basic round-trip: settings -> share code -> settings."""
    original = CrosshairSettings(
        gap=2,
        length=6,
        thickness=2,
        size=6,
        color="#00FF00",
        opacity=1.0,
        outline_enabled=True,
        outline_color="#000000",
        outline_thickness=1,
        center_dot=False,
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

    # Export to share code
    share_code, export_warnings = export_share_code(original)
    assert share_code is not None
    assert share_code.startswith("CSGO-")

    # Import from share code
    imported, import_warnings, format_name = import_share_code(share_code)
    assert imported is not None
    assert format_name == "CS2 v1"

    # Check key settings preserved
    assert imported.gap == original.gap
    assert imported.length == original.length
    assert imported.thickness == original.thickness
    assert imported.size == original.size
    assert imported.color == original.color
    assert imported.outline_enabled == original.outline_enabled
    assert imported.outline_thickness == original.outline_thickness
    assert imported.center_dot == original.center_dot
    assert imported.t_style == original.t_style
    assert imported.style == original.style


def test_round_trip_with_center_dot():
    """Test round-trip with center dot enabled."""
    original = CrosshairSettings(
        gap=3,
        length=8,
        thickness=2,
        size=4,
        color="#FF0000",
        center_dot=True,
        t_style=False,
    )

    share_code, _ = export_share_code(original)
    imported, _, _ = import_share_code(share_code)

    assert imported.center_dot is True
    assert imported.color == "#FF0000"


def test_round_trip_with_t_style():
    """Test round-trip with T-style enabled."""
    original = CrosshairSettings(
        gap=2,
        length=6,
        thickness=2,
        t_style=True,
    )

    share_code, _ = export_share_code(original)
    imported, _, _ = import_share_code(share_code)

    assert imported.t_style is True


def test_round_trip_custom_colors():
    """Test round-trip with various colors."""
    colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#808080"]

    for color in colors:
        original = CrosshairSettings(
            gap=2,
            length=6,
            thickness=2,
            color=color,
        )

        share_code, _ = export_share_code(original)
        imported, _, _ = import_share_code(share_code)

        # Color should be preserved (may have slight quantization)
        assert imported.color == color, f"Color mismatch for {color}: got {imported.color}"


def test_round_trip_all_styles():
    """Test round-trip for all CS2 styles."""
    for style in range(6):  # 0-5
        original = CrosshairSettings(
            gap=2,
            length=6,
            thickness=2,
            style=style,
        )

        share_code, _ = export_share_code(original)
        imported, _, _ = import_share_code(share_code)

        assert imported.style == style, f"Style mismatch for {style}: got {imported.style}"


def test_round_trip_dynamic_values():
    """Test round-trip with dynamic spread values."""
    original = CrosshairSettings(
        gap=2,
        length=6,
        thickness=2,
        dynamic_spread_limit=0.5,
        split_distance=10,
        inner_split_alpha=200,
        outer_split_alpha=150,
        split_size_ratio=0.75,
    )

    share_code, _ = export_share_code(original)
    imported, _, _ = import_share_code(share_code)

    # These values may have quantization due to 8-bit encoding
    assert abs(imported.dynamic_spread_limit - original.dynamic_spread_limit) < 0.01
    assert imported.split_distance == original.split_distance
    assert imported.inner_split_alpha == original.inner_split_alpha
    assert imported.outer_split_alpha == original.outer_split_alpha
    assert abs(imported.split_size_ratio - original.split_size_ratio) < 0.01


def test_round_trip_scope_settings():
    """Test round-trip with scope settings."""
    original = CrosshairSettings(
        gap=2,
        length=6,
        thickness=2,
        reference_resolution=1920,
        scope_dot_scale=1.5,
        scope_dot_use_crosshair_color=True,
    )

    share_code, _ = export_share_code(original)
    imported, _, _ = import_share_code(share_code)

    assert imported.reference_resolution == original.reference_resolution
    assert abs(imported.scope_dot_scale - original.scope_dot_scale) < 0.01
    assert imported.scope_dot_use_crosshair_color == original.scope_dot_use_crosshair_color


def test_multiple_round_trips():
    """Test multiple consecutive round-trips don't degrade."""
    original = CrosshairSettings(
        gap=5,
        length=10,
        thickness=3,
        size=8,
        color="#FF6600",
        center_dot=True,
        t_style=False,
        style=4,
    )

    current = original
    for i in range(5):
        share_code, _ = export_share_code(current)
        imported, _, _ = import_share_code(share_code)
        current = imported

    # After 5 round-trips, core settings should still match
    assert current.gap == original.gap
    assert current.length == original.length
    assert current.thickness == original.thickness
    assert current.color == original.color
    assert current.center_dot == original.center_dot


def test_import_unknown_code():
    """Test importing an unknown/invalid code."""
    result = import_share_code("CSGO-INVALIDCODE123")
    assert result[0] is None  # settings is None
    assert len(result[1]) > 0  # warnings present


def test_import_wrong_prefix():
    """Test importing code with wrong prefix."""
    result = import_share_code("CS2-ABCDEF")
    assert result[0] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])