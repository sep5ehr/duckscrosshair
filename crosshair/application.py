"""Main application class."""

import sys
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, QTimer, QCoreApplication
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from app.constants import APP_NAME, APP_VERSION
from app.state import AppState
from storage.settings_store import SettingsStore
from overlay.monitor_manager import MonitorManager
from overlay.overlay_window import OverlayWindow
from ui.settings_window import SettingsWindow
from ui.tray import TrayIcon, load_app_icon
from winplatform.hotkeys import get_hotkey_manager, cleanup_hotkeys


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class CrosshairOverlayApplication(QApplication):
    """Main application class."""

    def __init__(self, argv: list):
        super().__init__(argv)
        self.setApplicationName(APP_NAME)
        self.setApplicationVersion(APP_VERSION)
        self.setQuitOnLastWindowClosed(False)  # Keep running in tray

        # Set application icon
        self.setWindowIcon(load_app_icon())

        # State
        self.state = AppState()
        self.settings_store: Optional[SettingsStore] = None
        self.monitor_manager: Optional[MonitorManager] = None
        self.overlay_window: Optional[OverlayWindow] = None
        self.settings_window: Optional[SettingsWindow] = None
        self.tray_icon: Optional[TrayIcon] = None
        self.hotkey_manager = get_hotkey_manager()

        # Initialize
        self._init_components()
        self._connect_signals()

        logger.info(f"{APP_NAME} v{APP_VERSION} started")

    def _init_components(self):
        """Initialize all components."""
        # Settings store
        self.settings_store = SettingsStore(self)
        self.state.settings = self.settings_store.load()

        # Monitor manager
        self.monitor_manager = MonitorManager(self)
        self.state.monitor_manager = self.monitor_manager

        # Overlay window
        self.overlay_window = OverlayWindow(self.monitor_manager, self)
        self.overlay_window.update_settings(
            self.state.get_overlay_settings(),
            self.state.get_crosshair_settings()
        )
        self.state.overlay_window = self.overlay_window

        # Settings window
        self.settings_window = SettingsWindow(self.monitor_manager, self.settings_store, None)
        self.state.settings_window = self.settings_window

        # Tray icon
        self.tray_icon = TrayIcon(self)
        self.state.tray_icon = self.tray_icon
        self.tray_icon.show()

        # Show overlay if enabled
        if self.state.settings.overlay.enabled:
            self.overlay_window.set_enabled(True)
            self.tray_icon.set_overlay_enabled(True)
        else:
            self.overlay_window.set_enabled(False)
            self.tray_icon.set_overlay_enabled(False)

        # Update tray icon with crosshair colors
        self.tray_icon.update_icon(
            self.state.settings.crosshair.color,
            self.state.settings.crosshair.outline_color
        )

        # Update tray icon with crosshair colors
        self.tray_icon.update_icon(
            self.state.settings.crosshair.color,
            self.state.settings.crosshair.outline_color
        )

    def _connect_signals(self):
        """Connect component signals."""
        # Settings window signals
        self.settings_window.overlay_toggled.connect(self._on_overlay_toggled)
        self.settings_window.settings_changed.connect(self._on_settings_changed)
        self.settings_window.close_requested.connect(self._on_settings_closed)

        # Tray signals
        self.tray_icon.show_settings.connect(self._show_settings)
        self.tray_icon.toggle_overlay.connect(self._toggle_overlay)
        self.tray_icon.quit_requested.connect(self._quit_application)

        # Settings store signals
        self.settings_store.settings_changed.connect(self._on_settings_saved)

    def _on_overlay_toggled(self, enabled: bool):
        """Handle overlay toggle from settings or hotkey."""
        self.state.settings.overlay.enabled = enabled
        self.overlay_window.set_enabled(enabled)
        self.tray_icon.set_overlay_enabled(enabled)
        self.settings_store.update_overlay(self.state.settings.overlay)
        logger.info(f"Overlay {'enabled' if enabled else 'disabled'}")

    def _toggle_overlay(self):
        """Toggle overlay state."""
        new_state = not self.state.settings.overlay.enabled
        self._on_overlay_toggled(new_state)

    def _on_settings_changed(self, settings: AppState):
        """Handle settings changes from settings window."""
        self.state.settings = settings
        self.overlay_window.update_settings(
            settings.overlay,
            settings.crosshair
        )
        self.tray_icon.update_icon(
            settings.crosshair.color,
            settings.crosshair.outline_color
        )

    def _on_settings_saved(self, settings: AppState):
        """Handle settings saved to disk."""
        logger.debug("Settings persisted to disk")

    def _on_settings_closed(self):
        """Handle settings window close."""
        self.state.settings_window_visible = False

    def _show_settings(self):
        """Show settings window."""
        if self.settings_window.isHidden():
            self.settings_window.show()
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            self.state.settings_window_visible = True
        else:
            self.settings_window.raise_()
            self.settings_window.activateWindow()

    def _quit_application(self):
        """Clean shutdown."""
        logger.info("Shutting down...")
        cleanup_hotkeys()
        self.settings_store.force_save()
        self.overlay_window.close()
        self.settings_window.close()
        self.tray_icon.hide()
        self.quit()

    def run(self) -> int:
        """Run the application."""
        return self.exec()


def main():
    """Entry point."""
    app = CrosshairOverlayApplication(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())