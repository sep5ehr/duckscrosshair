"""Crosshair data models for internal rendering and CS2 share codes."""

from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class CrosshairSettings:
    """Internal crosshair model for the standalone overlay renderer."""

    # Core appearance
    gap: int = 2
    length: int = 6
    thickness: int = 2
    size: int = 6
    color: str = "#00FF00"
    opacity: float = 1.0
    scale: float = 1.0  # global size multiplier for the whole crosshair

    # Outline
    outline_enabled: bool = True
    outline_color: str = "#000000"
    outline_thickness: int = 1

    # Special styles
    center_dot: bool = False
    t_style: bool = False

    # CS2-specific fields (stored for share-code round-trip)
    style: int = 4
    dynamic_spread_limit: float = 0.0
    split_distance: int = 7
    inner_split_alpha: int = 255
    outer_split_alpha: int = 255
    split_size_ratio: float = 0.5
    reference_resolution: int = 1920
    scope_dot_scale: float = 1.0
    scope_dot_use_crosshair_color: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "gap": self.gap,
            "length": self.length,
            "thickness": self.thickness,
            "size": self.size,
            "color": self.color,
            "opacity": self.opacity,
            "scale": self.scale,
            "outline_enabled": self.outline_enabled,
            "outline_color": self.outline_color,
            "outline_thickness": self.outline_thickness,
            "center_dot": self.center_dot,
            "t_style": self.t_style,
            "style": self.style,
            "dynamic_spread_limit": self.dynamic_spread_limit,
            "split_distance": self.split_distance,
            "inner_split_alpha": self.inner_split_alpha,
            "outer_split_alpha": self.outer_split_alpha,
            "split_size_ratio": self.split_size_ratio,
            "reference_resolution": self.reference_resolution,
            "scope_dot_scale": self.scope_dot_scale,
            "scope_dot_use_crosshair_color": self.scope_dot_use_crosshair_color,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CrosshairSettings":
        """Create from dictionary with defaults for missing keys."""
        defaults = cls()
        return cls(
            gap=data.get("gap", defaults.gap),
            length=data.get("length", defaults.length),
            thickness=data.get("thickness", defaults.thickness),
            size=data.get("size", defaults.size),
            color=data.get("color", defaults.color),
            opacity=data.get("opacity", defaults.opacity),
            scale=data.get("scale", defaults.scale),
            outline_enabled=data.get("outline_enabled", defaults.outline_enabled),
            outline_color=data.get("outline_color", defaults.outline_color),
            outline_thickness=data.get("outline_thickness", defaults.outline_thickness),
            center_dot=data.get("center_dot", defaults.center_dot),
            t_style=data.get("t_style", defaults.t_style),
            style=data.get("style", defaults.style),
            dynamic_spread_limit=data.get("dynamic_spread_limit", defaults.dynamic_spread_limit),
            split_distance=data.get("split_distance", defaults.split_distance),
            inner_split_alpha=data.get("inner_split_alpha", defaults.inner_split_alpha),
            outer_split_alpha=data.get("outer_split_alpha", defaults.outer_split_alpha),
            split_size_ratio=data.get("split_size_ratio", defaults.split_size_ratio),
            reference_resolution=data.get("reference_resolution", defaults.reference_resolution),
            scope_dot_scale=data.get("scope_dot_scale", defaults.scope_dot_scale),
            scope_dot_use_crosshair_color=data.get("scope_dot_use_crosshair_color", defaults.scope_dot_use_crosshair_color),
        )

    def copy(self) -> "CrosshairSettings":
        """Create a deep copy."""
        return CrosshairSettings.from_dict(self.to_dict())


@dataclass
class OverlaySettings:
    """Overlay window settings."""

    enabled: bool = True
    click_through: bool = True
    always_on_top: bool = True
    monitor_id: str = "primary"
    opacity: float = 1.0

    def to_dict(self) -> dict:
        return {
            "enabled": self.enabled,
            "click_through": self.click_through,
            "always_on_top": self.always_on_top,
            "monitor_id": self.monitor_id,
            "opacity": self.opacity,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OverlaySettings":
        defaults = cls()
        return cls(
            enabled=data.get("enabled", defaults.enabled),
            click_through=data.get("click_through", defaults.click_through),
            always_on_top=data.get("always_on_top", defaults.always_on_top),
            monitor_id=data.get("monitor_id", defaults.monitor_id),
            opacity=data.get("opacity", defaults.opacity),
        )


@dataclass
class ShortcutSettings:
    """Keyboard shortcut settings."""

    toggle_overlay: str = "F8"
    toggle_settings: str = "F9"
    force_close: str = "Ctrl+Shift+Q"

    def to_dict(self) -> dict:
        return {
            "toggle_overlay": self.toggle_overlay,
            "toggle_settings": self.toggle_settings,
            "force_close": self.force_close,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ShortcutSettings":
        defaults = cls()
        return cls(
            toggle_overlay=data.get("toggle_overlay", defaults.toggle_overlay),
            toggle_settings=data.get("toggle_settings", defaults.toggle_settings),
            force_close=data.get("force_close", defaults.force_close),
        )


@dataclass
class AppSettings:
    """Complete application settings."""

    schema_version: int = 1
    overlay: OverlaySettings = field(default_factory=OverlaySettings)
    crosshair: CrosshairSettings = field(default_factory=CrosshairSettings)
    shortcuts: ShortcutSettings = field(default_factory=ShortcutSettings)
    last_share_code: str = ""
    # multi-game support (optional, defaulted: old settings files keep working)
    selected_game: str = "cs2"
    selected_format: str = ""
    last_codes: dict = field(default_factory=dict)  # game -> last used code
    # user-saved crosshair presets built in the app: [{"name": str, "settings": {...}}]
    saved_crosshairs: list = field(default_factory=list)
    preview_background: str = "checkerboard"

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "overlay": self.overlay.to_dict(),
            "crosshair": self.crosshair.to_dict(),
            "shortcuts": self.shortcuts.to_dict(),
            "last_share_code": self.last_share_code,
            "selected_game": self.selected_game,
            "selected_format": self.selected_format,
            "last_codes": dict(self.last_codes),
            "saved_crosshairs": [dict(e) for e in self.saved_crosshairs],
            "preview_background": self.preview_background,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        return cls(
            schema_version=data.get("schema_version", 1),
            overlay=OverlaySettings.from_dict(data.get("overlay", {})),
            crosshair=CrosshairSettings.from_dict(data.get("crosshair", {})),
            shortcuts=ShortcutSettings.from_dict(data.get("shortcuts", {})),
            last_share_code=data.get("last_share_code", ""),
            selected_game=data.get("selected_game", "cs2"),
            selected_format=data.get("selected_format", ""),
            last_codes=dict(data.get("last_codes", {})),
            saved_crosshairs=list(data.get("saved_crosshairs", [])),
            preview_background=data.get("preview_background", "checkerboard"),
        )