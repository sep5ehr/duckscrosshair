"""Core multi-game API: detection, universal model, conversion, registry."""

from crosshair.core.universal import UniversalCrosshair
from crosshair.core.detect import detect_crosshair_format
from crosshair.core.convert import (
    ConversionResult,
    ConversionReport,
    decode_to_universal,
    convert_crosshair,
    encode_universal,
)
from crosshair.codecs.registry import get_codec, list_games, GAME_CODECS

__all__ = [
    "UniversalCrosshair",
    "detect_crosshair_format",
    "ConversionResult",
    "ConversionReport",
    "decode_to_universal",
    "convert_crosshair",
    "encode_universal",
    "get_codec",
    "list_games",
    "GAME_CODECS",
]
