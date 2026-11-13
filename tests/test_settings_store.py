"""Tests for settings storage."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from crosshair.models import AppSettings, CrosshairSettings, OverlaySettings, ShortcutSettings
from storage.settings_store import SettingsStore


@pytest.fixture
def temp_settings_dir():
    """Create a temporary directory for settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def settings_store(temp_settings_dir):
    """Create a settings store with temporary path."""
    with patch('storage.settings_store.QStandardPaths.writableLocation') as mock:
        mock.return_value = str(temp_settings_dir)
        store = SettingsStore()
        store._settings_path = temp_settings_dir / "settings.json"
        yield store


def test_default_settings(settings_store):
    """Test default settings creation."""
    settings = settings_store.load()
    assert isinstance(settings, AppSettings)
    assert settings.schema_version == 1
    assert settings.overlay.enabled is True
    assert settings.crosshair.gap == 2


def test_save_and_load(settings_store):
    """Test saving and loading settings."""
    # Create custom settings
    settings = AppSettings(
        overlay=OverlaySettings(enabled=False, monitor_id="monitor_1"),
        crosshair=CrosshairSettings(gap=10, color="#FF0000"),
        shortcuts=ShortcutSettings(toggle_overlay="F10"),
        last_share_code="CSGO-TESTCODE"
    )
    settings_store.update_full_settings(settings)
    settings_store.force_save()

    # Create new store and load
    with patch('storage.settings_store.QStandardPaths.writableLocation') as mock:
        mock.return_value = str(settings_store._settings_path.parent)
        new_store = SettingsStore()
        new_store._settings_path = settings_store._settings_path
        loaded = new_store.load()

    assert loaded.overlay.enabled is False
    assert loaded.overlay.monitor_id == "monitor_1"
    assert loaded.crosshair.gap == 10
    assert loaded.crosshair.color == "#FF0000"
    assert loaded.shortcuts.toggle_overlay == "F10"
    assert loaded.last_share_code == "CSGO-TESTCODE"


def test_corrupted_settings_handling(settings_store):
    """Test handling of corrupted settings file."""
    # Write invalid JSON
    settings_store._settings_path.write_text("{ invalid json }")

    # Should load defaults without crashing
    settings = settings_store.load()
    assert isinstance(settings, AppSettings)
    assert settings.crosshair.gap == 2  # Default


def test_settings_migration_placeholder(settings_store):
    """Test settings migration (placeholder)."""
    # Write old version settings
    old_data = {
        "schema_version": 1,
        "overlay": {"enabled": True},
        "crosshair": {"gap": 5}
    }
    with open(settings_store._settings_path, "w") as f:
        json.dump(old_data, f)

    # Load should handle version
    settings = settings_store.load()
    assert settings.schema_version == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])