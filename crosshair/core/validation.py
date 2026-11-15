"""Validation helpers for game-native settings dicts (range clamping)."""

from __future__ import annotations

RANGES = {
    "red": (0, 255), "green": (0, 255), "blue": (0, 255), "alpha": (0, 255),
    "outline_red": (0, 255), "outline_green": (0, 255), "outline_blue": (0, 255),
    "outline_alpha": (0, 255),
    "gap": (-3840, 3840), "length": (0, 255), "thickness": (0, 32),
    "dynamic_spread_limit": (0, 255), "split_distance": (0, 127),
    "screen_height": (240, 65535), "style": (0, 9), "outline_mode": (0, 2),
    "color": (0, 7),
}


def clamp_settings(settings: dict, ranges: dict = None) -> tuple:
    """Clamp numeric settings into range. Returns (settings, clamped_keys)."""
    ranges = ranges or RANGES
    clamped = []
    out = dict(settings)
    for key, (lo, hi) in ranges.items():
        if key in out and isinstance(out[key], (int, float)) and not isinstance(out[key], bool):
            v = out[key]
            if v < lo or v > hi:
                out[key] = max(lo, min(hi, v))
                clamped.append(key)
    return out, clamped
