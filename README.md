# duckscrosshair
# Crosshair Overlay

A customizable crosshair overlay for Windows desktop applications, with full support for Counter-Strike 2 (CS2) share code import/export.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.6+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Transparent Desktop Overlay**: Borderless, click-through, always-on-top crosshair
- **Full Customization**: Gap, length, thickness, size, colors, outline, center dot, T-style
- **Live Preview**: Real-time preview in settings window with background options and zoom
- **CS2 Share Codes**: Import and export CS2 crosshair share codes (current format v1)
- **Multi-Monitor Support**: Select which monitor displays the overlay
- **Global Hotkeys**: Toggle overlay (F8) and settings (F9) system-wide
- **System Tray**: Quick access to settings, toggle, and exit
- **Persistent Settings**: Auto-saved to `%APPDATA%/CrosshairOverlay/settings.json`
- **DPI Aware**: Handles Windows display scaling correctly

## Screenshots

*[Screenshots would go here]*

## Installation

### From Source

```powershell
# Clone or download the project
cd crosshair-overlay

# Create virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Executable

```powershell
# Install PyInstaller
pip install pyinstaller

# Build directory-based (recommended for testing)
pyinstaller --noconfirm --clean --onedir --windowed --name "CrosshairOverlay" main.py

# Or build single-file
pyinstaller --noconfirm --clean --onefile --windowed --name "CrosshairOverlay" main.py
```

The executable will be in `dist/CrosshairOverlay/`.

## Usage

1. **Launch**: Run `python main.py` or the built executable
2. **Overlay**: Appears at screen center on primary monitor
3. **Settings**: Press **F9** or click tray icon → Settings
4. **Toggle Overlay**: Press **F8** or use tray menu
5. **Customize**: Adjust all crosshair properties in the settings window
6. **Import CS2 Code**: Paste a share code in the "CS2 Code" tab and click Import
7. **Export CS2 Code**: Adjust settings, go to "CS2 Code" tab, click Encode/Export

## Default Hotkeys

| Hotkey | Action |
|--------|--------|
| **F8** | Toggle overlay on/off |
| **F9** | Show/hide settings window |
| **Esc** | Close dialogs / cancel operations |

*Hotkeys can be customized in the Shortcuts tab.*

## CS2 Share Code Format

The application implements the **current CS2 share code format (version 1)**:

- **Prefix**: `CSGO-`
- **Encoding**: Custom Base32 alphabet (excludes I, L, O, 1, 0)
- **Checksum**: CRC8 (polynomial 0x1D)
- **Fields**: All CS2 crosshair settings including style, gap, length, thickness, color, outline, dot, dynamic spread, split settings, scope settings, T-style

### Supported Operations

- ✅ Decode current CS2 format (v1)
- ✅ Encode current CS2 format (v1)
- ✅ Round-trip preservation of all representable settings
- ✅ Validation with detailed error messages
- ⚠️ Legacy CS:GO formats: decode only (conversion planned)

### Example Share Code

```
CSGO-ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
```

## Settings

Settings are automatically saved to:
```
%APPDATA%\CrosshairOverlay\settings.json
```

Example structure:
```json
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
```

## Overlay Limitations

**Important**: This is a standard Windows desktop overlay. It works by creating a transparent, click-through, always-on-top window.

### Works With:
- ✅ Windowed applications
- ✅ Borderless windowed applications
- ✅ Most desktop applications
- ✅ Games running in **Borderless Windowed** mode

### Does NOT Work With:
- ❌ Exclusive fullscreen applications (many games)
- ❌ Applications that bypass desktop composition
- ❌ Applications with overlay blocking (some anti-cheat)

**This is a Windows limitation, not a bug.** No code injection, memory reading, or anti-cheat bypass is performed.

### Troubleshooting Overlay Visibility

1. Ensure "Enable Overlay" is checked in General tab
2. Try disabling "Click Through" temporarily
3. Check correct monitor is selected
4. For games: Use **Borderless Windowed** mode, not Exclusive Fullscreen
5. Some anti-cheat software may block overlays

## Project Structure

```
crosshair-overlay/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── LICENSE                 # MIT License
├── .gitignore              # Git ignore rules
├── app/                    # Application core
│   ├── __init__.py
│   ├── application.py      # Main application class
│   ├── constants.py        # Constants and defaults
│   └── state.py            # Application state
├── crosshair/              # Crosshair logic
│   ├── __init__.py
│   ├── models.py           # Data models
│   ├── validation.py       # Input validation
│   ├── renderer.py         # Shared rendering logic
│   ├── conversion.py       # Share code ↔ internal conversion
│   └── sharecode/          # CS2 share code codec
│       ├── __init__.py
│       ├── alphabet.py     # Base32 encoding
│       ├── checksum.py     # CRC8 checksum
│       ├── layouts.py      # Binary field layouts
│       ├── codec.py        # Main encode/decode
│       └── exceptions.py   # Custom exceptions
├── overlay/                # Overlay window
│   ├── __init__.py
│   ├── overlay_window.py   # Transparent overlay widget
│   ├── monitor_manager.py  # Multi-monitor handling
│   └── windows_styles.py   # Windows API styles
├── platform/               # Platform-specific
│   ├── __init__.py
│   └── hotkeys.py          # Global hotkeys (Windows)
├── storage/                # Settings persistence
│   ├── __init__.py
│   ├── settings_store.py   # JSON storage with debounce
│   └── migrations.py       # Schema migrations
├── ui/                     # User interface
│   ├── __init__.py
│   ├── settings_window.py  # Main settings window
│   ├── preview_widget.py   # Live preview with controls
│   ├── crosshair_controls.py # All crosshair sliders/inputs
│   ├── code_import_widget.py # Share code import/export
│   └── tray.py             # System tray icon
└── tests/                  # Unit tests
    ├── test_geometry.py
    ├── test_validation.py
    ├── test_settings_store.py
    ├── test_sharecode_decode.py
    ├── test_sharecode_encode.py
    └── test_round_trip.py
