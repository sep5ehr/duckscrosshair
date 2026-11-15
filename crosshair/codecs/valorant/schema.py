"""VALORANT crosshair profile schema.

Key map verified against a working open-source generator/parser
(genesy/crosshair-codes) and cross-checked with faheem-s27/ValorantCrosshairParser:

- Header (no section): `c` = override all crosshairs with primary,
  `s;1` = advanced options enabled, `p;0` = ADS does not copy primary,
  `NAME;"..."` = profile name.
- Primary (P) / ADS (A) sections:
    c color preset (0-7 presets, 8 = custom), u custom color hex (RRGGBB[FF]),
    h outline enabled, t outline thickness, o outline opacity,
    d center dot enabled, z center dot thickness, a center dot opacity,
    m override firing-error offset with crosshair offset,
    f fade crosshair with firing error, s follow spectating target.
  Line settings are prefixed `0` (inner) / `1` (outer):
    b show, a opacity, l length, v vertical length, g length not linked,
    t thickness, o offset, m movement error, s movement error multiplier,
    f firing error, e firing error multiplier.
- Sniper (S) section: d show, c color preset, t custom color, s thickness,
  o opacity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Preset color index -> hex (verified PresetColors enum)
PRESET_COLORS = {
    0: "#FFFFFF",  # White
    1: "#00FF00",  # Green
    2: "#7FFF00",  # Yellow Green
    3: "#DFFF00",  # Green Yellow
    4: "#FFFF00",  # Yellow
    5: "#00FFFF",  # Cyan
    6: "#FF00FF",  # Pink
    7: "#FF0000",  # Red
}
CUSTOM_COLOR_INDEX = 8

SECTION_NAMES = {"P": "primary", "A": "ads", "S": "sniper"}


@dataclass
class LineSettings:
    show: bool = True
    opacity: float = 0.8
    length: int = 6
    vertical_length: int = 6
    length_linked: bool = False
    thickness: int = 2
    offset: int = 3
    movement_error: bool = False
    movement_error_multiplier: float = 1.0
    firing_error: bool = True
    firing_error_multiplier: float = 1.0


@dataclass
class DotSettings:
    enabled: bool = False
    thickness: int = 2
    opacity: float = 1.0


@dataclass
class OutlineSettings:
    enabled: bool = True
    thickness: int = 1
    opacity: float = 0.5


@dataclass
class GunCrosshairSection:
    """Primary or ADS section."""

    color_preset: int = 0
    custom_color: Optional[str] = None  # hex without '#', RRGGBB or RRGGBBFF
    outline: OutlineSettings = field(default_factory=OutlineSettings)
    center_dot: DotSettings = field(default_factory=DotSettings)
    override_firing_error_offset: bool = False   # m
    fade_with_firing_error: Optional[bool] = None  # f
    follow_spectating: Optional[bool] = None       # s
    inner_lines: LineSettings = field(default_factory=lambda: LineSettings(
        show=True, opacity=0.8, length=6, vertical_length=6, thickness=2, offset=3,
        movement_error=False, movement_error_multiplier=1.0,
        firing_error=True, firing_error_multiplier=1.0))
    outer_lines: LineSettings = field(default_factory=lambda: LineSettings(
        show=True, opacity=0.35, length=2, vertical_length=2, thickness=2, offset=10,
        movement_error=True, movement_error_multiplier=1.0,
        firing_error=True, firing_error_multiplier=1.0))


@dataclass
class SniperSection:
    show: bool = True
    color_preset: int = 7
    custom_color: Optional[str] = None
    thickness: float = 1.0   # s
    opacity: float = 0.8     # o


@dataclass
class ValorantProfile:
    version: str = "0"
    override_all_with_primary: bool = False      # header c;1
    advanced_options: bool = False               # header s;1
    ads_copy_primary: bool = True                # header p;0 disables
    name: Optional[str] = None                   # NAME;"..."
    primary: GunCrosshairSection = field(default_factory=GunCrosshairSection)
    ads: GunCrosshairSection = field(default_factory=GunCrosshairSection)
    sniper: SniperSection = field(default_factory=SniperSection)

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ValorantProfile":
        import dataclasses
        def build(subcls, value):
            if not isinstance(value, dict):
                return subcls()
            valid = {f for f in subcls.__dataclass_fields__}
            return subcls(**{k: v for k, v in value.items() if k in valid})
        nested = {}
        for fname, subcls in (("primary", GunCrosshairSection), ("ads", GunCrosshairSection),
                              ("sniper", SniperSection)):
            nested[fname] = build(subcls, data.get(fname))
        for fname in ("outline", "center_dot", "inner_lines", "outer_lines"):
            pass
        # rebuild nested line/dot/outline objects
        for sec_name in ("primary", "ads"):
            sec = nested[sec_name]
            for fname, subcls in (("outline", OutlineSettings), ("center_dot", DotSettings),
                                  ("inner_lines", LineSettings), ("outer_lines", LineSettings)):
                raw = (data.get(sec_name) or {}).get(fname)
                if isinstance(raw, dict):
                    valid = {f for f in subcls.__dataclass_fields__}
                    setattr(sec, fname, subcls(**{k: v for k, v in raw.items() if k in valid}))
        valid = {f for f in cls.__dataclass_fields__}
        kwargs = {k: v for k, v in data.items() if k in valid and k not in nested}
        kwargs.update(nested)
        return cls(**kwargs)
