"""Windows-specific window styles for the overlay."""

import sys
from ctypes import wintypes, windll, c_int, byref

# Windows constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008

LWA_ALPHA = 0x00000002
LWA_COLORKEY = 0x00000001

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


def apply_overlay_styles(hwnd: int, click_through: bool = True, always_on_top: bool = True):
    """
    Apply Windows extended styles for overlay behavior.

    Args:
        hwnd: Window handle (int)
        click_through: Enable click-through (WS_EX_TRANSPARENT)
        always_on_top: Keep window on top (WS_EX_TOPMOST)
    """
    if sys.platform != "win32":
        return

    try:
        # Get current extended style
        ex_style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)

        # Base styles for overlay
        new_style = ex_style | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE

        if click_through:
            new_style |= WS_EX_TRANSPARENT

        if always_on_top:
            new_style |= WS_EX_TOPMOST

        # Apply extended style
        windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_style)

        # Set layered window attributes for transparency
        # Using color key (black) for transparency with alpha
        windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 255, LWA_COLORKEY | LWA_ALPHA)

        # Reposition to apply TOPMOST
        if always_on_top:
            windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )

    except Exception as e:
        # Fail silently - styles are best effort
        pass


def remove_overlay_styles(hwnd: int):
    """Remove overlay styles."""
    if sys.platform != "win32":
        return

    try:
        ex_style = windll.user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
        # Remove overlay-specific styles
        new_style = ex_style & ~(WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)
        windll.user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_style)
        windll.user32.SetWindowPos(
            hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
            SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE | SWP_SHOWWINDOW
        )
    except Exception:
        pass


def set_window_opacity(hwnd: int, opacity: float):
    """Set window opacity (0.0 to 1.0)."""
    if sys.platform != "win32":
        return

    try:
        alpha = int(max(0.0, min(1.0, opacity)) * 255)
        windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, alpha, LWA_ALPHA)
    except Exception:
        pass