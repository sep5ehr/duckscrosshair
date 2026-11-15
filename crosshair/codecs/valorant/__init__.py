"""VALORANT codec facade."""

from __future__ import annotations

from crosshair.codecs.base import CodecResult, GameCodec
from crosshair.codecs.valorant.decoder import decode_valorant_crosshair
from crosshair.codecs.valorant.encoder import encode_valorant_crosshair


class ValorantCodec(GameCodec):
    game_id = "valorant"
    display_name = "VALORANT"
    encodable_formats = ("valorant-native",)
    default_format = "valorant-native"

    def matches_prefix(self, code: str) -> bool:
        code = (code or "").strip()
        return code == "0" or code.startswith("0;")

    def decode(self, code: str) -> CodecResult:
        return decode_valorant_crosshair(code)

    def encode(self, settings: dict, format: str = None) -> CodecResult:
        return encode_valorant_crosshair(settings)


VALORANT_CODEC = ValorantCodec()

__all__ = ["ValorantCodec", "VALORANT_CODEC", "decode_valorant_crosshair",
           "encode_valorant_crosshair"]
