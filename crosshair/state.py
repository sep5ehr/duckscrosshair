"""Application state management."""

from dataclasses import dataclass, field
from typing import Optional
from crosshair.models import AppSettings, CrosshairSettings, OverlaySettings, ShortcutSettings


@dataclass
class AppState:
    """Central application state."""
    settings: AppSettings = field(default_factory=AppSettings)
    overlay_visible: bool = True
    settings_window_visible: bool = False

    # Runtime references (not serialized)
    overlay_window: Optional[object] = None
    settings_window: Optional[object] = None
    tray_icon: Optional[object] = None
    monitor_manager: Optional[object] = None

    def get_crosshair_settings(self) -> CrosshairSettings:
        return self.settings.crosshair

    def get_overlay_settings(self) -> OverlaySettings:
        return self.settings.overlay

    def get_shortcuts(self) -> ShortcutSettings:
        return self.settings.shortcuts