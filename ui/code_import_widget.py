"""CS2 share code import/export widget."""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox,
    QMessageBox, QApplication, QSizePolicy
)

from crosshair.sharecode import (
    decode_share_code, encode_share_code, validate_share_code,
    DecodeResult, EncodeResult
)
from crosshair.conversion import import_share_code, export_share_code
from crosshair.models import CrosshairSettings


class CodeImportWidget(QWidget):
    """Widget for importing and exporting CS2 share codes."""

    # Signals
    import_requested = Signal(str)  # share_code
    export_requested = Signal()  # triggers export from current settings
    settings_imported = Signal(CrosshairSettings, list, str)  # settings, warnings, format_name
    code_exported = Signal(str, list)  # share_code, warnings
    validation_result = Signal(bool, str, list)  # valid, format_name, warnings

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_settings: CrosshairSettings = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Import section
        import_group = QGroupBox("Import Share Code")
        import_layout = QVBoxLayout(import_group)
        import_layout.setSpacing(6)

        # Code input
        input_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Paste CS2 share code (e.g., CSGO-ABCDEF...)")
        self.code_input.setClearButtonEnabled(True)
        self.code_input.returnPressed.connect(self._on_import_clicked)
        input_layout.addWidget(self.code_input)

        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self._on_import_clicked)
        input_layout.addWidget(self.import_btn)

        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self._on_validate_clicked)
        input_layout.addWidget(self.validate_btn)

        import_layout.addLayout(input_layout)

        # Import actions
        action_layout = QHBoxLayout()
        self.decode_btn = QPushButton("Decode")
        self.decode_btn.clicked.connect(self._on_decode_clicked)
        action_layout.addWidget(self.decode_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        action_layout.addWidget(self.clear_btn)

        action_layout.addStretch()
        import_layout.addLayout(action_layout)

        # Detected format display
        self.format_label = QLabel("Format: —")
        self.format_label.setStyleSheet("color: #888; font-size: 11px;")
        import_layout.addWidget(self.format_label)

        layout.addWidget(import_group)

        # Export section
        export_group = QGroupBox("Export Share Code")
        export_layout = QVBoxLayout(export_group)
        export_layout.setSpacing(6)

        # Version selector
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Format Version:"))
        self.version_combo = QComboBox()
        self.version_combo.addItems(["CS2 Current (v1)"])
        version_layout.addWidget(self.version_combo)
        version_layout.addStretch()
        export_layout.addLayout(version_layout)

        # Export actions
        export_action_layout = QHBoxLayout()
        self.encode_btn = QPushButton("Encode / Export")
        self.encode_btn.clicked.connect(self._on_encode_clicked)
        export_action_layout.addWidget(self.encode_btn)

        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._on_copy_clicked)
        export_action_layout.addWidget(self.copy_btn)

        export_action_layout.addStretch()
        export_layout.addLayout(export_action_layout)

        # Generated code display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(60)
        self.output_text.setPlaceholderText("Generated share code will appear here...")
        self.output_text.setStyleSheet("font-family: monospace; font-size: 12px;")
        export_layout.addWidget(self.output_text)

        layout.addWidget(export_group)

        # Warnings/errors display
        self.warnings_text = QTextEdit()
        self.warnings_text.setReadOnly(True)
        self.warnings_text.setMaximumHeight(80)
        self.warnings_text.setPlaceholderText("Warnings and info will appear here...")
        self.warnings_text.setStyleSheet("""
            QTextEdit {
                background-color: #fff8e1;
                border: 1px solid #ffc107;
                border-radius: 4px;
                color: #5d4037;
            }
        """)
        layout.addWidget(self.warnings_text)

        layout.addStretch()

    def set_current_settings(self, settings: CrosshairSettings):
        """Update the current settings for export."""
        self._current_settings = settings

    def _on_import_clicked(self):
        """Handle import button click."""
        code = self.code_input.text().strip()
        if not code:
            self._show_warnings(["Please enter a share code"])
            return

        self._do_import(code)

    def _on_validate_clicked(self):
        """Handle validate button click."""
        code = self.code_input.text().strip()
        if not code:
            self._show_warnings(["Please enter a share code to validate"])
            return

        valid, format_name, warnings = validate_share_code(code)
        self.validation_result.emit(valid, format_name, warnings)

        if valid:
            self.format_label.setText(f"Format: {format_name} ✓")
            self.format_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        else:
            self.format_label.setText(f"Format: Invalid")
            self.format_label.setStyleSheet("color: #f44336; font-size: 11px;")

        self._show_warnings(warnings)

    def _on_decode_clicked(self):
        """Handle decode button click."""
        code = self.code_input.text().strip()
        if not code:
            self._show_warnings(["Please enter a share code"])
            return

        self._do_import(code)

    def _do_import(self, code: str):
        """Perform the import operation."""
        settings, warnings, format_name = import_share_code(code)

        if settings is None:
            self.format_label.setText("Format: Invalid")
            self.format_label.setStyleSheet("color: #f44336; font-size: 11px;")
            self._show_warnings(warnings)
            return

        self.format_label.setText(f"Format: {format_name}")
        self.format_label.setStyleSheet("color: #4caf50; font-size: 11px;")

        self.settings_imported.emit(settings, warnings, format_name)
        self.import_requested.emit(code)
        self._show_warnings(warnings)

    def _on_clear_clicked(self):
        """Clear the input and output."""
        self.code_input.clear()
        self.output_text.clear()
        self.warnings_text.clear()
        self.format_label.setText("Format: —")
        self.format_label.setStyleSheet("color: #888; font-size: 11px;")

    def _on_encode_clicked(self):
        """Handle encode/export button click."""
        if self._current_settings is None:
            self._show_warnings(["No current settings to export"])
            return

        share_code, warnings = export_share_code(self._current_settings)

        if share_code is None:
            self.output_text.setPlainText("Encoding failed")
            self._show_warnings(warnings)
            return

        self.output_text.setPlainText(share_code)
        self.code_exported.emit(share_code, warnings)
        self.export_requested.emit()
        self._show_warnings(warnings)

    def _on_copy_clicked(self):
        """Copy generated code to clipboard."""
        code = self.output_text.toPlainText().strip()
        if code and code != "Encoding failed":
            clipboard = QApplication.clipboard()
            clipboard.setText(code)
            self._show_warnings(["Copied to clipboard!"])

    def _show_warnings(self, warnings: list):
        """Display warnings in the text area."""
        if not warnings:
            self.warnings_text.clear()
            return

        text = "\n".join(f"• {w}" for w in warnings)
        self.warnings_text.setPlainText(text)

    def set_generated_code(self, code: str):
        """Set the generated code display (from external encode)."""
        self.output_text.setPlainText(code)