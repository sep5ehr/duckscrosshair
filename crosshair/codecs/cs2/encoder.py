"""CS2 share code encoder (all four formats).

Byte layouts ported from the verified `csgo-sharecode@7.0.1` implementation.
New codes default to the native `cs2-v1` format; legacy formats remain
encodable for users who need them.
"""

from __future__ import annotations

from crosshair.codecs.base import CodecResult
from crosshair.codecs.cs2.formats import (
    apply_crosshair_checksum,
    bytes_to_cs2_code,
    bytes_to_share_code,
    clamp,
)
from crosshair.codecs.cs2.schema import ALL_FORMATS, settings_from_dict, settings_to_dict

_SPLIT_ALPHA_STEPS_PER_UNIT = 20
_SPLIT_SIZE_RATIO_STEPS_PER_UNIT = 100
_LEGACY_OUTER_SPLIT_ALPHA_MIN_STEPS = 6

_STEPS_PER_UNIT = 100
_OUTER_SPLIT_ALPHA_MIN_STEPS = 30
_SCOPE_DOT_SCALE_MIN_STEPS = 10
_SCOPE_DOT_SCALE_MIN = 0.1
_SCOPE_DOT_SCALE_MAX = 2.0


def _legacy_v1_to_bytes(s: dict) -> bytearray:
    b = bytearray(18)
    b[1] = 1
    b[2] = int(s["gap"] * 10) & 0xFF
    b[3] = int(s["outline"] * 2) & 0xFF
    b[4] = int(clamp(s["red"], 0, 255))
    b[5] = int(clamp(s["green"], 0, 255))
    b[6] = int(clamp(s["blue"], 0, 255))
    b[7] = int(clamp(s["alpha"], 0, 255))
    b[8] = (int(clamp(s["split_distance"], 0, 7)) & 7) | (int(bool(s["follow_recoil"])) << 7)
    b[9] = int(s["fixed_crosshair_gap"] * 10) & 0xFF
    b[10] = ((int(clamp(s["color"], 0, 7)) & 7)
             | (int(bool(s["outline_enabled"])) << 3)
             | (int(round(s["inner_split_alpha"] * 10)) << 4))
    b[11] = (int(round(s["outer_split_alpha"] * 10)) & 0xF) | (int(round(s["split_size_ratio"] * 10)) << 4)
    b[12] = int(s["thickness"] * 10) & 0xFF
    b[13] = ((int(clamp(s["style"], 0, 7)) << 1)
             | (int(bool(s["center_dot_enabled"])) << 4)
             | (int(bool(s["deployed_weapon_gap_enabled"])) << 5)
             | (int(bool(s["alpha_enabled"])) << 6)
             | (int(bool(s["t_style_enabled"])) << 7))
    b[14] = int(s["length"] * 10) & 0xFF
    return b


def _pixel_crosshair_to_bytes(s: dict, max_style: int) -> bytearray:
    inner = int(round(clamp(s["inner_split_alpha"], 0, 1) * _SPLIT_ALPHA_STEPS_PER_UNIT))
    outer = int(round(clamp(s["outer_split_alpha"], 0.3, 1) * _SPLIT_ALPHA_STEPS_PER_UNIT)) \
        - _LEGACY_OUTER_SPLIT_ALPHA_MIN_STEPS
    ratio = int(round(clamp(s["split_size_ratio"], 0, 1) * _SPLIT_SIZE_RATIO_STEPS_PER_UNIT))
    bits = (int(clamp(s["split_distance"], 0, 127))
            | (inner << 7)
            | (outer << 12)
            | (ratio << 16)
            | (int(clamp(s["thickness"], 0, 31)) << 23)) & 0xFFFFFFFF
    screen_height = int(clamp(s["screen_height"], 0, 65535))
    b = bytearray(18)
    b[2] = (int(clamp(s["style"], 0, max_style))
            | (int(bool(s["follow_recoil"])) << 4)
            | (int(bool(s["center_dot_enabled"])) << 6)
            | (int(bool(s["t_style_enabled"])) << 7)) & 0xFF
    b[3] = int(clamp(s["red"], 0, 255))
    b[4] = int(clamp(s["green"], 0, 255))
    b[5] = int(clamp(s["blue"], 0, 255))
    b[6] = int(clamp(s["alpha"], 0, 255))
    b[7] = int(clamp(s["gap"], 0, 255))
    b[8] = int(clamp(s["length"], 0, 255))
    b[9] = int(clamp(s["dynamic_spread_limit"], 0, 255))
    b[10] = bits & 0xFF
    b[11] = (bits >> 8) & 0xFF
    b[12] = (bits >> 16) & 0xFF
    b[13] = (bits >> 24) & 0xFF
    b[14] = screen_height & 0xFF
    b[15] = (screen_height >> 8) & 0xFF
    return b


def _legacy_v3_to_bytes(s: dict) -> bytearray:
    b = _pixel_crosshair_to_bytes(s, 7)
    b[1] = 3
    b[2] |= int(bool(s["outline_enabled"])) << 5
    return b


