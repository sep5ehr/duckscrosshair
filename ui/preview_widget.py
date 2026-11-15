"""Enhanced preview widget with background and zoom controls."""

from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QSpinBox, QGroupBox, QCheckBox
)

from crosshair.renderer import CrosshairRenderer, RenderConfig


class PreviewWidget(QWidget):
    """Live preview widget with background selection and zoom."""

    background_changed = Signal(str)
    zoom_changed = Signal(float)

    def __init__(self, renderer: CrosshairRenderer, parent=None):
        super().__init__(parent)
        self.renderer = renderer
        self.config = RenderConfig()
        self.setMinimumSize(250, 250)
        self.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Expanding
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_background(self, background: str):
        """Set preview background type."""
        if background in ("light", "dark", "checkerboard"):
            self.config.background = background
            self.background_changed.emit(background)
            self.update()

    def set_zoom(self, zoom: float):
        """Set preview zoom level."""
        self.config.zoom = max(0.25, min(5.0, zoom))
        self.zoom_changed.emit(self.config.zoom)
        self.update()

    def set_show_center_mark(self, show: bool):
        """Show/hide center alignment mark."""
        self.config.show_center_mark = show
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = QRectF(self.rect())
        self.renderer.paint(painter, rect, self.config)

    def sizeHint(self):
        return QSize(300, 300)


class PreviewControls(QWidget):
    """Controls for the preview widget."""

    background_changed = Signal(str)
    zoom_changed = Signal(float)
    center_mark_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Background selection
        bg_group = QGroupBox("Preview Background")
        bg_layout = QHBoxLayout(bg_group)
        bg_layout.setSpacing(8)

        bg_label = QLabel("Background:")
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["Light", "Dark", "Checkerboard"])
        self.bg_combo.setCurrentText("Checkerboard")
        self.bg_combo.currentTextChanged.connect(
            lambda t: self.background_changed.emit(t.lower())
        )

        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_combo)
        bg_layout.addStretch()

        layout.addWidget(bg_group)

        # Zoom control
        zoom_group = QGroupBox("Zoom")
        zoom_layout = QHBoxLayout(zoom_group)
        zoom_layout.setSpacing(8)

        zoom_label = QLabel("Zoom:")
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(25, 500)  # 0.25x to 5.0x
        self.zoom_slider.setValue(100)
        self.zoom_slider.setTickInterval(25)
        self.zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.zoom_slider.valueChanged.connect(
            lambda v: self.zoom_changed.emit(v / 100.0)
        )

        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(25, 500)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setValue(100)
        self.zoom_spin.valueChanged.connect(
            lambda v: self.zoom_changed.emit(v / 100.0)
        )
        self.zoom_slider.valueChanged.connect(self.zoom_spin.setValue)
        self.zoom_spin.valueChanged.connect(self.zoom_slider.setValue)

        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(self.zoom_spin)

        layout.addWidget(zoom_group)

        # Center mark toggle
        self.center_mark_check = QCheckBox("Show center mark")
        self.center_mark_check.setChecked(False)
        self.center_mark_check.toggled.connect(self.center_mark_toggled.emit)
        layout.addWidget(self.center_mark_check)

        layout.addStretch()