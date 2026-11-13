"""Global hotkey management for Windows."""

import logging
import sys
from typing import Callable, Dict, Optional
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal, QAbstractNativeEventFilter, QByteArray
from PySide6.QtGui import QKeySequence, Qt

logger = logging.getLogger(__name__)

# Windows messages
WM_HOTKEY = 0x0312

# Virtual key codes
VK_F1 = 0x70
VK_F2 = 0x71
VK_F3 = 0x72
VK_F4 = 0x73
VK_F5 = 0x74
VK_F6 = 0x75
VK_F7 = 0x76
VK_F8 = 0x77
VK_F9 = 0x78
VK_F10 = 0x79
VK_F11 = 0x7A
VK_F12 = 0x7B
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_BACK = 0x08
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_LWIN = 0x5B
VK_RWIN = 0x5C

# Modifier flags
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000


@dataclass
class Hotkey:
    """Represents a registered hotkey."""
    id: int
    key: int
    modifiers: int
    callback: Callable
    description: str = ""


class HotkeyFilter(QAbstractNativeEventFilter):
    """Native event filter for Windows hotkey messages."""

    def __init__(self, hotkey_manager: 'HotkeyManager'):
        super().__init__()
        self.hotkey_manager = hotkey_manager

    def nativeEventFilter(self, eventType: QByteArray, message) -> tuple[bool, int]:
        """Filter native Windows messages for hotkeys."""
        if sys.platform != "win32":
            return False, 0

        try:
            # message is a pointer to MSG structure (as integer or VoidPtr)
            from ctypes import wintypes, windll, c_void_p, cast, POINTER

            MSG = wintypes.MSG
            # Convert message to integer if it's a VoidPtr
            if hasattr(message, '__int__'):
                message_int = int(message)
            else:
                message_int = message
            msg_ptr = cast(c_void_p(message_int), POINTER(MSG))
            msg = msg_ptr.contents

            if msg.message == WM_HOTKEY:
                hotkey_id = msg.wParam
                self.hotkey_manager._handle_hotkey(hotkey_id)
                return True, 0
        except Exception as e:
            logger.error(f"Error in hotkey filter: {e}")

        return False, 0


