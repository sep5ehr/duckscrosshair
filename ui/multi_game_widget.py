"""Multi-game share code widget: detect, import, export, convert (CS2/VALORANT/Deadlock)."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QApplication, QListWidget,
)

from crosshair.models import CrosshairSettings
from crosshair.core import (
    detect_crosshair_format, convert_crosshair, encode_universal,
)
from crosshair.core.app_model import universal_to_app, app_to_universal
from crosshair.codecs.registry import GAME_CODECS, list_games

GAME_LABELS = {"cs2": "Counter-Strike 2", "valorant": "VALORANT", "deadlock": "Deadlock"}


class MultiGameWidget(QWidget):
    """Import/export/convert share codes for all supported games."""

    settings_imported = Signal(object, list, str)   # CrosshairSettings, warnings, format
    code_exported = Signal(str, list)               # code, warnings
    presets_changed = Signal(list)                  # saved crosshair presets (persisted by parent)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_settings: CrosshairSettings = CrosshairSettings()
        self._last_universal = None
        self._presets: list = []   # [{"name": str, "settings": dict}]
        self._setup_ui()

    def set_current_settings(self, settings: CrosshairSettings):
        self._current_settings = settings

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # --- game & format selection ---
        sel_group = QGroupBox("Game")
        sel_layout = QHBoxLayout(sel_group)
        sel_layout.addWidget(QLabel("Game:"))
        self.game_combo = QComboBox()
        for gid in list_games():
            self.game_combo.addItem(GAME_LABELS.get(gid, gid), gid)
        self.game_combo.currentIndexChanged.connect(self._on_game_changed)
        sel_layout.addWidget(self.game_combo)
        sel_layout.addWidget(QLabel("Output format:"))
        self.format_combo = QComboBox()
        sel_layout.addWidget(self.format_combo)
        sel_layout.addStretch()
        layout.addWidget(sel_group)
        self._on_game_changed(0)

        # --- import ---
        imp_group = QGroupBox("Import / Decode (auto-detect)")
        imp_layout = QVBoxLayout(imp_group)
        row = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText(
            "Paste any code: CSGO-..., CS..., 0;... (VALORANT), DL.... (Deadlock)")
        self.code_input.setClearButtonEnabled(True)
        self.code_input.returnPressed.connect(self._on_import)
        row.addWidget(self.code_input)
        self.import_btn = QPushButton("Import")
        self.import_btn.clicked.connect(self._on_import)
        row.addWidget(self.import_btn)
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self._on_validate)
        row.addWidget(self.validate_btn)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._on_clear)
        row.addWidget(self.clear_btn)
        imp_layout.addLayout(row)
        self.format_label = QLabel("Detected format: —")
        self.format_label.setStyleSheet("color: #888; font-size: 11px;")
        imp_layout.addWidget(self.format_label)
        layout.addWidget(imp_group)

        # --- export ---
        exp_group = QGroupBox("Export")
        exp_layout = QVBoxLayout(exp_group)
        row2 = QHBoxLayout()
        self.encode_btn = QPushButton("Encode / Export")
        self.encode_btn.clicked.connect(self._on_encode)
        row2.addWidget(self.encode_btn)
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self._on_copy)
        row2.addWidget(self.copy_btn)
        row2.addStretch()
        exp_layout.addLayout(row2)
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(60)
        self.output_text.setPlaceholderText("Generated share code appears here...")
        self.output_text.setStyleSheet("font-family: monospace;")
        exp_layout.addWidget(self.output_text)
        layout.addWidget(exp_group)

        # --- convert ---
        conv_group = QGroupBox("Convert to another game")
        conv_layout = QVBoxLayout(conv_group)
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Target:"))
        self.target_combo = QComboBox()
        for gid in list_games():
            self.target_combo.addItem(GAME_LABELS.get(gid, gid), gid)
        row3.addWidget(self.target_combo)
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self._on_convert)
        row3.addWidget(self.convert_btn)
        row3.addStretch()
        conv_layout.addLayout(row3)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setMaximumHeight(110)
        self.report_text.setPlaceholderText("Conversion report appears here...")
        conv_layout.addWidget(self.report_text)
        layout.addWidget(conv_group)

        # --- saved crosshairs (built in the app) ---
        presets_group = QGroupBox("Saved Crosshairs (this app)")
        presets_layout = QVBoxLayout(presets_group)
        self.presets_list = QListWidget()
        self.presets_list.setMaximumHeight(100)
        presets_layout.addWidget(self.presets_list)
        presets_row = QHBoxLayout()
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("Preset name...")
        presets_row.addWidget(self.preset_name_edit)
        self.save_preset_btn = QPushButton("Save Current")
        self.save_preset_btn.setToolTip("Save the crosshair currently built in the app")
        self.save_preset_btn.clicked.connect(self._on_save_preset)
        presets_row.addWidget(self.save_preset_btn)
        self.load_preset_btn = QPushButton("Load")
        self.load_preset_btn.clicked.connect(self._on_load_preset)
        presets_row.addWidget(self.load_preset_btn)
        self.delete_preset_btn = QPushButton("Delete")
        self.delete_preset_btn.clicked.connect(self._on_delete_preset)
        presets_row.addWidget(self.delete_preset_btn)
        presets_layout.addLayout(presets_row)
        hint = QLabel("Use Encode / Export above to turn the current app crosshair into a "
                      "CS2 / VALORANT / Deadlock share code.")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        hint.setWordWrap(True)
        presets_layout.addWidget(hint)
        layout.addWidget(presets_group)

        # --- warnings ---
        self.warnings_text = QTextEdit()
        self.warnings_text.setReadOnly(True)
        self.warnings_text.setMaximumHeight(80)
        self.warnings_text.setPlaceholderText("Warnings and validation errors appear here...")
        self.warnings_text.setStyleSheet(
            "QTextEdit { background-color: #fff8e1; border: 1px solid #ffc107; }")
        layout.addWidget(self.warnings_text)

        layout.addStretch()

    # ------------------------------------------------------------------
    # saved presets
    def set_saved_crosshairs(self, presets: list):
        self._presets = list(presets or [])
        self._refresh_presets_list()

    def get_saved_crosshairs(self) -> list:
        return list(self._presets)

    def _refresh_presets_list(self):
        self.presets_list.clear()
        for p in self._presets:
            self.presets_list.addItem(p.get("name", "unnamed"))

    def _on_save_preset(self):
        from crosshair.models import CrosshairSettings
        name = self.preset_name_edit.text().strip() or "Crosshair %d" % (len(self._presets) + 1)
        settings = self._current_settings
        if not isinstance(settings, CrosshairSettings):
            settings = CrosshairSettings()
        entry = {"name": name, "settings": settings.to_dict()}
        # replace existing with same name
        self._presets = [p for p in self._presets if p.get("name") != name]
        self._presets.append(entry)
        self._refresh_presets_list()
        self.presets_changed.emit(self.get_saved_crosshairs())
        self._show_messages(["Saved preset '%s'" % name])

    def _on_load_preset(self):
        row = self.presets_list.currentRow()
        if row < 0 or row >= len(self._presets):
            self._show_messages(["Select a preset to load"])
            return
        entry = self._presets[row]
        settings = CrosshairSettings.from_dict(entry.get("settings", {}))
        self._current_settings = settings
        self.settings_imported.emit(settings, ["Loaded preset '%s'" % entry.get("name")],
                                    "preset")
        self._show_messages(["Loaded preset '%s'" % entry.get("name")])

    def _on_delete_preset(self):
        row = self.presets_list.currentRow()
        if row < 0 or row >= len(self._presets):
            return
        name = self._presets[row].get("name")
        del self._presets[row]
        self._refresh_presets_list()
        self.presets_changed.emit(self.get_saved_crosshairs())
        self._show_messages(["Deleted preset '%s'" % name])

    # ------------------------------------------------------------------
    def _on_game_changed(self, _index):
        gid = self.game_combo.currentData()
        codec = GAME_CODECS[gid]
        self.format_combo.clear()
        for fmt in codec.encodable_formats:
            label = fmt + (" (default)" if fmt == codec.default_format else "")
            self.format_combo.addItem(label, fmt)
        # select default
        idx = self.format_combo.findData(codec.default_format)
        if idx >= 0:
            self.format_combo.setCurrentIndex(idx)

    def _selected_format(self):
        return self.format_combo.currentData()

    def _show_messages(self, messages):
        self.warnings_text.setPlainText("\n".join(str(m) for m in messages) if messages else "")

    def _on_import(self):
        code = self.code_input.text().strip()
        det = detect_crosshair_format(code)
        if not det.valid:
            self.format_label.setText("Detected format: INVALID")
            self._show_messages([det.error or "Invalid code"])
            return
        self.format_label.setText(
            "Detected format: %s — %s" % (GAME_LABELS.get(det.game, det.game), det.format))
        # route to the matching game in the combo, keep user's format choice for export
        idx = self.game_combo.findData(det.game)
        if idx >= 0:
            self.game_combo.setCurrentIndex(idx)
        self._show_messages(det.warnings)
        from crosshair.core import decode_to_universal
        _det, universal, _report = decode_to_universal(code)
        if universal is not None:
            self._last_universal = universal
            app_settings = universal_to_app(universal)
            self.settings_imported.emit(app_settings, list(det.warnings),
                                        "%s %s" % (det.game, det.format))

    def _on_validate(self):
        code = self.code_input.text().strip()
        det = detect_crosshair_format(code)
        if det.valid:
            self.format_label.setText(
                "Detected format: %s — %s (valid)" % (GAME_LABELS.get(det.game, det.game), det.format))
            self._show_messages(det.warnings)
        else:
            self.format_label.setText("Detected format: INVALID")
            self._show_messages([det.error or "Invalid code"])

    def _on_clear(self):
        self.code_input.clear()
        self.output_text.clear()
        self.report_text.clear()
        self.format_label.setText("Detected format: —")
        self._show_messages([])

    def _on_encode(self):
        gid = self.game_combo.currentData()
        fmt = self._selected_format()
        if self._last_universal is not None and self._last_universal.metadata.get("source_game") == gid:
            universal = self._last_universal
        else:
            universal = app_to_universal(self._current_settings, gid)
        result = encode_universal(universal, gid, fmt)
        if not result.success:
            self._show_messages([result.error or "Encoding failed"])
            return
        self.output_text.setPlainText(result.code)
        self._show_messages(result.warnings)
        self.code_exported.emit(result.code, list(result.warnings))

    def _on_copy(self):
        code = self.output_text.toPlainText().strip()
        if code:
            QApplication.clipboard().setText(code)

    def _on_convert(self):
        code = self.code_input.text().strip()
        target = self.target_combo.currentData()
        result = convert_crosshair(code, target)
        if not result.success:
            self.report_text.setPlainText(
                "Conversion failed: %s\n\n%s" % (result.error, result.report.summary() if result.report else ""))
            return
        rep = result.report
        lines = [rep.summary(), ""]
        lines.append("Converted: " + (", ".join(rep.converted) or "—"))
        lines.append("Unsupported in target: " + (", ".join(rep.unsupported) or "—"))
        lines.append("Defaulted: " + (", ".join(rep.defaulted) or "—"))
        lines.append("Unrepresentable: " + (", ".join(rep.unrepresentable) or "—"))
        if rep.warnings:
            lines.append("Warnings: " + "; ".join(rep.warnings))
        lines.append("")
        lines.append("Code: " + result.code)
        self.report_text.setPlainText("\n".join(lines))
        self.output_text.setPlainText(result.code)
