"""Platform-specific functionality."""

from winplatform.hotkeys import (
    HotkeyManager,
    Hotkey,
    get_hotkey_manager,
    cleanup_hotkeys,
)

__all__ = [
    "HotkeyManager",
    "Hotkey",
    "get_hotkey_manager",
    "cleanup_hotkeys",
]
