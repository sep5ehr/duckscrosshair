"""Settings storage with JSON persistence, debouncing, and migration."""

import json
import os
import shutil
import logging
from pathlib import Path
from typing import Optional, Callable
from dataclasses import asdict

from PySide6.QtCore import QObject, QTimer, Signal, QStandardPaths

from app.constants import (
    SETTINGS_DIR_NAME,
    SETTINGS_FILE_NAME,
    SETTINGS_SCHEMA_VERSION,
    SETTINGS_DEBOUNCE_MS,
)
from crosshair.models import AppSettings, CrosshairSettings, OverlaySettings, ShortcutSettings


logger = logging.getLogger(__name__)


class SettingsStore(QObject):
    """Manages application settings persistence with debounced saves."""

    # Signals
    settings_changed = Signal(object)  # AppSettings
    settings_loaded = Signal(object)   # AppSettings
    save_error = Signal(str)           # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings: Optional[AppSettings] = None
        self._settings_path: Optional[Path] = None
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._perform_save)
        self._dirty = False

        # Initialize settings path
        self._init_settings_path()

    def _init_settings_path(self):
        """Initialize the settings file path."""
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        if not app_data:
            # Fallback to local AppData
            app_data = os.path.join(os.environ.get("APPDATA", ""), SETTINGS_DIR_NAME)

        settings_dir = Path(app_data)
        settings_dir.mkdir(parents=True, exist_ok=True)
        self._settings_path = settings_dir / SETTINGS_FILE_NAME
        logger.info(f"Settings path: {self._settings_path}")

    def load(self) -> AppSettings:
        """Load settings from disk, or return defaults if not found/corrupted."""
        if self._settings_path and self._settings_path.exists():
            try:
                with open(self._settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Validate schema version
                schema_version = data.get("schema_version", 1)
                if schema_version != SETTINGS_SCHEMA_VERSION:
                    logger.warning(f"Settings schema version mismatch: {schema_version} != {SETTINGS_SCHEMA_VERSION}")
                    # Could migrate here in the future

                self._settings = AppSettings.from_dict(data)
                logger.info("Settings loaded successfully")
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted settings file: {e}")
                self._backup_corrupted_settings()
                self._settings = AppSettings()
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                self._settings = AppSettings()
        else:
            logger.info("No settings file found, using defaults")
            self._settings = AppSettings()

        self._dirty = False
        self.settings_loaded.emit(self._settings)
        return self._settings

    def _backup_corrupted_settings(self):
        """Backup corrupted settings file before replacing."""
        if self._settings_path and self._settings_path.exists():
            backup_path = self._settings_path.with_suffix(".json.corrupted")
            try:
                shutil.copy2(self._settings_path, backup_path)
                logger.info(f"Backed up corrupted settings to {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup corrupted settings: {e}")

    def get_settings(self) -> AppSettings:
        """Get current settings (loads if not already loaded)."""
        if self._settings is None:
            return self.load()
        return self._settings

    def update_crosshair(self, crosshair: CrosshairSettings):
        """Update crosshair settings and mark dirty."""
        if self._settings:
            self._settings.crosshair = crosshair
            self._mark_dirty()

    def update_overlay(self, overlay: OverlaySettings):
        """Update overlay settings and mark dirty."""
        if self._settings:
            self._settings.overlay = overlay
            self._mark_dirty()

    def update_shortcuts(self, shortcuts: ShortcutSettings):
        """Update shortcut settings and mark dirty."""
        if self._settings:
            self._settings.shortcuts = shortcuts
            self._mark_dirty()

    def update_last_share_code(self, code: str):
        """Update last share code and mark dirty."""
        if self._settings:
            self._settings.last_share_code = code
            self._mark_dirty()

    def update_full_settings(self, settings: AppSettings):
        """Replace all settings and mark dirty."""
        self._settings = settings
        self._mark_dirty()

    def _mark_dirty(self):
        """Mark settings as dirty and start debounce timer."""
        self._dirty = True
        self._debounce_timer.start(SETTINGS_DEBOUNCE_MS)

    def _perform_save(self):
        """Actually write settings to disk."""
        if not self._dirty or not self._settings or not self._settings_path:
            return

        try:
            # Write to temporary file first, then atomically replace
            temp_path = self._settings_path.with_suffix(".json.tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self._settings.to_dict(), f, indent=2)

            # Atomic replace
            temp_path.replace(self._settings_path)

            self._dirty = False
            logger.debug("Settings saved successfully")
            self.settings_changed.emit(self._settings)

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.save_error.emit(str(e))

    def force_save(self):
        """Force immediate save (bypass debounce)."""
        self._debounce_timer.stop()
        self._perform_save()

    def reset_to_defaults(self) -> AppSettings:
        """Reset settings to defaults and save."""
        self._settings = AppSettings()
        self._mark_dirty()
        self.force_save()
        return self._settings

    def export_settings(self, path: Path) -> bool:
        """Export settings to a file."""
        if not self._settings:
            return False
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._settings.to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False

    def import_settings(self, path: Path) -> bool:
        """Import settings from a file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._settings = AppSettings.from_dict(data)
            self._mark_dirty()
            self.force_save()
            self.settings_loaded.emit(self._settings)
            return True
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False