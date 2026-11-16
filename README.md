# Crosshair Overlay

<p align="center">
  <img src="resources/icons/icon.png" alt="Crosshair Overlay" width="120"/>
</p>

<p align="center">
  <b>A customizable crosshair overlay for Windows desktop applications.</b><br/>
  <b>Full support for Counter-Strike 2 (CS2), VALORANT, and Deadlock share codes.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt" alt="PySide6"/>
</p>

---

## 📖 About

**Crosshair Overlay** is a transparent, click-through, always-on-top crosshair overlay for Windows. It is designed primarily for **shooting games** to help with **no-scope sniper shots** by keeping a static crosshair fixed on your screen.

The application allows you to fully customize your crosshair, save presets, and import/export share codes for **Counter-Strike 2 (CS2)**, **VALORANT**, and **Deadlock**.

## ✨ Features

- 🎯 **Transparent Desktop Overlay**: Borderless, click-through, always-on-top crosshair.
- 🔧 **Full Customization**: Gap, length, thickness, dot size, global **Scale**, colors, outline, center dot, T-style, and more.
- 👁️ **Live Preview**: Real-time preview in the settings window with background options and zoom.
- 💾 **Saved Crosshairs**: Save your crosshair as a named preset, load/delete presets.
- 🔄 **Multi-Game Share Codes**:
  - **CS2**: legacy-v1, legacy-v3, legacy-v4, native cs2-v1.
  - **VALORANT**: profile codes.
  - **Deadlock**: `DL.` reticle codes.
  - Auto-detection, cross-game conversion, and conversion reports.
- 🖥️ **Multi-Monitor Support**: Select which monitor displays the overlay.
- ⌨️ **Global Hotkeys**: Toggle overlay (**F8**) and settings (**F9**) system-wide.
- 📌 **System Tray**: Quick access to settings, toggle, and exit.
- 💾 **Persistent Settings**: Auto-saved to `%APPDATA%/CrosshairOverlay/settings.json`.
- 📏 **DPI Aware**: Handles Windows display scaling correctly.

## 🚀 Getting Started

### From Source


# Clone or download the project
git clone https://github.com/sep5ehr/duckscrosshair.git
cd duckscrosshair

# Create virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run the application
python main.py
Building Executable

# Install PyInstaller
pip install pyinstaller

# Build directory-based (recommended for testing)
pyinstaller --noconfirm --clean --onedir --windowed --name "CrosshairOverlay" main.py

# Or build single-file
pyinstaller --noconfirm --clean --onefile --windowed --name "CrosshairOverlay" main.py
The executable will be in dist/CrosshairOverlay/.

⚠️ PyInstaller requires an .ico file for the executable icon. Convert your PNG to ICO first (using Pillow or an online converter).

🎮 Usage
Launch: Run python main.py or the built executable.

Overlay: Appears at screen center on the primary monitor.

Settings: Press F9 or click the tray icon → Settings.

Toggle Overlay: Press F8 or use the tray menu.

Customize: Adjust all crosshair properties in the settings window.

Import / Export Codes: Paste any supported code (CS2, VALORANT, Deadlock) in the Games tab — the format is auto-detected — then Import; adjust settings and Encode/Export, or convert between games.

⌨️ Default Hotkeys
Hotkey	Action
F8	Toggle overlay on/off
F9	Show/hide settings window
Ctrl+Shift+Q	Force close the app
Esc	Close dialogs / cancel operations
Hotkeys can be customized in the Shortcuts tab. Click a shortcut field and press any key combination or mouse button (MouseLeft, MouseRight, MouseMiddle, MouseX1/Mouse4, MouseX2/Mouse5) to bind it.

🧩 Multi-Game Codec Architecture
Independent, verified codecs per game (the old app-internal codec in crosshair/sharecode/ is kept untouched for backward compatibility):


crosshair/
  codecs/
    base.py            # CodecResult / DetectionResult / ConversionReport / GameCodec
    registry.py        # game codec registry
    cs2/               # ported from the verified csgo-sharecode@7.0.1 reference
      formats.py       # base-57 containers, checksum, legacy CSGO-... vs native CS...
      schema.py        # legacy-v1 / legacy-v3 / legacy-v4 / cs2-v1 dataclasses
      decoder.py       # decode_cs2_crosshair(code) - auto-detects container+version
      encoder.py       # encode_cs2_crosshair(settings, format="cs2-v1")
    valorant/
      parser.py        # lossless semicolon-token parser/serializer
      schema.py        # P/A/S sections, full documented key map, color presets
      decoder.py       # decode_valorant_crosshair(code)
      encoder.py       # encode_valorant_crosshair(settings)
    deadlock/
      protobuf_wire.py # generic protobuf wire parse/serialize (no invented layout)
      schema.py        # DL. prefix + base64url, strict validation
      decoder.py       # decode_deadlock_crosshair(code) - lossless raw + wire fields
      encoder.py       # encode_deadlock_crosshair(settings)
  core/
    universal.py       # normalized UniversalCrosshair model (+game_extensions+metadata)
    detect.py          # detect_crosshair_format(code)
    convert.py         # convert_crosshair(code, target_game) with ConversionReport
    app_model.py       # bridge to the app's CrosshairSettings
    validation.py
