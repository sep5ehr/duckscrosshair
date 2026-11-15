"""Conversion between CS2 share code models and internal crosshair model."""

from typing import Optional
from crosshair.models import CrosshairSettings
from crosshair.sharecode import CS2ShareCodec, DecodeResult


def sharecode_to_internal(decode_result: DecodeResult) -> tuple[CrosshairSettings, list[str]]:
    """
    Convert a successful decode result to internal CrosshairSettings.

    Returns:
        (CrosshairSettings, warnings)
    """
    warnings = []

    if not decode_result.success or not decode_result.internal_model:
        return CrosshairSettings(), ["Decode failed, using defaults"]

    model = decode_result.internal_model
    cs2_data = decode_result.crosshair_data

    # Map CS2 fields to internal model
    internal = CrosshairSettings(
        gap=model.get("gap", 2),
        length=model.get("length", 6),
        thickness=model.get("thickness", 2),
        size=model.get("size", 6),
        color=model.get("color", "#00FF00"),
        opacity=1.0,  # CS2 doesn't store opacity separately
        outline_enabled=model.get("outline_enabled", True),
        outline_color="#000000",  # CS2 uses black outline
        outline_thickness=model.get("outline_thickness", 1),
        center_dot=model.get("center_dot", False),
        t_style=model.get("t_style", False),
        style=model.get("style", 4),
        dynamic_spread_limit=model.get("dynamic_spread_limit", 0.0),
        split_distance=model.get("split_distance", 7),
        inner_split_alpha=model.get("inner_split_alpha", 255),
        outer_split_alpha=model.get("outer_split_alpha", 255),
        split_size_ratio=model.get("split_size_ratio", 0.5),
        reference_resolution=model.get("reference_resolution", 1920),
        scope_dot_scale=model.get("scope_dot_scale", 1.0),
        scope_dot_use_crosshair_color=model.get("scope_dot_use_crosshair_color", False),
    )

    # Warnings for fields that don't map perfectly
    if cs2_data:
        # CS2 outline is always black, but we allow custom outline color
        if cs2_data.draw_outline and internal.outline_color != "#000000":
            warnings.append("CS2 share codes only support black outline; custom outline color will not be preserved in share code")

        # CS2 doesn't store opacity separately
        warnings.append("Opacity is not stored in CS2 share codes; defaulting to 1.0")

    return internal, warnings


def internal_to_sharecode(internal: CrosshairSettings) -> dict:
    """
    Convert internal CrosshairSettings to model dict for share code encoding.
    """
    return {
        "style": internal.style,
        "gap": internal.gap,
        "length": internal.length,
        "thickness": internal.thickness,
        "size": internal.size,
        "outline_enabled": internal.outline_enabled,
        "outline_thickness": internal.outline_thickness,
        "center_dot": internal.center_dot,
        "color": internal.color,
        "dynamic_spread_limit": internal.dynamic_spread_limit,
        "split_distance": internal.split_distance,
        "inner_split_alpha": internal.inner_split_alpha,
        "outer_split_alpha": internal.outer_split_alpha,
        "split_size_ratio": internal.split_size_ratio,
        "reference_resolution": internal.reference_resolution,
        "scope_dot_scale": internal.scope_dot_scale,
        "scope_dot_use_crosshair_color": internal.scope_dot_use_crosshair_color,
        "t_style": internal.t_style,
    }


def import_share_code(share_code: str) -> tuple[Optional[CrosshairSettings], list[str], Optional[str]]:
    """
    Import a share code and return internal settings.

    Returns:
        (CrosshairSettings or None, warnings, format_name or None)
    """
    codec = CS2ShareCodec()
    result = codec.decode(share_code)

    if not result.success:
        return None, [result.error or "Unknown error"], None

    settings, conv_warnings = sharecode_to_internal(result)
    all_warnings = result.warnings + conv_warnings

    return settings, all_warnings, result.format_name


def export_share_code(settings: CrosshairSettings) -> tuple[Optional[str], list[str]]:
    """
    Export internal settings to a CS2 share code.

    Returns:
        (share_code or None, warnings)
    """
    codec = CS2ShareCodec()
    model = internal_to_sharecode(settings)
    result = codec.encode(model)

    if not result.success:
        return None, [result.error or "Encoding failed"] + result.warnings

    return result.share_code, result.warnings