class HotkeyManager(QObject):
    """Manages global hotkeys on Windows."""

    hotkey_triggered = Signal(int)  # hotkey_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hotkeys: Dict[int, Hotkey] = {}
        self._next_id = 1
        self._filter = HotkeyFilter(self)
        self._registered = False

        # Install native event filter
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.instance().installNativeEventFilter(self._filter)

    def parse_hotkey_string(self, hotkey_str: str) -> tuple[int, int]:
        """
        Parse a hotkey string like "F8", "Ctrl+Shift+F9", "Alt+Space".

        Returns:
            (virtual_key, modifiers)
        """
        hotkey_str = hotkey_str.strip().upper()
        parts = [p.strip() for p in hotkey_str.split("+")]

        modifiers = 0
        key = 0

        for part in parts:
            if part == "CTRL" or part == "CONTROL":
                modifiers |= MOD_CONTROL
            elif part == "ALT":
                modifiers |= MOD_ALT
            elif part == "SHIFT":
                modifiers |= MOD_SHIFT
            elif part == "WIN" or part == "WINDOWS":
                modifiers |= MOD_WIN
            else:
                # Key
                key = self._parse_key(part)

        return key, modifiers

    def _parse_key(self, key_str: str) -> int:
        """Parse a key string to virtual key code."""
        key_map = {
            "F1": VK_F1, "F2": VK_F2, "F3": VK_F3, "F4": VK_F4,
            "F5": VK_F5, "F6": VK_F6, "F7": VK_F7, "F8": VK_F8,
            "F9": VK_F9, "F10": VK_F10, "F11": VK_F11, "F12": VK_F12,
            "ESC": VK_ESCAPE, "ESCAPE": VK_ESCAPE,
            "SPACE": VK_SPACE,
            "TAB": VK_TAB,
            "ENTER": VK_RETURN, "RETURN": VK_RETURN,
            "BACKSPACE": VK_BACK, "BACK": VK_BACK,
            "SHIFT": VK_SHIFT,
            "CTRL": VK_CONTROL, "CONTROL": VK_CONTROL,
            "ALT": VK_MENU,
            "WIN": VK_LWIN, "WINDOWS": VK_LWIN,
        }

        # Check for single letter/number keys
        if len(key_str) == 1 and key_str.isalnum():
            return ord(key_str)

        return key_map.get(key_str, 0)

    def register_hotkey(self, hotkey_str: str, callback: Callable, description: str = "") -> Optional[int]:
        """
        Register a global hotkey.

        Args:
            hotkey_str: String like "F8", "Ctrl+F9"
            callback: Function to call when hotkey is triggered
            description: Human-readable description

        Returns:
            Hotkey ID if successful, None if failed
        """
        if sys.platform != "win32":
            logger.warning("Global hotkeys only supported on Windows")
            return None

        key, modifiers = self.parse_hotkey_string(hotkey_str)
        if key == 0:
            logger.error(f"Invalid hotkey: {hotkey_str}")
            return None

        hotkey_id = self._next_id
        self._next_id += 1

        try:
            from ctypes import windll
            result = windll.user32.RegisterHotKey(None, hotkey_id, modifiers, key)
            if result == 0:
                error = windll.kernel32.GetLastError()
                logger.error(f"Failed to register hotkey {hotkey_str} (id={hotkey_id}): error {error}")
                return None

            hotkey = Hotkey(
                id=hotkey_id,
                key=key,
                modifiers=modifiers,
                callback=callback,
                description=description or hotkey_str
            )
            self._hotkeys[hotkey_id] = hotkey
            self._registered = True
            logger.info(f"Registered hotkey: {hotkey_str} (id={hotkey_id})")
            return hotkey_id

        except Exception as e:
            logger.error(f"Exception registering hotkey {hotkey_str}: {e}")
            return None

    def unregister_hotkey(self, hotkey_id: int) -> bool:
        """Unregister a hotkey by ID."""
        if sys.platform != "win32":
            return False

        if hotkey_id not in self._hotkeys:
            return False

        try:
            from ctypes import windll
            result = windll.user32.UnregisterHotKey(None, hotkey_id)
            if result:
                del self._hotkeys[hotkey_id]
                logger.info(f"Unregistered hotkey id={hotkey_id}")
                return True
            else:
                logger.error(f"Failed to unregister hotkey id={hotkey_id}")
                return False
        except Exception as e:
            logger.error(f"Exception unregistering hotkey id={hotkey_id}: {e}")
            return False

    def unregister_all(self):
        """Unregister all hotkeys."""
        for hotkey_id in list(self._hotkeys.keys()):
            self.unregister_hotkey(hotkey_id)
        self._hotkeys.clear()
        self._registered = False

    def _handle_hotkey(self, hotkey_id: int):
        """Handle triggered hotkey."""
        hotkey = self._hotkeys.get(hotkey_id)
        if hotkey:
            logger.debug(f"Hotkey triggered: {hotkey.description} (id={hotkey_id})")
            try:
                hotkey.callback()
            except Exception as e:
                logger.error(f"Error in hotkey callback: {e}")
            self.hotkey_triggered.emit(hotkey_id)

    def get_registered_hotkeys(self) -> Dict[int, Hotkey]:
        """Get all registered hotkeys."""
        return self._hotkeys.copy()

    def check_conflicts(self, hotkey_str: str) -> list[str]:
        """Check for conflicts with existing hotkeys."""
        key, modifiers = self.parse_hotkey_string(hotkey_str)
        conflicts = []

        for hk in self._hotkeys.values():
            if hk.key == key and hk.modifiers == modifiers:
                conflicts.append(hk.description)

        return conflicts


# Global instance
_hotkey_manager: Optional[HotkeyManager] = None


def get_hotkey_manager() -> HotkeyManager:
    """Get or create the global hotkey manager."""
    global _hotkey_manager
    if _hotkey_manager is None:
        _hotkey_manager = HotkeyManager()
    return _hotkey_manager


def cleanup_hotkeys():
    """Clean up global hotkeys on exit."""
    global _hotkey_manager
    if _hotkey_manager:
        _hotkey_manager.unregister_all()
        _hotkey_manager = None