def _legacy_v4_to_bytes(s: dict) -> bytearray:
    b = _pixel_crosshair_to_bytes(s, 8)
    b[1] = 4
    b[13] |= int(clamp(s.get("outline_mode", 1), 0, 2)) << 4
    return b


def _cs2_v1_to_bytes(s: dict) -> bytearray:
    inner = int(round(clamp(s["inner_split_alpha"], 0, 1) * _STEPS_PER_UNIT))
    outer = int(round(clamp(s["outer_split_alpha"], 0.3, 1) * _STEPS_PER_UNIT)) \
        - _OUTER_SPLIT_ALPHA_MIN_STEPS
    ratio = int(round(clamp(s["split_size_ratio"], 0, 1) * _STEPS_PER_UNIT))
    bits = (int(clamp(s["split_distance"], 0, 127))
            | (inner << 7)
            | (outer << 14)
            | (ratio << 21)
            | (int(bool(s["scope_dot_use_crosshair_color"])) << 28)) & 0xFFFFFFFF
    screen_height = int(clamp(s["screen_height"], 0, 65535))
    scope_dot_scale = int(round(clamp(s["scope_dot_scale"], _SCOPE_DOT_SCALE_MIN,
                                       _SCOPE_DOT_SCALE_MAX) * _STEPS_PER_UNIT)) \
        - _SCOPE_DOT_SCALE_MIN_STEPS
    gap = int(clamp(s["gap"], -3840, 3840)) & 0xFFFF
    b = bytearray(32)
    b[1] = 1
    b[2] = screen_height & 0xFF
    b[3] = (screen_height >> 8) & 0xFF
    b[4] = (int(clamp(s["style"], 0, 9))
            | (int(bool(s["follow_recoil"])) << 5)
            | (int(bool(s["center_dot_enabled"])) << 6)
            | (int(bool(s["t_style_enabled"])) << 7)) & 0xFF
    b[5] = int(clamp(s["red"], 0, 255))
    b[6] = int(clamp(s["green"], 0, 255))
    b[7] = int(clamp(s["blue"], 0, 255))
    b[8] = int(clamp(s["alpha"], 0, 255))
    b[9] = int(clamp(s["outline_red"], 0, 255))
    b[10] = int(clamp(s["outline_green"], 0, 255))
    b[11] = int(clamp(s["outline_blue"], 0, 255))
    b[12] = int(clamp(s["outline_alpha"], 0, 255))
    b[13] = (int(clamp(s["thickness"], 0, 32)) | (int(clamp(s["outline_mode"], 0, 2)) << 6)) & 0xFF
    b[14] = gap & 0xFF
    b[15] = (gap >> 8) & 0xFF
    b[16] = int(clamp(s["length"], 0, 255))
    b[17] = int(clamp(s["dynamic_spread_limit"], 0, 255))
    b[18] = bits & 0xFF
    b[19] = (bits >> 8) & 0xFF
    b[20] = (bits >> 16) & 0xFF
    b[21] = (bits >> 24) & 0xFF
    b[22] = scope_dot_scale & 0xFF
    return b


_ENCODERS = {
    "legacy-v1": (_legacy_v1_to_bytes, bytes_to_share_code),
    "legacy-v3": (_legacy_v3_to_bytes, bytes_to_share_code),
    "legacy-v4": (_legacy_v4_to_bytes, bytes_to_share_code),
    "cs2-v1": (_cs2_v1_to_bytes, bytes_to_cs2_code),
}


def encode_cs2_crosshair(settings: dict, format: str = "cs2-v1") -> CodecResult:
    """Encode game-native settings to a CS2 share code.

    `format` defaults to the native `cs2-v1`; legacy-v1/v3/v4 remain
    supported. Every field is validated/clamped exactly like the game does.
    """
    format = format or "cs2-v1"
    if format not in ALL_FORMATS:
        return CodecResult(
            success=False, game="cs2", format=format,
            error="Unsupported CS2 format for encoding: %r (supported: %s)"
            % (format, ", ".join(ALL_FORMATS)))
    try:
        obj = settings_from_dict(dict(settings, format=format))
        s = settings_to_dict(obj)
        to_bytes, to_code = _ENCODERS[format]
        raw = to_bytes(s)
        apply_crosshair_checksum(raw)
        code = to_code(bytes(raw))
    except Exception as e:
        return CodecResult(success=False, game="cs2", format=format,
                           error="Encoding failed: %s" % e)

    # verify round-trip through our own decoder
    from crosshair.codecs.cs2.decoder import decode_cs2_crosshair
    check = decode_cs2_crosshair(code)
    warnings = []
    if not check.success:
        warnings.append("Generated code failed validation round-trip: %s" % check.error)
    return CodecResult(success=True, game="cs2", format=format, code=code,
                       settings=s, warnings=warnings,
                       metadata={"container": "cs2" if format == "cs2-v1" else "legacy"})
