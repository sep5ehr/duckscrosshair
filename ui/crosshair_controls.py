"""Crosshair settings controls for the settings window."""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QPixmap, QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QSlider, QSpinBox, QDoubleSpinBox, QCheckBox,
    QComboBox, QPushButton, QColorDialog, QLineEdit, QSizePolicy
)

from crosshair.models import CrosshairSettings
from crosshair.validation import validate_crosshair_settings, VALIDATION_RANGES

# Default crosshair settings (defined here to avoid circular imports)
DEFAULT_CROSSHAIR = CrosshairSettings(
    gap=2,
    length=6,
    thickness=2,
    size=6,
    color="#00FF00",
    opacity=1.0,
    outline_enabled=True,
    outline_color="#000000",
    outline_thickness=1,
    center_dot=False,
    t_style=False,
    style=4,
    dynamic_spread_limit=0.0,
    split_distance=7,
    inner_split_alpha=255,
    outer_split_alpha=255,
    split_size_ratio=0.5,
    reference_resolution=1920,
    scope_dot_scale=1.0,
    scope_dot_use_crosshair_color=False,
)


class ColorButton(QPushButton):
    """Button that shows a color preview and opens color dialog."""

    color_changed = Signal(str)

    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self._color = color.upper()
        self.setFixedSize(32, 24)
        self.setToolTip("Click to pick color\nRight-click for HEX input")
        self.clicked.connect(self._pick_color)
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 1px solid #888;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #fff;
            }}
        """)

    def _pick_color(self):
        dialog = QColorDialog(QColor(self._color), self)
        dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        if dialog.exec():
            color = dialog.selectedColor()
            self.set_color(color.name(QColor.NameFormat.HexArgb))

    def set_color(self, color: str):
        """Set color from hex string."""
        color = color.upper()
        if color != self._color:
            self._color = color
            self._update_style()
            self.color_changed.emit(color)

    def get_color(self) -> str:
        return self._color

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self._show_hex_input()
        else:
            super().mousePressEvent(event)

    def _show_hex_input(self):
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self, "HEX Color Input", "Enter HEX color (e.g. #FF0000 or #FF0000FF):",
            text=self._color
        )
        if ok and text:
            text = text.strip().upper()
            if not text.startswith("#"):
                text = "#" + text
            # Validate
            try:
                if len(text) in (4, 7, 9):
                    int(text[1:], 16)
                    self.set_color(text)
            except ValueError:
                pass


class SliderSpinBox(QWidget):
    """Synchronized slider and spin box for integer values."""

    value_changed = Signal(int)

    def __init__(self, label: str, min_val: int, max_val: int, default: int,
                 suffix: str = "", parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._setting_name = label.lower().replace(" ", "_")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.label = QLabel(label + ":")
        self.label.setMinimumWidth(100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(min_val, max_val)
        self.slider.setValue(default)
        self.slider.setTickInterval(max(1, (max_val - min_val) // 10))
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.spin = QSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setValue(default)
        if suffix:
            self.spin.setSuffix(" " + suffix)
        self.spin.setMinimumWidth(80)

        # Synchronize
        self.slider.valueChanged.connect(self.spin.setValue)
        self.spin.valueChanged.connect(self.slider.setValue)
        self.spin.valueChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spin)

    def value(self) -> int:
        return self.spin.value()

    def set_value(self, value: int):
        self.spin.setValue(value)

    def set_enabled(self, enabled: bool):
        self.slider.setEnabled(enabled)
        self.spin.setEnabled(enabled)
        self.label.setEnabled(enabled)


class FloatSliderSpinBox(QWidget):
    """Synchronized slider and spin box for float values."""

    value_changed = Signal(float)

    def __init__(self, label: str, min_val: float, max_val: float, default: float,
                 step: float = 0.01, decimals: int = 2, suffix: str = "", parent=None):
        super().__init__(parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._multiplier = int(1 / step) if step > 0 else 100

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.label = QLabel(label + ":")
        self.label.setMinimumWidth(100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(int(min_val * self._multiplier), int(max_val * self._multiplier))
        self.slider.setValue(int(default * self._multiplier))
        self.slider.setTickInterval(max(1, int((max_val - min_val) * self._multiplier // 10)))
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(min_val, max_val)
        self.spin.setValue(default)
        self.spin.setSingleStep(step)
        self.spin.setDecimals(decimals)
        if suffix:
            self.spin.setSuffix(" " + suffix)
        self.spin.setMinimumWidth(80)

        # Synchronize
        self.slider.valueChanged.connect(
            lambda v: self.spin.setValue(v / self._multiplier)
        )
        self.spin.valueChanged.connect(
            lambda v: self.slider.setValue(int(v * self._multiplier))
        )
        self.spin.valueChanged.connect(self.value_changed.emit)

        layout.addWidget(self.label)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.spin)

    def value(self) -> float:
        return self.spin.value()

    def set_value(self, value: float):
        self.spin.setValue(value)

    def set_enabled(self, enabled: bool):
        self.slider.setEnabled(enabled)
        self.spin.setEnabled(enabled)
        self.label.setEnabled(enabled)


class CrosshairControls(QWidget):
    """Complete crosshair settings controls."""

    settings_changed = Signal(CrosshairSettings)
    reset_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = CrosshairSettings()
        self._controls = {}
        self._setup_ui()
        self._load_settings(self._settings)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Core appearance group
        core_group = QGroupBox("Core Appearance")
        core_layout = QVBoxLayout(core_group)
        core_layout.setSpacing(6)

        # Gap
        self.gap_control = SliderSpinBox(
            "Gap", VALIDATION_RANGES["gap"][0], VALIDATION_RANGES["gap"][1],
            DEFAULT_CROSSHAIR.gap, "px"
        )
        core_layout.addWidget(self.gap_control)

        # Length
        self.length_control = SliderSpinBox(
            "Length", VALIDATION_RANGES["length"][0], VALIDATION_RANGES["length"][1],
            DEFAULT_CROSSHAIR.length, "px"
        )
        core_layout.addWidget(self.length_control)

        # Thickness
        self.thickness_control = SliderSpinBox(
            "Thickness", VALIDATION_RANGES["thickness"][0], VALIDATION_RANGES["thickness"][1],
            DEFAULT_CROSSHAIR.thickness, "px"
        )
        core_layout.addWidget(self.thickness_control)

        # Size (dot size)
        self.size_control = SliderSpinBox(
            "Dot Size", VALIDATION_RANGES["size"][0], VALIDATION_RANGES["size"][1],
            DEFAULT_CROSSHAIR.size, "px"
        )
        core_layout.addWidget(self.size_control)

        layout.addWidget(core_group)

        # Color & Opacity group
        color_group = QGroupBox("Color & Opacity")
        color_layout = QGridLayout(color_group)
        color_layout.setSpacing(6)
        color_layout.setColumnStretch(1, 1)

        # Main color
        color_layout.addWidget(QLabel("Main Color:"), 0, 0)
        self.color_btn = ColorButton(DEFAULT_CROSSHAIR.color)
        self.color_btn.color_changed.connect(self._on_color_changed)
        color_layout.addWidget(self.color_btn, 0, 1)

        # Opacity
        self.opacity_control = FloatSliderSpinBox(
            "Opacity", VALIDATION_RANGES["opacity"][0], VALIDATION_RANGES["opacity"][1],
            DEFAULT_CROSSHAIR.opacity, 0.01, 2, ""
        )
        color_layout.addWidget(QLabel("Opacity:"), 1, 0)
        color_layout.addWidget(self.opacity_control, 1, 1)

        layout.addWidget(color_group)

        # Outline group
        outline_group = QGroupBox("Outline")
        outline_layout = QGridLayout(outline_group)
        outline_layout.setSpacing(6)
        outline_layout.setColumnStretch(1, 1)

        self.outline_check = QCheckBox("Enable Outline")
        self.outline_check.setChecked(DEFAULT_CROSSHAIR.outline_enabled)
        self.outline_check.toggled.connect(self._on_outline_toggled)
        outline_layout.addWidget(self.outline_check, 0, 0, 1, 2)

        outline_layout.addWidget(QLabel("Outline Color:"), 1, 0)
        self.outline_color_btn = ColorButton(DEFAULT_CROSSHAIR.outline_color)
        self.outline_color_btn.color_changed.connect(self._on_outline_color_changed)
        outline_layout.addWidget(self.outline_color_btn, 1, 1)

        self.outline_thickness_control = SliderSpinBox(
            "Outline Thickness", VALIDATION_RANGES["outline_thickness"][0],
            VALIDATION_RANGES["outline_thickness"][1],
            DEFAULT_CROSSHAIR.outline_thickness, "px"
        )
        outline_layout.addWidget(self.outline_thickness_control, 2, 0, 1, 2)

        layout.addWidget(outline_group)

        # Special styles group
        style_group = QGroupBox("Special Styles")
        style_layout = QVBoxLayout(style_group)
        style_layout.setSpacing(6)

        self.center_dot_check = QCheckBox("Center Dot")
        self.center_dot_check.setChecked(DEFAULT_CROSSHAIR.center_dot)
        self.center_dot_check.toggled.connect(self._emit_settings)
        style_layout.addWidget(self.center_dot_check)

        self.t_style_check = QCheckBox("T-Style (hide top line)")
        self.t_style_check.setChecked(DEFAULT_CROSSHAIR.t_style)
        self.t_style_check.toggled.connect(self._emit_settings)
        style_layout.addWidget(self.t_style_check)

        layout.addWidget(style_group)

        # CS2-specific group
        cs2_group = QGroupBox("CS2 Settings (for share codes)")
        cs2_layout = QGridLayout(cs2_group)
        cs2_layout.setSpacing(6)
        cs2_layout.setColumnStretch(1, 1)

        # Style
        cs2_layout.addWidget(QLabel("Style:"), 0, 0)
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "Classic (0)",
            "Classic Static (1)",
            "Legacy (2)",
            "Legacy Static (3)",
            "Classic Dynamic (4)",
            "Follow Recoil (5)"
        ])
        self.style_combo.setCurrentIndex(DEFAULT_CROSSHAIR.style)
        self.style_combo.currentIndexChanged.connect(self._emit_settings)
        cs2_layout.addWidget(self.style_combo, 0, 1)

        # Dynamic spread limit
        self.dynamic_spread_control = FloatSliderSpinBox(
            "Dynamic Spread Limit",
            VALIDATION_RANGES["dynamic_spread_limit"][0],
            VALIDATION_RANGES["dynamic_spread_limit"][1],
            DEFAULT_CROSSHAIR.dynamic_spread_limit,
            0.01, 2, ""
        )
        cs2_layout.addWidget(self.dynamic_spread_control, 1, 0, 1, 2)

        # Split distance
        self.split_distance_control = SliderSpinBox(
            "Split Distance",
            VALIDATION_RANGES["split_distance"][0],
            VALIDATION_RANGES["split_distance"][1],
            DEFAULT_CROSSHAIR.split_distance, "px"
        )
        cs2_layout.addWidget(self.split_distance_control, 2, 0, 1, 2)

        # Inner split alpha
        self.inner_alpha_control = SliderSpinBox(
            "Inner Split Alpha",
            VALIDATION_RANGES["inner_split_alpha"][0],
            VALIDATION_RANGES["inner_split_alpha"][1],
            DEFAULT_CROSSHAIR.inner_split_alpha, ""
        )
        cs2_layout.addWidget(self.inner_alpha_control, 3, 0, 1, 2)

        # Outer split alpha
        self.outer_alpha_control = SliderSpinBox(
            "Outer Split Alpha",
            VALIDATION_RANGES["outer_split_alpha"][0],
            VALIDATION_RANGES["outer_split_alpha"][1],
            DEFAULT_CROSSHAIR.outer_split_alpha, ""
        )
        cs2_layout.addWidget(self.outer_alpha_control, 4, 0, 1, 2)

        # Split size ratio
        self.split_ratio_control = FloatSliderSpinBox(
            "Split Size Ratio",
            VALIDATION_RANGES["split_size_ratio"][0],
            VALIDATION_RANGES["split_size_ratio"][1],
            DEFAULT_CROSSHAIR.split_size_ratio,
            0.01, 2, ""
        )
        cs2_layout.addWidget(self.split_ratio_control, 5, 0, 1, 2)

        # Reference resolution
        self.ref_res_control = SliderSpinBox(
            "Reference Resolution",
            VALIDATION_RANGES["reference_resolution"][0],
            VALIDATION_RANGES["reference_resolution"][1],
            DEFAULT_CROSSHAIR.reference_resolution, "px"
        )
        cs2_layout.addWidget(self.ref_res_control, 6, 0, 1, 2)

        # Scope dot scale
        self.scope_scale_control = FloatSliderSpinBox(
            "Scope Dot Scale",
            VALIDATION_RANGES["scope_dot_scale"][0],
            VALIDATION_RANGES["scope_dot_scale"][1],
            DEFAULT_CROSSHAIR.scope_dot_scale,
            0.01, 2, ""
        )
        cs2_layout.addWidget(self.scope_scale_control, 7, 0, 1, 2)

        # Scope dot use crosshair color
        self.scope_color_check = QCheckBox("Scope Dot Uses Crosshair Color")
        self.scope_color_check.setChecked(DEFAULT_CROSSHAIR.scope_dot_use_crosshair_color)
        self.scope_color_check.toggled.connect(self._emit_settings)
        cs2_layout.addWidget(self.scope_color_check, 8, 0, 1, 2)

        layout.addWidget(cs2_group)

        # Reset button
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_requested.emit)
        layout.addWidget(self.reset_btn)

        layout.addStretch()

        # Connect all controls
        self._connect_controls()

    def _connect_controls(self):
        """Connect all control signals to emit settings changed."""
        controls = [
            self.gap_control, self.length_control, self.thickness_control,
            self.size_control, self.opacity_control, self.outline_thickness_control,
            self.dynamic_spread_control, self.split_distance_control,
            self.inner_alpha_control, self.outer_alpha_control,
            self.split_ratio_control, self.ref_res_control, self.scope_scale_control
        ]
        for ctrl in controls:
            ctrl.value_changed.connect(self._emit_settings)

    def _on_color_changed(self, color: str):
        self._emit_settings()

    def _on_outline_color_changed(self, color: str):
        self._emit_settings()

    def _on_outline_toggled(self, checked: bool):
        self.outline_color_btn.setEnabled(checked)
        self.outline_thickness_control.set_enabled(checked)
        self._emit_settings()

    def _emit_settings(self):
        """Emit current settings."""
        self._settings = self.get_settings()
        self.settings_changed.emit(self._settings)

    def get_settings(self) -> CrosshairSettings:
        """Get current settings from controls."""
        return CrosshairSettings(
            gap=self.gap_control.value(),
            length=self.length_control.value(),
            thickness=self.thickness_control.value(),
            size=self.size_control.value(),
            color=self.color_btn.get_color(),
            opacity=self.opacity_control.value(),
            outline_enabled=self.outline_check.isChecked(),
            outline_color=self.outline_color_btn.get_color(),
            outline_thickness=self.outline_thickness_control.value(),
            center_dot=self.center_dot_check.isChecked(),
            t_style=self.t_style_check.isChecked(),
            style=self.style_combo.currentIndex(),
            dynamic_spread_limit=self.dynamic_spread_control.value(),
            split_distance=self.split_distance_control.value(),
            inner_split_alpha=self.inner_alpha_control.value(),
            outer_split_alpha=self.outer_alpha_control.value(),
            split_size_ratio=self.split_ratio_control.value(),
            reference_resolution=self.ref_res_control.value(),
            scope_dot_scale=self.scope_scale_control.value(),
            scope_dot_use_crosshair_color=self.scope_color_check.isChecked(),
        )

    def _load_settings(self, settings: CrosshairSettings):
        """Load settings into controls."""
        self.gap_control.set_value(settings.gap)
        self.length_control.set_value(settings.length)
        self.thickness_control.set_value(settings.thickness)
        self.size_control.set_value(settings.size)
        self.color_btn.set_color(settings.color)
        self.opacity_control.set_value(settings.opacity)
        self.outline_check.setChecked(settings.outline_enabled)
        self.outline_color_btn.set_color(settings.outline_color)
        self.outline_thickness_control.set_value(settings.outline_thickness)
        self.center_dot_check.setChecked(settings.center_dot)
        self.t_style_check.setChecked(settings.t_style)
        self.style_combo.setCurrentIndex(settings.style)
        self.dynamic_spread_control.set_value(settings.dynamic_spread_limit)
        self.split_distance_control.set_value(settings.split_distance)
        self.inner_alpha_control.set_value(settings.inner_split_alpha)
        self.outer_alpha_control.set_value(settings.outer_split_alpha)
        self.split_ratio_control.set_value(settings.split_size_ratio)
        self.ref_res_control.set_value(settings.reference_resolution)
        self.scope_scale_control.set_value(settings.scope_dot_scale)
        self.scope_color_check.setChecked(settings.scope_dot_use_crosshair_color)

        # Update outline enabled state
        self._on_outline_toggled(settings.outline_enabled)

    def load_settings(self, settings: CrosshairSettings):
        """Public method to load settings."""
        self._load_settings(settings)
        self._emit_settings()