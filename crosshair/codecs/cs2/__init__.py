"""CS2 codec facade: prefix matching + decode/encode entry points."""

from __future__ import annotations

from crosshair.codecs.base import CodecResult, GameCodec
from crosshair.codecs.cs2.decoder import (
    decode_cs2_crosshair,
    is_cs2_container,
    is_legacy_container,
)
from crosshair.codecs.cs2.encoder import encode_cs2_crosshair
from crosshair.codecs.cs2.schema import ALL_FORMATS


class Cs2Codec(GameCodec):
    game_id = "cs2"
    display_name = "Counter-Strike 2"
    encodable_formats = ALL_FORMATS
    default_format = "cs2-v1"

    def matches_prefix(self, code: str) -> bool:
        code = (code or "").strip()
        return is_legacy_container(code) or is_cs2_container(code)

    def decode(self, code: str) -> CodecResult:
        return decode_cs2_crosshair(code)

    def encode(self, settings: dict, format: str = None) -> CodecResult:
        return encode_cs2_crosshair(settings, format or self.default_format)


CS2_CODEC = Cs2Codec()

__all__ = [
    "Cs2Codec",
    "CS2_CODEC",
    "decode_cs2_crosshair",
    "encode_cs2_crosshair",
    "is_cs2_container",
    "is_legacy_container",
    "ALL_FORMATS",
]
