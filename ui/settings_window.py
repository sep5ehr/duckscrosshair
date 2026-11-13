"""Main settings window with all crosshair controls."""

import os
import sys
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QPoint
from PySide6.QtGui import QAction, QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QCheckBox, QComboBox, QSpinBox,
    QGroupBox, QFormLayout, QScrollArea, QMessageBox,
    QSystemTrayIcon, QMenu, QStyle, QLineEdit
)

from crosshair.models import CrosshairSettings, OverlaySettings, ShortcutSettings, AppSettings
from crosshair.renderer import CrosshairRenderer
from ui.preview_widget import PreviewWidget, PreviewControls
from ui.crosshair_controls import CrosshairControls
from ui.code_import_widget import CodeImportWidget
from overlay.monitor_manager import MonitorManager, MonitorInfo
from winplatform.hotkeys import get_hotkey_manager, HotkeyManager
from storage.settings_store import SettingsStore


class SettingsWindow(QMainWindow):
    """Main settings window with tabs for all configuration."""

    # Signals
    overlay_toggled = Signal(bool)
    settings_changed = Signal(AppSettings)
    close_requested = Signal()

    def __init__(self, monitor_manager: MonitorManager, settings_store: SettingsStore, parent=None):
        super().__init__(parent)
        self.monitor_manager = monitor_manager
        self.settings_store = settings_store
        self.hotkey_manager = get_hotkey_manager()

        self._settings = settings_store.get_settings()
        self._renderer = CrosshairRenderer(self._settings.crosshair)
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._save_settings)

        self._setup_ui()
        self._load_settings()
        self._register_hotkeys()

    def _setup_ui(self):
        self.setWindowTitle("Crosshair Overlay Settings")
        self.setMinimumSize(800, 600)
        self.resize(900, 700)

        # Central widget with tabs
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self.tabs)

        # Create tabs
        self._create_general_tab()
        self._create_crosshair_tab()
        self._create_preview_tab()
        self._create_code_tab()
        self._create_shortcuts_tab()
        self._create_about_tab()

        # Status bar
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.statusBar().setSizeGripEnabled(False)

        # Connect settings store signals
        self.settings_store.settings_changed.connect(self._on_settings_saved)
        self.settings_store.save_error.connect(self._on_save_error)

    def _create_general_tab(self):
        """Create General settings tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Left panel - settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        # Overlay enable
        self.overlay_enable_check = QCheckBox("Enable Overlay")
        self.overlay_enable_check.setChecked(self._settings.overlay.enabled)
        self.overlay_enable_check.toggled.connect(self._on_overlay_toggled)
        left_layout.addWidget(self.overlay_enable_check)

        # Monitor selection
        monitor_group = QGroupBox("Monitor")
        monitor_layout = QFormLayout(monitor_group)
        monitor_layout.setSpacing(8)

        self.monitor_combo = QComboBox()
        self._update_monitor_list()
        self.monitor_combo.currentTextChanged.connect(self._on_monitor_changed)
        monitor_layout.addRow("Display:", self.monitor_combo)

        # Refresh monitors button
        refresh_btn = QPushButton("Refresh Monitors")
        refresh_btn.clicked.connect(self._refresh_monitors)
        monitor_layout.addRow("", refresh_btn)

        left_layout.addWidget(monitor_group)

        # Window behavior
        behavior_group = QGroupBox("Window Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        behavior_layout.setSpacing(8)

        self.always_on_top_check = QCheckBox("Always on Top")
        self.always_on_top_check.setChecked(self._settings.overlay.always_on_top)
        self.always_on_top_check.toggled.connect(self._on_behavior_changed)
        behavior_layout.addWidget(self.always_on_top_check)

        self.click_through_check = QCheckBox("Click Through (mouse passes through)")
        self.click_through_check.setChecked(self._settings.overlay.click_through)
        self.click_through_check.toggled.connect(self._on_behavior_changed)
        behavior_layout.addWidget(self.click_through_check)

        left_layout.addWidget(behavior_group)

        # Opacity
        opacity_group = QGroupBox("Overlay Opacity")
        opacity_layout = QFormLayout(opacity_group)
        self.overlay_opacity_spin = QSpinBox()
        self.overlay_opacity_spin.setRange(1, 100)
        self.overlay_opacity_spin.setValue(int(self._settings.overlay.opacity * 100))
        self.overlay_opacity_spin.setSuffix("%")
        self.overlay_opacity_spin.valueChanged.connect(self._on_behavior_changed)
        opacity_layout.addRow("Opacity:", self.overlay_opacity_spin)
        left_layout.addWidget(opacity_group)

        # Start with Windows
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        self.startup_check = QCheckBox("Start with Windows")
        self.startup_check.setChecked(self._is_startup_enabled())
        self.startup_check.toggled.connect(self._on_startup_toggled)
        startup_layout.addWidget(self.startup_check)
        left_layout.addWidget(startup_group)

        left_layout.addStretch()

        # Right panel - preview
        self.general_preview = PreviewWidget(self._renderer)
        self.general_preview.setMinimumWidth(200)
        self.general_preview.setMaximumWidth(250)

        # Add both panels
        layout.addWidget(left_widget, 2)
        layout.addWidget(self.general_preview, 1)

        self.tabs.addTab(widget, "General")

    def _create_crosshair_tab(self):
        """Create Crosshair settings tab."""
        # Main widget with horizontal layout (controls + preview)
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Scroll area for many controls (left side)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(400)

        self.crosshair_controls = CrosshairControls()
        self.crosshair_controls.settings_changed.connect(self._on_crosshair_changed)
        self.crosshair_controls.reset_requested.connect(self._on_reset_crosshair)

        scroll.setWidget(self.crosshair_controls)

        # Preview widget (right side)
        self.crosshair_preview = PreviewWidget(self._renderer)
        self.crosshair_preview.setMinimumWidth(200)
        self.crosshair_preview.setMaximumWidth(250)

        # Add to layout
        layout.addWidget(scroll, 2)
        layout.addWidget(self.crosshair_preview, 1)

        self.tabs.addTab(widget, "Crosshair")

    def _create_preview_tab(self):
        """Create Preview tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Preview widget (left side, larger)
        self.preview_widget = PreviewWidget(self._renderer)
        self.preview_widget.setMinimumWidth(400)

        # Controls (right side)
        self.preview_controls = PreviewControls()
        self.preview_controls.background_changed.connect(self.preview_widget.set_background)
        self.preview_controls.zoom_changed.connect(self.preview_widget.set_zoom)
        self.preview_controls.center_mark_toggled.connect(self.preview_widget.set_show_center_mark)

        # Add to layout with stretch factors
        layout.addWidget(self.preview_widget, 3)
        layout.addWidget(self.preview_controls, 1)

        self.tabs.addTab(widget, "Preview")

    def _create_code_tab(self):
        """Create CS2 Code import/export tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self.code_widget = CodeImportWidget()
        self.code_widget.set_current_settings(self._settings.crosshair)
        self.code_widget.settings_imported.connect(self._on_code_imported)
        self.code_widget.code_exported.connect(self._on_code_exported)
        self.code_widget.validation_result.connect(self._on_validation_result)

        # Preview widget (right side)
        self.code_preview = PreviewWidget(self._renderer)
        self.code_preview.setMinimumWidth(200)
        self.code_preview.setMaximumWidth(250)

        layout.addWidget(self.code_widget, 2)
        layout.addWidget(self.code_preview, 1)

        self.tabs.addTab(widget, "CS2 Code")

    def _create_shortcuts_tab(self):
        """Create Keyboard Shortcuts tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Left panel - shortcuts settings
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)

        # Shortcuts list
        shortcuts_group = QGroupBox("Global Hotkeys")
        shortcuts_layout = QFormLayout(shortcuts_group)
        shortcuts_layout.setSpacing(8)

        # Toggle overlay
        toggle_overlay_layout = QHBoxLayout()
        self.toggle_overlay_edit = QLineEdit(self._settings.shortcuts.toggle_overlay)
        self.toggle_overlay_edit.setPlaceholderText("Press key combination...")
        self.toggle_overlay_edit.setMaximumWidth(200)
        self.toggle_overlay_edit.installEventFilter(self)
        self._toggle_overlay_edit_active = False
        toggle_overlay_layout.addWidget(self.toggle_overlay_edit)
        self.toggle_overlay_test_btn = QPushButton("Test")
        self.toggle_overlay_test_btn.clicked.connect(lambda: self._test_hotkey("toggle_overlay"))
        toggle_overlay_layout.addWidget(self.toggle_overlay_test_btn)
        shortcuts_layout.addRow("Toggle Overlay:", toggle_overlay_layout)

        # Toggle settings
        toggle_settings_layout = QHBoxLayout()
        self.toggle_settings_edit = QLineEdit(self._settings.shortcuts.toggle_settings)
        self.toggle_settings_edit.setPlaceholderText("Press key combination...")
        self.toggle_settings_edit.setMaximumWidth(200)
        self.toggle_settings_edit.installEventFilter(self)
        self._toggle_settings_edit_active = False
        toggle_settings_layout.addWidget(self.toggle_settings_edit)
        self.toggle_settings_test_btn = QPushButton("Test")
        self.toggle_settings_test_btn.clicked.connect(lambda: self._test_hotkey("toggle_settings"))
        toggle_settings_layout.addWidget(self.toggle_settings_test_btn)
        shortcuts_layout.addRow("Toggle Settings:", toggle_settings_layout)

        left_layout.addWidget(shortcuts_group)

        # Conflict detection
        conflict_group = QGroupBox("Conflict Detection")
        conflict_layout = QVBoxLayout(conflict_group)

        self.conflict_label = QLabel("No conflicts detected")
        self.conflict_label.setStyleSheet("color: #4caf50;")
        conflict_layout.addWidget(self.conflict_label)

        check_conflicts_btn = QPushButton("Check for Conflicts")
        check_conflicts_btn.clicked.connect(self._check_hotkey_conflicts)
        conflict_layout.addWidget(check_conflicts_btn)

        left_layout.addWidget(conflict_group)

        # Info
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        info_text = QLabel(
            "Global hotkeys work system-wide, even when the application is not focused.\n"
            "Default: F8 = Toggle Overlay, F9 = Toggle Settings\n"
            "Press Esc to cancel key capture."
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(info_text)
        left_layout.addWidget(info_group)

        left_layout.addStretch()

        # Right panel - preview
        self.shortcuts_preview = PreviewWidget(self._renderer)
        self.shortcuts_preview.setMinimumWidth(200)
        self.shortcuts_preview.setMaximumWidth(250)

        # Add both panels
        layout.addWidget(left_widget, 2)
        layout.addWidget(self.shortcuts_preview, 1)

        self.tabs.addTab(widget, "Shortcuts")

    def _create_about_tab(self):
        """Create About tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Left panel - info
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(12)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # App info
        info_group = QGroupBox("Application")
        info_layout = QFormLayout(info_group)

        from app.constants import APP_NAME, APP_VERSION
        import sys
        import PySide6

        info_layout.addRow("Name:", QLabel(APP_NAME))
        info_layout.addRow("Version:", QLabel(APP_VERSION))
        info_layout.addRow("Python:", QLabel(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"))
        info_layout.addRow("PySide6:", QLabel(PySide6.__version__))

        left_layout.addWidget(info_group)

        # Limitations
        limits_group = QGroupBox("Overlay Limitations")
        limits_layout = QVBoxLayout(limits_group)

        limits_text = QLabel(
            "• This overlay works best with windowed and borderless-windowed applications.\n"
            "• Exclusive fullscreen applications (many games) may not display the overlay.\n"
            "• This is a Windows desktop limitation, not a bug in this application.\n"
            "• No code injection, memory reading, or anti-cheat bypass is performed.\n"
            "• The overlay uses standard Windows APIs for transparency and click-through."
        )
        limits_text.setWordWrap(True)
        limits_text.setStyleSheet("color: #666; font-size: 11px;")
        limits_layout.addWidget(limits_text)

        left_layout.addWidget(limits_group)

        # Troubleshooting
        trouble_group = QGroupBox("Troubleshooting")
        trouble_layout = QVBoxLayout(trouble_group)

        trouble_text = QLabel(
            "If the overlay doesn't appear:\n"
            "1. Ensure the application is running (check system tray)\n"
            "2. Check that 'Enable Overlay' is checked in General tab\n"
            "3. Try disabling 'Click Through' temporarily\n"
            "4. Check the correct monitor is selected\n"
            "5. For games: use Borderless Windowed mode instead of Exclusive Fullscreen\n"
            "6. Some anti-cheat software may block overlays"
        )
        trouble_text.setWordWrap(True)
        trouble_text.setStyleSheet("color: #666; font-size: 11px;")
        trouble_layout.addWidget(trouble_text)

        left_layout.addWidget(trouble_group)

        left_layout.addStretch()

        # Right panel - preview
        self.about_preview = PreviewWidget(self._renderer)
        self.about_preview.setMinimumWidth(200)
        self.about_preview.setMaximumWidth(250)

        # Add both panels
        layout.addWidget(left_widget, 2)
        layout.addWidget(self.about_preview, 1)

        self.tabs.addTab(widget, "About")

    def _load_settings(self):
        """Load settings into UI."""
        s = self._settings

        # General
        self.overlay_enable_check.setChecked(s.overlay.enabled)
        self.always_on_top_check.setChecked(s.overlay.always_on_top)
        self.click_through_check.setChecked(s.overlay.click_through)
        self.overlay_opacity_spin.setValue(int(s.overlay.opacity * 100))

        # Monitor
        self._update_monitor_list()
        idx = self.monitor_combo.findData(s.overlay.monitor_id)
        if idx >= 0:
            self.monitor_combo.setCurrentIndex(idx)

        # Crosshair
        self.crosshair_controls.load_settings(s.crosshair)

        # Preview
        self.preview_controls.bg_combo.setCurrentText(
            self._get_preview_background_name()
        )
        self.preview_controls.zoom_slider.setValue(100)
        self.preview_controls.zoom_spin.setValue(100)

        # Shortcuts
        self.toggle_overlay_edit.setText(s.shortcuts.toggle_overlay)
        self.toggle_settings_edit.setText(s.shortcuts.toggle_settings)

        # Code widget
        self.code_widget.set_current_settings(s.crosshair)

    def _get_preview_background_name(self) -> str:
        # This would come from settings if we stored it
        return "Checkerboard"

    def _update_monitor_list(self):
        """Update monitor combo box."""
        current_data = self.monitor_combo.currentData()
        self.monitor_combo.clear()

        monitors = self.monitor_manager.get_monitors()
        for monitor in monitors:
            text = f"{monitor.name} ({monitor.geometry.width()}x{monitor.geometry.height()})"
            if monitor.is_primary:
                text += " ★"
            self.monitor_combo.addItem(text, monitor.id)

        # Restore selection
        if current_data:
            idx = self.monitor_combo.findData(current_data)
            if idx >= 0:
                self.monitor_combo.setCurrentIndex(idx)
        else:
            # Default to primary
            idx = self.monitor_combo.findData("primary")
            if idx >= 0:
                self.monitor_combo.setCurrentIndex(idx)

    def _refresh_monitors(self):
        """Refresh monitor list."""
        self.monitor_manager._scan_monitors()
        self._update_monitor_list()

    def _register_hotkeys(self):
        """Register global hotkeys from settings."""
        s = self._settings.shortcuts
        self.hotkey_manager.register_hotkey(
            s.toggle_overlay,
            self._on_hotkey_toggle_overlay,
            "Toggle Overlay"
        )
        self.hotkey_manager.register_hotkey(
            s.toggle_settings,
            self._on_hotkey_toggle_settings,
            "Toggle Settings"
        )

    def _unregister_hotkeys(self):
        """Unregister all hotkeys."""
        self.hotkey_manager.unregister_all()

    def _on_hotkey_toggle_overlay(self):
        """Hotkey callback for toggle overlay."""
        self.overlay_toggled.emit(not self._settings.overlay.enabled)

    def _on_hotkey_toggle_settings(self):
        """Hotkey callback for toggle settings."""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _on_overlay_toggled(self, enabled: bool):
        """Handle overlay enable/disable."""
        self._settings.overlay.enabled = enabled
        self.overlay_toggled.emit(enabled)
        self._mark_dirty()

    def _on_monitor_changed(self, text: str):
        """Handle monitor selection change."""
        monitor_id = self.monitor_combo.currentData()
        if monitor_id:
            self._settings.overlay.monitor_id = monitor_id
            self._mark_dirty()

    def _on_behavior_changed(self):
        """Handle window behavior changes."""
        self._settings.overlay.always_on_top = self.always_on_top_check.isChecked()
        self._settings.overlay.click_through = self.click_through_check.isChecked()
        self._settings.overlay.opacity = self.overlay_opacity_spin.value() / 100.0
        self._mark_dirty()

    def _is_startup_enabled(self) -> bool:
        """Check if app is set to start with Windows."""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                try:
                    winreg.QueryValueEx(key, "DucksCrosshair")
                    return True
                except FileNotFoundError:
                    return False
        except Exception:
            return False

    def _on_startup_toggled(self, enabled: bool):
        """Handle start with Windows toggle."""
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    # Add to startup
                    exe_path = sys.executable
                    if exe_path.endswith("python.exe") or exe_path.endswith("pythonw.exe"):
                        # Running from source - use main.py
                        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
                        winreg.SetValueEx(key, "DucksCrosshair", 0, winreg.REG_SZ, f'"{exe_path}" "{script_path}"')
                    else:
                        # Running from compiled executable
                        winreg.SetValueEx(key, "DucksCrosshair", 0, winreg.REG_SZ, f'"{exe_path}"')
                else:
                    # Remove from startup
                    try:
                        winreg.DeleteValue(key, "DucksCrosshair")
                    except FileNotFoundError:
                        pass
        except Exception as e:
            logger.warning(f"Failed to update startup setting: {e}")
        self._mark_dirty()

    def _on_crosshair_changed(self, settings: CrosshairSettings):
        """Handle crosshair settings change."""
        self._settings.crosshair = settings
        self._renderer.update_settings(settings)
        self.preview_widget.update()
        self.general_preview.update()
        self.crosshair_preview.update()
        self.code_widget.set_current_settings(settings)
        self._mark_dirty()

    def _on_reset_crosshair(self):
        """Reset crosshair to defaults."""
        from app.constants import DEFAULT_CROSSHAIR
        self.crosshair_controls.load_settings(DEFAULT_CROSSHAIR)

    def _on_code_imported(self, settings: CrosshairSettings, warnings: list, format_name: str):
        """Handle imported share code settings."""
        self.crosshair_controls.load_settings(settings)
        self._settings.crosshair = settings
        self._mark_dirty()
        self._show_status(f"Imported {format_name}")

    def _on_code_exported(self, share_code: str, warnings: list):
        """Handle exported share code."""
        self._show_status("Share code exported")

    def _on_validation_result(self, valid: bool, format_name: str, warnings: list):
        """Handle validation result."""
        if valid:
            self._show_status(f"Valid {format_name}")
        else:
            self._show_status("Invalid share code")

    def _on_settings_saved(self, settings: AppSettings):
        """Handle settings saved signal."""
        self._show_status("Saved", 2000)

    def _on_save_error(self, error: str):
        """Handle save error."""
        self._show_status(f"Save error: {error}", 5000)

    def _mark_dirty(self):
        """Mark settings as dirty for debounced save."""
        self.settings_store.update_full_settings(self._settings)
        self.settings_changed.emit(self._settings)

    def _save_settings(self):
        """Force save settings."""
        self.settings_store.force_save()

    def _show_status(self, message: str, timeout: int = 0):
        """Show status message."""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))

    def _test_hotkey(self, name: str):
        """Test a hotkey by triggering its callback."""
        if name == "toggle_overlay":
            self._on_hotkey_toggle_overlay()
        elif name == "toggle_settings":
            self._on_hotkey_toggle_settings()

    def _check_hotkey_conflicts(self):
        """Check for hotkey conflicts."""
        conflicts = []

        # Check toggle overlay
        conflicts.extend(self.hotkey_manager.check_conflicts(self.toggle_overlay_edit.text()))
        # Check toggle settings
        conflicts.extend(self.hotkey_manager.check_conflicts(self.toggle_settings_edit.text()))

        # Check duplicates between the two
        if self.toggle_overlay_edit.text().upper() == self.toggle_settings_edit.text().upper():
            conflicts.append("Toggle Overlay and Toggle Settings use the same key")

        if conflicts:
            self.conflict_label.setText("Conflicts: " + ", ".join(conflicts))
            self.conflict_label.setStyleSheet("color: #f44336;")
        else:
            self.conflict_label.setText("No conflicts detected")
            self.conflict_label.setStyleSheet("color: #4caf50;")

    def eventFilter(self, obj, event):
        """Event filter for key capture in shortcut fields."""
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QKeyEvent

        if event.type() == QEvent.Type.KeyPress and obj in (self.toggle_overlay_edit, self.toggle_settings_edit):
            key_event = event
            key = key_event.key()
            modifiers = key_event.modifiers()

            # Ignore modifier-only presses
            if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                return True

            # Build key string
            parts = []
            if modifiers & Qt.KeyboardModifier.ControlModifier:
                parts.append("Ctrl")
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                parts.append("Shift")
            if modifiers & Qt.KeyboardModifier.AltModifier:
                parts.append("Alt")
            if modifiers & Qt.KeyboardModifier.MetaModifier:
                parts.append("Win")

            # Get key name
            key_name = self._key_to_string(key)
            if key_name:
                parts.append(key_name)

            hotkey_str = "+".join(parts)
            obj.setText(hotkey_str)

            # Update settings
            if obj == self.toggle_overlay_edit:
                self._settings.shortcuts.toggle_overlay = hotkey_str
            else:
                self._settings.shortcuts.toggle_settings = hotkey_str

            # Re-register hotkeys
            self.hotkey_manager.unregister_all()
            self._register_hotkeys()

            return True

        return super().eventFilter(obj, event)

    def _key_to_string(self, key: int) -> str:
        """Convert Qt key to string."""
        key_map = {
            Qt.Key.Key_Escape: "Esc",
            Qt.Key.Key_Tab: "Tab",
            Qt.Key.Key_Backspace: "Backspace",
            Qt.Key.Key_Return: "Enter",
            Qt.Key.Key_Enter: "Enter",
            Qt.Key.Key_Space: "Space",
            Qt.Key.Key_F1: "F1", Qt.Key.Key_F2: "F2", Qt.Key.Key_F3: "F3",
            Qt.Key.Key_F4: "F4", Qt.Key.Key_F5: "F5", Qt.Key.Key_F6: "F6",
            Qt.Key.Key_F7: "F7", Qt.Key.Key_F8: "F8", Qt.Key.Key_F9: "F9",
            Qt.Key.Key_F10: "F10", Qt.Key.Key_F11: "F11", Qt.Key.Key_F12: "F12",
        }

        if key in key_map:
            return key_map[key]

        # Single character keys
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key - Qt.Key.Key_A + ord('A'))
        if Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            return chr(key - Qt.Key.Key_0 + ord('0'))

        return ""

    def closeEvent(self, event):
        """Handle close event - hide instead of close."""
        event.ignore()
        self.hide()
        self.close_requested.emit()

    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Update preview
        self.preview_widget.update()

    def get_settings(self) -> AppSettings:
        """Get current settings."""
        return self._settings