Pipeline for conversion: source code → source decoder → universal model → target encoder → target code. The original code is always kept in metadata; conversion reports list converted / unsupported / defaulted / unrepresentable properties. The settings window has a new Games tab.

Deadlock Support Scope (Honest)
DL. codes are validated (prefix + base64url) and round-trip byte-identically (raw payload preserved, generic protobuf wire parsing included). Per-field game semantics of the DL. payload could not be verified against a reference implementation in this environment and are therefore reported as best-effort/unverified rather than guessed. Converting a non-Deadlock code into a DL. code is refused (reported as unrepresentable) instead of fabricating a payload.

📄 CS2 Share Code Format
The application implements the current CS2 share code format (version 1). The real game formats are implemented (ported from the verified csgo-sharecode reference):

Format	Container	Notes
legacy-v1	CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx	CS:GO era
legacy-v3	same legacy container	pixel values + screen height
legacy-v4	same legacy container	adds outline mode + Static Square
cs2-v1	CS + 44 chars, no dashes	native CS2: outline RGBA, scope dot prefs, negative gap, 0.01-step alphas
Both containers are base-57 big numbers (dictionary excludes 0, 1, I, g, l, _), byte 0 = checksum sum(bytes[1:]) % 256, byte 1 = version. Formats are identified by container + version, never by version alone (legacy-v1 and cs2-v1 both store version byte 1).

Supported Operations
✅ Decode all four formats (real game fixtures in tests/fixtures.py).

✅ Encode all four formats (new codes default to cs2-v1).

✅ Byte-exact round-trip of every real fixture.

✅ Validation: malformed containers, bad checksums, unsupported versions (incl. legacy-v2), screen height 0, CS2-style clamping.

✅ Codes generated by this app's previous internal codec still import (detected as app-legacy-v1).

⚙️ Settings
Settings are automatically saved to:


%APPDATA%\CrosshairOverlay\settings.json
Example structure:

json
{
  "schema_version": 1,
  "overlay": {
    "enabled": true,
    "click_through": true,
    "always_on_top": true,
    "monitor_id": "primary",
    "opacity": 1.0
  },
  "crosshair": {
    "gap": 2,
    "length": 6,
    "thickness": 2,
    "size": 6,
    "color": "#00FF00",
    "opacity": 1.0,
    "outline_enabled": true,
    "outline_color": "#000000",
    "outline_thickness": 1,
    "center_dot": false,
    "t_style": false,
    "style": 4,
    "dynamic_spread_limit": 0.0,
    "split_distance": 7,
    "inner_split_alpha": 255,
    "outer_split_alpha": 255,
    "split_size_ratio": 0.5,
    "reference_resolution": 1920,
    "scope_dot_scale": 1.0,
    "scope_dot_use_crosshair_color": false
  },
  "shortcuts": {
    "toggle_overlay": "F8",
    "toggle_settings": "F9"
  },
  "last_share_code": ""
}
⚠️ Overlay Limitations
Important: This is a standard Windows desktop overlay. It works by creating a transparent, click-through, always-on-top window.

Works With:
✅ Windowed applications

✅ Borderless windowed applications

✅ Most desktop applications

✅ Games running in Borderless Windowed mode

Does NOT Work With:
❌ Exclusive fullscreen applications (many games)

❌ Applications that bypass desktop composition

❌ Applications with overlay blocking (some anti-cheat)

This is a Windows limitation, not a bug. No code injection, memory reading, or anti-cheat bypass is performed.

Troubleshooting Overlay Visibility
Ensure "Enable Overlay" is checked in the General tab.

Try disabling "Click Through" temporarily.

Check the correct monitor is selected.

For games: Use Borderless Windowed mode, not Exclusive Fullscreen.

Some anti-cheat software may block overlays.

📁 Project Structure

duckscrosshair/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore rules
├── CrosshairOverlay.spec   # PyInstaller spec file
├── app/                    # Application core
├── crosshair/              # Crosshair logic, codecs, models
├── overlay/                # Overlay window
├── winplatform/            # Platform-specific (hotkeys, etc.)
├── storage/                # Settings persistence
├── ui/                     # User interface
├── resources/              # Icons, assets
├── tests/                  # Unit tests
└── build/                  # Build artifacts
🧪 Running Tests

# Run all tests
pytest

# Run specific test file
pytest tests/test_round_trip.py -v

# Run with coverage
pytest --cov=crosshair --cov=overlay --cov=storage --cov=platform --cov=ui --cov=app
🛠️ Development
Architecture
The application follows a modular architecture:

Models (crosshair/models.py): Pure data classes for settings.

Renderer (crosshair/renderer.py): Shared QPainter logic for preview and overlay.

Codec (crosshair/sharecode/): CS2 share code encoding/decoding (legacy).

Codecs (crosshair/codecs/): New multi-game codec system.

Overlay (overlay/): Transparent window with Windows API styles.

UI (ui/): Settings window with tabs for all configuration.

Storage (storage/): JSON persistence with debounced writes.

Platform (winplatform/): Windows global hotkeys via native API.

📄 License
This project is licensed under the MIT License — see the LICENSE file for details.

🙏 Acknowledgments
CS2 share code format research from:

akiver/csgo-sharecode

JDD310/CS2-Crosshair-Converter

setposgg/cs2-crosshair

PySide6/Qt for the excellent GUI framework.

<p align="center">Made with ❤️ for the gaming community</p>
