"""VALORANT crosshair profile code decoder."""

from __future__ import annotations

from crosshair.codecs.base import CodecResult
from crosshair.codecs.valorant.parser import parse_code, serialize_code
from crosshair.codecs.valorant.schema import (
    ValorantProfile, GunCrosshairSection, SniperSection,
    PRESET_COLORS, CUSTOM_COLOR_INDEX,
)

_LINE_KEYS = {
    "b": "show", "a": "opacity", "l": "length", "v": "vertical_length",
    "g": "length_linked", "t": "thickness", "o": "offset",
    "m": "movement_error", "s": "movement_error_multiplier",
    "f": "firing_error", "e": "firing_error_multiplier",
}

_BOOL_KEYS = {"b", "g", "m", "f", "h", "d", "c", "s", "p"}


def _to_bool(value: str) -> bool:
    return value not in ("0", "", "false")


def _to_float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: str, default: int) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _apply_line_token(section: GunCrosshairSection, key: str, value: str, warnings: list) -> bool:
    """Apply a `0x`/`1x` line token. Returns True if handled."""
    if len(key) != 2 or key[0] not in ("0", "1") or key[1] not in _LINE_KEYS:
        return False
    lines = section.inner_lines if key[0] == "0" else section.outer_lines
    attr = _LINE_KEYS[key[1]]
    if attr in ("show", "length_linked", "movement_error", "firing_error"):
        setattr(lines, attr, _to_bool(value))
    elif attr in ("opacity", "movement_error_multiplier", "firing_error_multiplier"):
        setattr(lines, attr, _to_float(value, getattr(lines, attr)))
    else:
        setattr(lines, attr, _to_int(value, getattr(lines, attr)))
    return True


def _apply_gun_token(section: GunCrosshairSection, key: str, value: str) -> None:
    if key == "c":
        section.color_preset = _to_int(value, 0)
    elif key == "u":
        section.custom_color = value
        section.color_preset = CUSTOM_COLOR_INDEX
    elif key == "h":
        section.outline.enabled = _to_bool(value)
    elif key == "t":
        section.outline.thickness = _to_int(value, section.outline.thickness)
    elif key == "o":
        section.outline.opacity = _to_float(value, section.outline.opacity)
    elif key == "d":
        section.center_dot.enabled = _to_bool(value)
    elif key == "z":
        section.center_dot.thickness = _to_int(value, section.center_dot.thickness)
    elif key == "a":
        section.center_dot.opacity = _to_float(value, section.center_dot.opacity)
    elif key == "m":
        section.override_firing_error_offset = _to_bool(value)
    elif key == "f":
        section.fade_with_firing_error = _to_bool(value)
    elif key == "s":
        section.follow_spectating = _to_bool(value)


def decode_valorant_crosshair(code: str) -> CodecResult:
    """Decode a native VALORANT crosshair profile code.

    Returns game-native settings: the semantic profile plus the lossless
    token stream so re-encoding never loses unknown properties.
    """
    code = (code or "").strip()
    result = parse_code(code)
    if not result.ok:
        return CodecResult(success=False, game="valorant",
                           error="; ".join(result.errors))

    warnings = list(result.warnings)
    parsed = result.code
    profile = ValorantProfile()
    sections = {"P": profile.primary, "A": profile.ads}

    for tok in parsed.tokens:
        if tok.section is None:
            if tok.key == "c":
                profile.override_all_with_primary = _to_bool(tok.value)
            elif tok.key == "s":
                profile.advanced_options = _to_bool(tok.value)
            elif tok.key == "p":
                profile.ads_copy_primary = _to_bool(tok.value)
            elif tok.key == "NAME":
                profile.name = tok.value.strip('"')
            else:
                warnings.append("unknown header key %r (preserved)" % tok.key)
        elif tok.section in ("P", "A"):
            section = sections[tok.section]
            if not _apply_line_token(section, tok.key, tok.value, warnings):
                if tok.key in ("0b", "1b"):
                    pass
                _apply_gun_token(section, tok.key, tok.value)
                if tok.key not in ("c", "u", "h", "t", "o", "d", "z", "a", "m", "f", "s") \
                        and len(tok.key) != 2:
                    warnings.append("unknown key %r in section %r (preserved)"
                                    % (tok.key, tok.section))
        elif tok.section == "S":
            sniper = profile.sniper
            if tok.key == "d":
                sniper.show = _to_bool(tok.value)
            elif tok.key == "c":
                sniper.color_preset = _to_int(tok.value, 7)
            elif tok.key == "t":
                sniper.custom_color = tok.value
                sniper.color_preset = CUSTOM_COLOR_INDEX
            elif tok.key == "s":
                sniper.thickness = _to_float(tok.value, sniper.thickness)
            elif tok.key == "o":
                sniper.opacity = _to_float(tok.value, sniper.opacity)
            else:
                warnings.append("unknown key %r in sniper section (preserved)" % tok.key)
        else:
            warnings.append("unknown token %r (preserved)" % tok.key)

    # VALORANT semantics: when no `0g`/`1g` token is present the vertical line
    # length follows the horizontal one; when no `0v`/`1v` token is present and
    # lengths are linked, vertical == length.
    for section in (profile.primary, profile.ads):
        for prefix, lines in (("0", section.inner_lines), ("1", section.outer_lines)):
            has_g = parsed.get(prefix + "g", "P" if section is profile.primary else "A") is not None
            has_v = parsed.get(prefix + "v", "P" if section is profile.primary else "A") is not None
            if not has_g:
                lines.length_linked = False
                if not has_v:
                    lines.vertical_length = lines.length

    settings = {
        "format": "valorant-native",
        "profile": profile.to_dict(),
        "tokens": [
            {"key": t.key, "value": t.value, "section": t.section}
            for t in parsed.tokens
        ],
        "section_markers": [e.name for e in parsed.elements if hasattr(e, "name")],
        "trailing_separator": parsed.trailing_separator,
    }
    settings["parsed"] = parsed
    return CodecResult(
        success=True, game="valorant", format="valorant-native",
        settings=settings, code=code, warnings=warnings,
        metadata={"original_code": code},
    )
