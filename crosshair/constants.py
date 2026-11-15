"""Application constants and default values."""

from dataclasses import dataclass
from typing import Final

# Application metadata
APP_NAME: Final[str] = "DucksCrosshair"
APP_VERSION: Final[str] = "1.0.0"
ORG_NAME: Final[str] = "DucksCrosshair"

# Settings file
SETTINGS_DIR_NAME: Final[str] = "DucksCrosshair"
SETTINGS_FILE_NAME: Final[str] = "settings.json"
SETTINGS_SCHEMA_VERSION: Final[int] = 1

# Default crosshair settings
@dataclass(frozen=True)
class DefaultCrosshair:
    gap: int = 2
    length: int = 6
    thickness: int = 2
    size: int = 6
    color: str = "#00FF00"
    opacity: float = 1.0
    outline_enabled: bool = True
    outline_color: str = "#000000"
    outline_thickness: int = 1
    center_dot: bool = False
    t_style: bool = False
    style: int = 4  # CS2 style: 4 = classic static
    dynamic_spread_limit: float = 0.0
    split_distance: int = 7
    inner_split_alpha: int = 255
    outer_split_alpha: int = 255
    split_size_ratio: float = 0.5
    reference_resolution: int = 1920
    scope_dot_scale: float = 1.0
    scope_dot_use_crosshair_color: bool = False


# Default overlay settings
@dataclass(frozen=True)
class DefaultOverlay:
    enabled: bool = True
    click_through: bool = True
    always_on_top: bool = True
    monitor_id: str = "primary"
    opacity: float = 1.0


# Default shortcuts
@dataclass(frozen=True)
class DefaultShortcuts:
    toggle_overlay: str = "F8"
    toggle_settings: str = "F9"


# Validation ranges
VALIDATION_RANGES: Final[dict] = {
    "gap": (0, 50),
    "length": (0, 100),
    "thickness": (1, 20),
    "size": (0, 50),
    "opacity": (0.0, 1.0),
    "outline_thickness": (0, 10),
    "dynamic_spread_limit": (0.0, 1.0),
    "split_distance": (0, 100),
    "inner_split_alpha": (0, 255),
    "outer_split_alpha": (0, 255),
    "split_size_ratio": (0.0, 1.0),
    "reference_resolution": (640, 7680),
    "scope_dot_scale": (0.0, 10.0),
    "style": (0, 5),
}

# CS2 Share code alphabet (base32 variant)
CS2_ALPHABET: Final[str] = "ABCDEFGHJKLMNOPQRSTUVWXYZ234567"
CS2_ALPHABET_MAP: Final[dict] = {c: i for i, c in enumerate(CS2_ALPHABET)}

# Preview backgrounds
PREVIEW_BACKGROUNDS: Final[list] = ["light", "dark", "checkerboard"]

# Monitor refresh interval (ms)
MONITOR_REFRESH_INTERVAL: Final[int] = 2000

# Settings debounce (ms)
SETTINGS_DEBOUNCE_MS: Final[int] = 500