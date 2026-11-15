"""Cross-game conversion engine.

Pipeline: source code -> source decoder -> universal model -> compatibility
mapping -> target encoder -> target code, with a report of what was converted,
what was unsupported, and what fell back to defaults. The original code is
always preserved in the universal model's metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from crosshair.codecs.base import CodecResult, ConversionReport
from crosshair.codecs.registry import GAME_CODECS, get_codec
from crosshair.core.detect import detect_crosshair_format
from crosshair.core.universal import UniversalCrosshair


# ---------------------------------------------------------------------------
# game-native settings -> universal
# ---------------------------------------------------------------------------

def _hex(rgb) -> str:
    return "#%02X%02X%02X" % (int(rgb[0]) & 0xFF, int(rgb[1]) & 0xFF, int(rgb[2]) & 0xFF)


def cs2_to_universal(settings: dict, report: ConversionReport) -> UniversalCrosshair:
    fmt = settings.get("format", "cs2-v1")
    u = UniversalCrosshair(game="cs2")
    u.color = _hex((settings.get("red", 50), settings.get("green", 250), settings.get("blue", 50)))
    alpha = settings.get("alpha", 255)
    u.alpha = alpha / 255.0 if isinstance(alpha, (int, float)) else 1.0
    report.converted.append("color")

    u.center_dot.enabled = bool(settings.get("center_dot_enabled", False))
    u.center_dot.size = 1.0  # CS2 dot has no size setting
    u.center_dot.opacity = u.alpha
    report.converted.append("center_dot.enabled")

    gap = settings.get("gap", 4)
    u.inner_lines.enabled = True
    u.inner_lines.thickness = settings.get("thickness", 2)
    u.inner_lines.length = settings.get("length", 8)
    u.inner_lines.offset = abs(gap) if isinstance(gap, (int, float)) else 4
    u.inner_lines.opacity = u.alpha
    report.converted += ["lines.thickness", "lines.length", "lines.offset"]

    split = settings.get("split_distance", 0)
    u.outer_lines.enabled = bool(split)
    u.outer_lines.offset = split if isinstance(split, (int, float)) else 0
    if split:
        report.converted.append("outer_lines.enabled/offset (split distance)")

    if fmt == "cs2-v1":
        u.outline.enabled = settings.get("outline_mode", 0) > 0
        u.outline.color = _hex((settings.get("outline_red", 0), settings.get("outline_green", 0),
                                settings.get("outline_blue", 0)))
        u.outline.opacity = settings.get("outline_alpha", 255) / 255.0
        report.converted.append("outline.rgba")
    elif fmt == "legacy-v4":
        u.outline.enabled = settings.get("outline_mode", 0) > 0
        u.outline.color = "#000000"
        u.outline.opacity = u.alpha
        report.converted.append("outline.enabled")
    elif fmt == "legacy-v3":
        u.outline.enabled = bool(settings.get("outline_enabled", True))
        report.defaulted.append("outline.color -> #000000 (legacy-v3 stores no outline color)")
        report.defaulted.append("outline.thickness -> 1 (legacy-v3 stores no outline thickness)")
    else:  # legacy-v1
        u.outline.enabled = bool(settings.get("outline_enabled", False))
        u.outline.thickness = settings.get("outline", 1.0)
        report.defaulted.append("outline.color -> #000000 (legacy-v1 stores no outline color)")

    u.game_extensions["cs2"] = {
        k: v for k, v in settings.items()
        if k not in ("red", "green", "blue", "alpha", "gap", "length", "thickness",
                     "split_distance", "center_dot_enabled")
    }
    return u


def valorant_to_universal(settings: dict, report: ConversionReport) -> UniversalCrosshair:
    from crosshair.codecs.valorant.schema import ValorantProfile, PRESET_COLORS, CUSTOM_COLOR_INDEX
    profile = ValorantProfile.from_dict(settings.get("profile", {}))
    p = profile.primary
    u = UniversalCrosshair(game="valorant")

    if p.color_preset == CUSTOM_COLOR_INDEX and p.custom_color:
        hexc = p.custom_color.lstrip("#")
        u.color = "#" + hexc[:6].upper()
        report.converted.append("color (custom hex)")
    elif p.color_preset in PRESET_COLORS:
        u.color = PRESET_COLORS[p.color_preset]
        report.converted.append("color (preset %d)" % p.color_preset)
    else:
        report.defaulted.append("color -> preset 0 (unknown preset %r)" % p.color_preset)

    u.outline.enabled = p.outline.enabled
    u.outline.thickness = p.outline.thickness
    u.outline.opacity = p.outline.opacity
    u.outline.color = "#000000"  # VALORANT outline color is fixed black
    report.converted += ["outline.enabled", "outline.thickness", "outline.opacity"]
    report.defaulted.append("outline.color -> #000000 (VALORANT outlines are always black)")

    u.center_dot.enabled = p.center_dot.enabled
    u.center_dot.size = p.center_dot.thickness
    u.center_dot.opacity = p.center_dot.opacity
    report.converted += ["center_dot.*"]

    for src, dst in ((p.inner_lines, u.inner_lines), (p.outer_lines, u.outer_lines)):
        dst.enabled = src.show
        dst.thickness = src.thickness
        dst.length = src.length
        dst.offset = src.offset
        dst.opacity = src.opacity
        dst.movement_error = src.movement_error
        dst.firing_error = src.firing_error
    report.converted += ["inner_lines.*", "outer_lines.*"]

    u.alpha = 1.0
    report.defaulted.append("alpha -> 1.0 (VALORANT has no global crosshair alpha)")

    u.game_extensions["valorant"] = {
        "general": {
            "override_all_with_primary": profile.override_all_with_primary,
            "advanced_options": profile.advanced_options,
            "ads_copy_primary": profile.ads_copy_primary,
            "name": profile.name,
        },
        "ads_section": settings.get("profile", {}).get("ads"),
        "sniper_section": settings.get("profile", {}).get("sniper"),
        "inner_vertical_length": p.inner_lines.vertical_length,
        "outer_vertical_length": p.outer_lines.vertical_length,
        "movement_error_multipliers": {
            "inner": p.inner_lines.movement_error_multiplier,
            "outer": p.outer_lines.movement_error_multiplier,
        },
        "firing_error_multipliers": {
            "inner": p.inner_lines.firing_error_multiplier,
            "outer": p.outer_lines.firing_error_multiplier,
        },
    }
    report.unsupported += [
        "ads section (VALORANT-specific)",
        "sniper section (VALORANT-specific)",
        "per-line vertical length (VALORANT-specific)",
        "movement/firing error multipliers (no universal equivalent)",
    ]
    return u


def deadlock_to_universal(settings: dict, report: ConversionReport) -> UniversalCrosshair:
    u = UniversalCrosshair(game="deadlock")
    report.unrepresentable.append(
        "Deadlock field semantics are wire-level only (unverified mapping); "
        "raw payload preserved in game_extensions")
    u.game_extensions["deadlock"] = {
        "raw_hex": settings.get("raw_hex"),
        "wire_fields": settings.get("wire_fields"),
        "wire_parse_ok": settings.get("wire_parse_ok"),
    }
    return u


_TO_UNIVERSAL = {
    "cs2": cs2_to_universal,
    "valorant": valorant_to_universal,
    "deadlock": deadlock_to_universal,
}


# ---------------------------------------------------------------------------
# universal -> game-native settings
# ---------------------------------------------------------------------------

def universal_to_cs2(u: UniversalCrosshair, report: ConversionReport, format: str = "cs2-v1") -> dict:
    from crosshair.codecs.cs2.schema import FORMAT_CLASSES
    cls = FORMAT_CLASSES[format]
    r, g, b = (int(u.color[i:i + 2], 16) for i in (1, 3, 5))
    alpha = int(round(u.alpha * 255))
    s = dict(
        format=format,
        red=r, green=g, blue=b, alpha=alpha,
        gap=int(u.inner_lines.offset),
        length=int(u.inner_lines.length),
        thickness=int(u.inner_lines.thickness),
        center_dot_enabled=u.center_dot.enabled,
        t_style_enabled=False,
        split_distance=int(u.outer_lines.offset) if u.outer_lines.enabled else 0,
        screen_height=1080,
    )
    ext = u.game_extensions.get("cs2", {})
    # carry over source CS2 properties when converting CS2 -> CS2-compatible targets
    for key, default in (
        ("style", 4), ("follow_recoil", False), ("dynamic_spread_limit", 255),
        ("inner_split_alpha", 1.0), ("outer_split_alpha", 0.45), ("split_size_ratio", 0.3),
    ):
        s[key] = ext.get(key, default)
    if format == "cs2-v1":
        s["outline_mode"] = 1 if u.outline.enabled else 0
        or_, og, ob = (int(u.outline.color[i:i + 2], 16) for i in (1, 3, 5))
        s["outline_red"], s["outline_green"], s["outline_blue"] = or_, og, ob
        s["outline_alpha"] = int(round(u.outline.opacity * 255))
        s["scope_dot_scale"] = float(ext.get("scope_dot_scale", 1.0))
        s["scope_dot_use_crosshair_color"] = bool(ext.get("scope_dot_use_crosshair_color", False))
        report.converted.append("outline.rgba -> cs2-v1")
    elif format == "legacy-v4":
        s["outline_mode"] = 1 if u.outline.enabled else 0
        report.defaulted.append("outline.color -> dropped (legacy-v4 has no outline RGB)")
    elif format == "legacy-v3":
        s["outline_enabled"] = u.outline.enabled
        report.defaulted.append("outline.color/thickness -> dropped (legacy-v3)")
    else:
        s.update(
            outline=u.outline.thickness,
            outline_enabled=u.outline.enabled,
            color=1,
            alpha_enabled=alpha != 255,
            fixed_crosshair_gap=3.0,
            deployed_weapon_gap_enabled=False,
        )
        report.defaulted.append("legacy-v1: gap stored as float/10, style limited to 0-3")
    report.converted += ["color.rgb", "alpha", "center_dot", "lines", "split_distance"]
    # only keep fields valid for the target format
    valid = set(cls.__dataclass_fields__)
    return {k: v for k, v in s.items() if k in valid}


def universal_to_valorant(u: UniversalCrosshair, report: ConversionReport) -> dict:
    from crosshair.codecs.valorant.schema import (
        ValorantProfile, GunCrosshairSection, LineSettings, OutlineSettings,
        DotSettings, SniperSection, PRESET_COLORS, CUSTOM_COLOR_INDEX,
    )
    profile = ValorantProfile()
    p = profile.primary

    hexc = u.color.lstrip("#").upper()
    presets = {v.lstrip("#"): k for k, v in PRESET_COLORS.items()}
    if hexc in presets:
        p.color_preset = presets[hexc]
        report.converted.append("color -> preset %d" % p.color_preset)
    else:
        p.color_preset = CUSTOM_COLOR_INDEX
        p.custom_color = hexc + "FF"
        report.converted.append("color -> custom hex")

    p.outline = OutlineSettings(enabled=u.outline.enabled, thickness=u.outline.thickness,
                                opacity=u.outline.opacity)
    p.center_dot = DotSettings(enabled=u.center_dot.enabled, thickness=int(u.center_dot.size),
                               opacity=u.center_dot.opacity)
    p.inner_lines = LineSettings(
        show=u.inner_lines.enabled, thickness=u.inner_lines.thickness,
        length=int(u.inner_lines.length), offset=int(u.inner_lines.offset),
        opacity=u.inner_lines.opacity, movement_error=u.inner_lines.movement_error,
        firing_error=u.inner_lines.firing_error)
    p.outer_lines = LineSettings(
        show=u.outer_lines.enabled, thickness=u.outer_lines.thickness,
        length=int(u.outer_lines.length), offset=int(u.outer_lines.offset),
        opacity=u.outer_lines.opacity, movement_error=u.outer_lines.movement_error,
        firing_error=u.outer_lines.firing_error)
    report.converted += ["outline", "center_dot", "inner_lines", "outer_lines"]

    if u.alpha != 1.0:
        report.unsupported.append("global alpha (VALORANT has no global crosshair alpha)")
    report.defaulted.append("ads section -> default (VALORANT-specific)")
    report.defaulted.append("sniper section -> default (VALORANT-specific)")
    report.unsupported.append("vertical line lengths -> linked to horizontal length")
    return {"profile": profile.to_dict()}


def universal_to_deadlock(u: UniversalCrosshair, report: ConversionReport) -> dict:
    # No verified semantic mapping exists; carry the raw payload when the
    # source was Deadlock, otherwise we cannot fabricate one.
    raw = u.game_extensions.get("deadlock", {}).get("raw_hex")
    if raw is None:
        report.unrepresentable.append(
            "No verified Deadlock field mapping: cannot synthesize a DL. payload from "
            "universal settings without a verified reference. Import a real DL. code first.")
        return {}
    report.converted.append("raw payload preserved (wire-level)")
    return {"raw_hex": raw}


_FROM_UNIVERSAL = {
    "cs2": universal_to_cs2,
    "valorant": universal_to_valorant,
    "deadlock": universal_to_deadlock,
}


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

@dataclass
class ConversionResult:
    success: bool
    code: Optional[str] = None
    game: str = ""
    format: str = ""
    universal: Optional[UniversalCrosshair] = None
    report: Optional[ConversionReport] = None
    error: Optional[str] = None
    warnings: list = field(default_factory=list)


def decode_to_universal(code: str) -> tuple:
    """Detect + decode a code and convert to the universal model.

    Returns (DetectionResult, UniversalCrosshair, ConversionReport).
    """
    det = detect_crosshair_format(code)
    if not det.valid:
        return det, None, None
    report = ConversionReport(source_game=det.game, source_format=det.format)
    u = _TO_UNIVERSAL[det.game](det.settings, report)
    u.metadata = dict(det.metadata)
    u.metadata["source_game"] = det.game
    u.metadata["source_format"] = det.format
    u.metadata["original_code"] = det.code
    return det, u, report


def convert_crosshair(code: str, target_game: str, target_format: str = None) -> ConversionResult:
    """Full pipeline: code -> decode -> universal -> target encoder -> code."""
    det, u, report = decode_to_universal(code)
    if not det.valid:
        return ConversionResult(success=False, error=det.error)
    codec = get_codec(target_game)
    fmt = target_format or codec.default_format
    report.target_game = target_game
    report.target_format = fmt
    settings = _FROM_UNIVERSAL[target_game](u, report, fmt) if target_game == "cs2" \
        else _FROM_UNIVERSAL[target_game](u, report)
    enc = codec.encode(settings, fmt)
    if not enc.success:
        report.warnings.append("Target encoding failed: %s" % enc.error)
        return ConversionResult(success=False, game=target_game, format=fmt,
                                universal=u, report=report, error=enc.error,
                                warnings=list(report.warnings))
    return ConversionResult(success=True, code=enc.code, game=target_game, format=fmt,
                            universal=u, report=report,
                            warnings=list(report.warnings) + list(enc.warnings))


def encode_universal(u: UniversalCrosshair, game: str, format: str = None) -> CodecResult:
    """Encode a universal model directly to a game code."""
    codec = get_codec(game)
    fmt = format or codec.default_format
    report = ConversionReport(target_game=game, target_format=fmt,
                              source_game=u.metadata.get("source_game", "universal"))
    settings = _FROM_UNIVERSAL[game](u, report, fmt) if game == "cs2" \
        else _FROM_UNIVERSAL[game](u, report)
    result = codec.encode(settings, fmt)
    result.warnings = list(report.warnings) + list(result.warnings) + result.warnings
    return result
