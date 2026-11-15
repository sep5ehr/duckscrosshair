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
VK_XBUTTON1 = 0x05
VK_XBUTTON2 = 0x06
# Navigation / system keys
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_HOME = 0x24
VK_END = 0x23
VK_PRIOR = 0x21  # Page Up
VK_NEXT = 0x22   # Page Down
VK_INSERT = 0x2D
VK_DELETE = 0x2E
VK_SNAPSHOT = 0x2C  # Print Screen
VK_SCROLL = 0x91
VK_PAUSE = 0x13
VK_NUMPAD0 = 0x60
VK_OEM_MINUS = 0xBD
VK_OEM_PLUS = 0xBB

# Low-level mouse hook (mouse buttons cannot be registered via RegisterHotKey)
WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207
WM_XBUTTONDOWN = 0x020B
WM_MOUSEWHEEL = 0x020A

MOUSE_BUTTON_NAMES = {
    "MOUSELEFT": "MouseLeft", "MB1": "MouseLeft", "LBUTTON": "MouseLeft",
    "MOUSERIGHT": "MouseRight", "MB2": "MouseRight", "RBUTTON": "MouseRight",
    "MOUSEMIDDLE": "MouseMiddle", "MB3": "MouseMiddle", "MBUTTON": "MouseMiddle",
    "MOUSEX1": "MouseX1", "MOUSE4": "MouseX1", "XBUTTON1": "MouseX1",
    "MOUSEX2": "MouseX2", "MOUSE5": "MouseX2", "XBUTTON2": "MouseX2",
}
MOUSE_BUTTON_VK = {
    "MouseLeft": 0x01, "MouseRight": 0x02, "MouseMiddle": 0x04,
    "MouseX1": VK_XBUTTON1, "MouseX2": VK_XBUTTON2,
}

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
    mouse_hotkey_triggered = Signal(int)  # hotkey_id (emitted from the mouse hook thread)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hotkeys: Dict[int, Hotkey] = {}
        self._mouse_hotkeys: Dict[tuple, int] = {}  # (button_name, modifiers) -> hotkey_id
        self._next_id = 1
        self._filter = HotkeyFilter(self)
        self._registered = False
        self._mouse_hook_handle = None
        self._mouse_hook_proc = None
        self._mouse_hook_thread = None
        self._mouse_hook_thread_id = None
        self.mouse_hotkey_triggered.connect(self._handle_hotkey)

        # Install native event filter
        from PySide6.QtCore import QCoreApplication
        QCoreApplication.instance().installNativeEventFilter(self._filter)

    def parse_hotkey_string(self, hotkey_str: str) -> tuple[int, int]:
        """Parse "F8", "Ctrl+Shift+F9", "Alt+Space". Returns (virtual_key, modifiers)."""
        key, modifiers, _mouse = self.parse_hotkey_string_ex(hotkey_str)
        return key, modifiers

    def parse_hotkey_string_ex(self, hotkey_str: str) -> tuple[int, int, Optional[str]]:
        """
        Parse a hotkey string like "F8", "Ctrl+MouseLeft", "Mouse4".

        Returns:
            (virtual_key, modifiers, mouse_button_name or None)
        """
        hotkey_str = hotkey_str.strip().upper()
        parts = [p.strip() for p in hotkey_str.split("+") if p.strip()]

        modifiers = 0
        key = 0
        mouse_button = None

        for part in parts:
            if part in ("CTRL", "CONTROL"):
                modifiers |= MOD_CONTROL
            elif part == "ALT":
                modifiers |= MOD_ALT
            elif part == "SHIFT":
                modifiers |= MOD_SHIFT
            elif part in ("WIN", "WINDOWS"):
                modifiers |= MOD_WIN
            else:
                mouse = MOUSE_BUTTON_NAMES.get(part)
                if mouse:
                    mouse_button = mouse
                else:
                    key = self._parse_key(part)

        return key, modifiers, mouse_button

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
            "LEFT": VK_LEFT, "UP": VK_UP, "RIGHT": VK_RIGHT, "DOWN": VK_DOWN,
            "HOME": VK_HOME, "END": VK_END,
            "PAGEUP": VK_PRIOR, "PGUP": VK_PRIOR,
            "PAGEDOWN": VK_NEXT, "PGDN": VK_NEXT,
            "INSERT": VK_INSERT, "INS": VK_INSERT,
            "DELETE": VK_DELETE, "DEL": VK_DELETE,
            "PRINTSCREEN": VK_SNAPSHOT, "PRTSC": VK_SNAPSHOT,
            "SCROLLLOCK": VK_SCROLL, "PAUSE": VK_PAUSE,
            "MINUS": VK_OEM_MINUS, "EQUAL": VK_OEM_PLUS, "PLUS": VK_OEM_PLUS,
        }
        for i in range(10):
            key_map["NUM%d" % i] = VK_NUMPAD0 + i
            key_map["NUMPAD%d" % i] = VK_NUMPAD0 + i

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

        key, modifiers, mouse_button = self.parse_hotkey_string_ex(hotkey_str)
        if mouse_button:
            return self._register_mouse_hotkey(hotkey_str, mouse_button, modifiers, callback, description)
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
            if hotkey_id in self._hotkeys:
                del self._hotkeys[hotkey_id]
            for combo, hid in list(self._mouse_hotkeys.items()):
                if hid == hotkey_id:
                    del self._mouse_hotkeys[combo]
            return True

        if hotkey_id not in self._hotkeys:
            return False

        was_mouse = False
        for combo, hid in list(self._mouse_hotkeys.items()):
            if hid == hotkey_id:
                del self._mouse_hotkeys[combo]
                was_mouse = True
        if not self._mouse_hotkeys:
            self._stop_mouse_hook()

        if was_mouse:
            # mouse hotkeys were never registered with RegisterHotKey
            del self._hotkeys[hotkey_id]
            return True

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
        self._mouse_hotkeys.clear()
        self._stop_mouse_hook()
        self._registered = False

    # ------------------------------------------------------------------
    # Mouse button hotkeys via a low-level mouse hook (WH_MOUSE_LL)
    # ------------------------------------------------------------------

    def _register_mouse_hotkey(self, hotkey_str: str, button: str, modifiers: int,
                               callback: Callable, description: str = "") -> Optional[int]:
        hotkey_id = self._next_id
        self._next_id += 1
        hotkey = Hotkey(
            id=hotkey_id,
            key=MOUSE_BUTTON_VK.get(button, 0),
            modifiers=modifiers,
            callback=callback,
            description=description or hotkey_str,
        )
        self._hotkeys[hotkey_id] = hotkey
        self._mouse_hotkeys[(button, modifiers)] = hotkey_id
        self._ensure_mouse_hook()
        logger.info(f"Registered mouse hotkey: {hotkey_str} (id={hotkey_id})")
        return hotkey_id

    def _current_mouse_modifiers(self) -> int:
        from ctypes import windll
        mods = 0
        if windll.user32.GetAsyncKeyState(VK_SHIFT) & 0x8000:
            mods |= MOD_SHIFT
        if windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000:
            mods |= MOD_CONTROL
        if windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000:
            mods |= MOD_ALT
        if windll.user32.GetAsyncKeyState(VK_LWIN) & 0x8000 or \
           windll.user32.GetAsyncKeyState(VK_RWIN) & 0x8000:
            mods |= MOD_WIN
        return mods

    def _ensure_mouse_hook(self):
        if sys.platform != "win32" or self._mouse_hook_handle:
            return
        import ctypes
        import threading
        from ctypes import windll, wintypes

        HOOKPROC = ctypes.WINFUNCTYPE(
            ctypes.c_long, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p)

        def hook_proc(nCode, wParam, lParam):
            try:
                if nCode >= 0 and wParam in (WM_LBUTTONDOWN, WM_RBUTTONDOWN,
                                             WM_MBUTTONDOWN, WM_XBUTTONDOWN):
                    if wParam == WM_LBUTTONDOWN:
                        button = "MouseLeft"
                    elif wParam == WM_RBUTTONDOWN:
                        button = "MouseRight"
                    elif wParam == WM_MBUTTONDOWN:
                        button = "MouseMiddle"
                    else:
                        xbtn = (wParam >> 16) & 0xFFFF
                        button = "MouseX1" if xbtn == 1 else "MouseX2"
                    mods = self._current_mouse_modifiers()
                    hotkey_id = self._mouse_hotkeys.get((button, mods))
                    if hotkey_id is not None:
                        self.mouse_hotkey_triggered.emit(hotkey_id)
                        return 1  # swallow the click
            except Exception as e:
                logger.error(f"Mouse hook error: {e}")
            return windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

        self._mouse_hook_proc = HOOKPROC(hook_proc)
        module = windll.kernel32.GetModuleHandleW(None)
        handle = windll.user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_hook_proc, module, 0)
        if not handle:
            logger.error("Failed to install low-level mouse hook")
            self._mouse_hook_proc = None
            return
        self._mouse_hook_handle = handle

        def loop():
            from ctypes import windll, wintypes, byref
            msg = wintypes.MSG()
            while windll.user32.GetMessageW(byref(msg), None, 0, 0) > 0:
                windll.user32.TranslateMessage(byref(msg))
                windll.user32.DispatchMessageW(byref(msg))

        self._mouse_hook_thread = threading.Thread(target=loop, daemon=True)
        self._mouse_hook_thread.start()
        self._mouse_hook_thread_id = self._mouse_hook_thread.ident
        logger.info("Low-level mouse hook installed")

    def _stop_mouse_hook(self):
        if sys.platform != "win32" or not self._mouse_hook_handle:
            return
        try:
            from ctypes import windll
            windll.user32.UnhookWindowsHookEx(self._mouse_hook_handle)
            self._mouse_hook_handle = None
            self._mouse_hook_proc = None
            if self._mouse_hook_thread_id:
                windll.user32.PostThreadMessageW(self._mouse_hook_thread_id, 0x0012, 0, 0)  # WM_QUIT
        except Exception as e:
            logger.error(f"Failed to remove mouse hook: {e}")

    def is_mouse_hotkey(self, hotkey_str: str) -> bool:
        _key, _mods, mouse = self.parse_hotkey_string_ex(hotkey_str)
        return mouse is not None

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
        key, modifiers, mouse = self.parse_hotkey_string_ex(hotkey_str)
        conflicts = []

        if mouse:
            for (btn, mods), hid in self._mouse_hotkeys.items():
                if btn == mouse and mods == modifiers:
                    conflicts.append(self._hotkeys[hid].description)
            return conflicts

        mouse_ids = set(self._mouse_hotkeys.values())
        for hk in self._hotkeys.values():
            if hk.id in mouse_ids:
                continue
            if hk.key == key and hk.modifiers == modifiers and key != 0:
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