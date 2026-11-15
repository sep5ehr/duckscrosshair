"""Registry of all game codecs."""

from __future__ import annotations

from crosshair.codecs.base import GameCodec

GAME_CODECS = {}


def register(codec: GameCodec) -> None:
    GAME_CODECS[codec.game_id] = codec


def get_codec(game_id: str) -> GameCodec:
    return GAME_CODECS[game_id]


def list_games() -> list:
    return list(GAME_CODECS.keys())


# Import game codecs last to avoid circular imports.
from crosshair.codecs.cs2 import CS2_CODEC
from crosshair.codecs.valorant import VALORANT_CODEC
from crosshair.codecs.deadlock import DEADLOCK_CODEC

for _c in (CS2_CODEC, VALORANT_CODEC, DEADLOCK_CODEC):
    register(_c)
