"""CS2 crosshair schemas for every supported format.

Field names and semantics mirror the verified `csgo-sharecode@7.0.1` types
(`CrosshairLegacyV1`, `CrosshairLegacyV3`, `CrosshairLegacyV4`, `CrosshairV1`).
Do not rename fields: they map 1:1 to the ConVars the game writes on import.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

LEGACY_FORMATS = ("legacy-v1", "legacy-v3", "legacy-v4")
CS2_FORMATS = ("cs2-v1",)
ALL_FORMATS = LEGACY_FORMATS + CS2_FORMATS


@dataclass
class CrosshairLegacyV1:
    """CS:GO era code (legacy container, version byte 1)."""

    format: str = "legacy-v1"
    length: float = 3.0
    red: int = 50
    green: int = 250
    blue: int = 50
    gap: float = 1.0
    alpha_enabled: bool = False
    alpha: int = 200
    outline_enabled: bool = False
    outline: float = 1.0
    color: int = 1
    thickness: float = 0.5
    center_dot_enabled: bool = False
    split_distance: int = 7
    follow_recoil: bool = False
    fixed_crosshair_gap: float = 3.0
    inner_split_alpha: float = 1.0
    outer_split_alpha: float = 0.5
    split_size_ratio: float = 0.3
    t_style_enabled: bool = False
    deployed_weapon_gap_enabled: bool = False
    # CS2 style meaning: 0-3 classic, 4 classic static, 5 legacy
    style: int = 4


@dataclass
class CrosshairLegacyV3:
    """CS2 legacy container, version byte 3 (pixel values + screen height)."""

    format: str = "legacy-v3"
    style: int = 4
    follow_recoil: bool = False
    outline_enabled: bool = True
    center_dot_enabled: bool = False
    t_style_enabled: bool = False
    red: int = 50
    green: int = 250
    blue: int = 50
    alpha: int = 255
    gap: int = 4
    length: int = 8
    thickness: int = 2
    dynamic_spread_limit: int = 255
    split_distance: int = 7
    inner_split_alpha: float = 1.0
    outer_split_alpha: float = 0.45
    split_size_ratio: float = 0.3
    screen_height: int = 1080


@dataclass
class CrosshairLegacyV4(CrosshairLegacyV3):
    """CS2 legacy container, version byte 4 (adds outlineMode, style 8)."""

    format: str = "legacy-v4"
    outline_mode: int = 1  # 0 none, 1 full, 2 half


@dataclass
class CrosshairCs2V1:
    """Native CS2 code (CS container, version byte 1).

    Adds outline RGBA, scope dot preferences, negative gap, 0.01-step split
    alphas and the Static Quad style (9).
    """

    format: str = "cs2-v1"
    style: int = 4
    follow_recoil: bool = False
    center_dot_enabled: bool = False
    t_style_enabled: bool = False
    outline_mode: int = 1  # 0 none, 1 full, 2 half
    red: int = 50
    green: int = 250
    blue: int = 50
    alpha: int = 255
    outline_red: int = 0
    outline_green: int = 0
    outline_blue: int = 0
    outline_alpha: int = 255
    gap: int = 4  # -3840..3840, signed 16-bit
    length: int = 8  # 0..255
    thickness: int = 2  # 0..32
    dynamic_spread_limit: int = 255  # 0..255
    split_distance: int = 7  # 0..127
    inner_split_alpha: float = 1.0  # 0..1, 0.01 steps
    outer_split_alpha: float = 0.45  # 0.3..1, 0.01 steps
    split_size_ratio: float = 0.3  # 0..1, 0.01 steps
    screen_height: int = 1080  # 0..65535, 0 rejected, min applied 240
    scope_dot_scale: float = 1.0  # 0.1..2, 0.01 steps
    scope_dot_use_crosshair_color: bool = False


FORMAT_CLASSES = {
    "legacy-v1": CrosshairLegacyV1,
    "legacy-v3": CrosshairLegacyV3,
    "legacy-v4": CrosshairLegacyV4,
    "cs2-v1": CrosshairCs2V1,
}


def settings_from_dict(data: dict) -> object:
    """Build the dataclass for `data['format']` from a plain dict."""
    fmt = data.get("format", "cs2-v1")
    if fmt not in FORMAT_CLASSES:
        raise ValueError("Unsupported CS2 format: %r" % fmt)
    cls = FORMAT_CLASSES[fmt]
    valid = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
    kwargs = {k: v for k, v in data.items() if k in valid}
    return cls(**kwargs)


def settings_to_dict(obj) -> dict:
    return asdict(obj)
