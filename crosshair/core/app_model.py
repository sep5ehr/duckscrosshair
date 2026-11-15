"""Bridge between the universal crosshair model and the app's CrosshairSettings."""

from __future__ import annotations

from crosshair.core.universal import UniversalCrosshair
from crosshair.models import CrosshairSettings


def universal_to_app(u: UniversalCrosshair) -> CrosshairSettings:
    """Map a universal model onto the existing app settings (overlay renderer)."""
    s = CrosshairSettings()
    s.color = u.color
    s.opacity = u.alpha
    s.scale = float(getattr(u, "scale", 1.0) or 1.0)
    s.gap = int(round(u.inner_lines.offset))
    s.length = int(round(u.inner_lines.length))
    s.thickness = max(1, int(round(u.inner_lines.thickness)))
    s.size = max(1, int(round(u.center_dot.size)))
    s.outline_enabled = u.outline.enabled
    s.outline_color = u.outline.color
    s.outline_thickness = max(0, int(round(u.outline.thickness)))
    s.center_dot = u.center_dot.enabled
    ext = u.game_extensions.get("cs2", {})
    s.t_style = bool(ext.get("t_style_enabled", False))
    s.style = int(ext.get("style", 4))
    s.dynamic_spread_limit = float(ext.get("dynamic_spread_limit", 0.0)) / 255.0 \
        if ext.get("dynamic_spread_limit") is not None else 0.0
    s.split_distance = int(u.outer_lines.offset) if u.outer_lines.enabled else 0
    s.inner_split_alpha = int(round(ext.get("inner_split_alpha", 1.0) * 255))
    s.outer_split_alpha = int(round(ext.get("outer_split_alpha", 1.0) * 255))
    s.split_size_ratio = float(ext.get("split_size_ratio", 0.5))
    s.reference_resolution = int(ext.get("screen_height", 1920))
    s.scope_dot_scale = float(ext.get("scope_dot_scale", 1.0))
    s.scope_dot_use_crosshair_color = bool(ext.get("scope_dot_use_crosshair_color", False))
    return s


def app_to_universal(s: CrosshairSettings, game: str = "cs2") -> UniversalCrosshair:
    """Map the app's current settings to a universal model for encoding."""
    u = UniversalCrosshair(game=game)
    u.color = s.color
    u.alpha = s.opacity
    u.scale = float(getattr(s, "scale", 1.0) or 1.0)
    u.inner_lines.offset = s.gap
    u.inner_lines.length = s.length
    u.inner_lines.thickness = s.thickness
    u.inner_lines.opacity = s.opacity
    u.outer_lines.enabled = s.split_distance > 0
    u.outer_lines.offset = s.split_distance
    u.center_dot.enabled = s.center_dot
    u.center_dot.size = s.size
    u.center_dot.opacity = s.opacity
    u.outline.enabled = s.outline_enabled
    u.outline.color = s.outline_color
    u.outline.thickness = s.outline_thickness
    u.game_extensions["cs2"] = {
        "style": s.style,
        "t_style_enabled": s.t_style,
        "dynamic_spread_limit": int(round(s.dynamic_spread_limit * 255)),
        "inner_split_alpha": s.inner_split_alpha / 255.0,
        "outer_split_alpha": s.outer_split_alpha / 255.0,
        "split_size_ratio": s.split_size_ratio,
        "screen_height": s.reference_resolution,
        "scope_dot_scale": s.scope_dot_scale,
        "scope_dot_use_crosshair_color": s.scope_dot_use_crosshair_color,
    }
    return u
