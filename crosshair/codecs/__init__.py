"""Multi-game crosshair share-code codecs (CS2, VALORANT, Deadlock).

Each game lives in its own subpackage with an independent encoder, decoder,
parser and schema. The shared application never assumes games share a native
format; everything goes through `crosshair.core` (universal model, detection,
conversion).
"""

from crosshair.codecs.base import (
    CodecResult,
    DetectionResult,
    GameCodec,
    ConversionReport,
)
from crosshair.codecs.registry import get_codec, list_games, GAME_CODECS

__all__ = [
    "CodecResult",
    "DetectionResult",
    "GameCodec",
    "ConversionReport",
    "get_codec",
    "list_games",
    "GAME_CODECS",
]
