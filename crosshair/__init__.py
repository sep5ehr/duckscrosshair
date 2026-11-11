"""Crosshair package - models, rendering, validation, and share code handling."""

from crosshair.models import (
    CrosshairSettings,
    OverlaySettings,
    ShortcutSettings,
    AppSettings,
)
from crosshair.validation import (
    validate_crosshair_settings,
    ValidationResult,
)
from crosshair.renderer import (
    CrosshairRenderer,
    PreviewWidget,
    RenderConfig,
)
from crosshair.conversion import (
    sharecode_to_internal,
    internal_to_sharecode,
    import_share_code,
    export_share_code,
)
from crosshair.sharecode import (
    CS2ShareCodec,
    DecodeResult,
    EncodeResult,
    decode_share_code,
    encode_share_code,
    validate_share_code,
)

__all__ = [
    # Models
    "CrosshairSettings",
    "OverlaySettings",
    "ShortcutSettings",
    "AppSettings",
    # Validation
    "validate_crosshair_settings",
    "ValidationResult",
    # Renderer
    "CrosshairRenderer",
    "PreviewWidget",
    "RenderConfig",
    # Conversion
    "sharecode_to_internal",
    "internal_to_sharecode",
    "import_share_code",
    "export_share_code",
    # Share code
    "CS2ShareCodec",
    "DecodeResult",
    "EncodeResult",
    "decode_share_code",
    "encode_share_code",
    "validate_share_code",
]
