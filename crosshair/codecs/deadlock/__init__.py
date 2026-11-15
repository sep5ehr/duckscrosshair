"""Deadlock codec facade."""

from __future__ import annotations

from crosshair.codecs.base import CodecResult, GameCodec
from crosshair.codecs.deadlock.decoder import decode_deadlock_crosshair
from crosshair.codecs.deadlock.encoder import encode_deadlock_crosshair
from crosshair.codecs.deadlock.schema import PREFIX


class DeadlockCodec(GameCodec):
    game_id = "deadlock"
    display_name = "Deadlock"
    encodable_formats = ("deadlock-reticle",)
    default_format = "deadlock-reticle"

    def matches_prefix(self, code: str) -> bool:
        return (code or "").strip().startswith(PREFIX)

    def decode(self, code: str) -> CodecResult:
        return decode_deadlock_crosshair(code)

    def encode(self, settings: dict, format: str = None) -> CodecResult:
        return encode_deadlock_crosshair(settings)


DEADLOCK_CODEC = DeadlockCodec()

__all__ = ["DeadlockCodec", "DEADLOCK_CODEC", "decode_deadlock_crosshair",
           "encode_deadlock_crosshair", "PREFIX"]