```

## Dependencies

- **PySide6** (Qt for Python) - GUI framework
- **pytest** - Testing framework
- **pytest-qt** - Qt testing utilities

All dependencies are in `requirements.txt`.

## Running Tests

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_round_trip.py -v

# Run with coverage
pytest --cov=crosshair --cov=overlay --cov=storage --cov=platform --cov=ui --cov=app
```

## Development

### Architecture

The application follows a modular architecture:

1. **Models** (`crosshair/models.py`): Pure data classes for settings
2. **Renderer** (`crosshair/renderer.py`): Shared QPainter logic for preview and overlay
3. **Codec** (`crosshair/sharecode/`): CS2 share code encoding/decoding
4. **Overlay** (`overlay/`): Transparent window with Windows API styles
5. **UI** (`ui/`): Settings window with tabs for all configuration
6. **Storage** (`storage/`): JSON persistence with debounced writes
7. **Platform** (`platform/`): Windows global hotkeys via native API

### Adding Features

1. Add model fields in `crosshair/models.py`
2. Add validation in `crosshair/validation.py`
3. Update renderer in `crosshair/renderer.py`
4. Add controls in `ui/crosshair_controls.py`
5. Update share code layouts in `crosshair/sharecode/layouts.py` if needed
6. Add tests in `tests/`

## Building Distribution

### PyInstaller Spec

The project includes a `CrosshairOverlay.spec` file for building:

```powershell
pyinstaller CrosshairOverlay.spec
```

### Required Resources

- Qt plugins (automatically bundled)
- Icons (generated programmatically)
- No external resource files needed

## Known Issues

1. **Exclusive Fullscreen**: Overlay won't appear over exclusive fullscreen apps
2. **High DPI**: Some scaling edge cases on multi-monitor mixed DPI setups
3. **Hotkey Conflicts**: Some keys may be reserved by system/other apps
4. **Legacy Codes**: Only current CS2 format fully supported

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- CS2 share code format research from:
  - [akiver/csgo-sharecode](https://github.com/akiver/csgo-sharecode)
  - [JDD310/CS2-Crosshair-Converter](https://github.com/JDD310/CS2-Crosshair-Converter)
  - [setposgg/cs2-crosshair](https://github.com/setposgg/cs2-crosshair)
- PySide6/Qt for the excellent GUI framework
