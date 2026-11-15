"""Base types shared by all game codecs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CodecResult:
    """Result of a decode or encode operation.

    `settings` is the game-native settings dict (NOT the universal model).
    `metadata` always carries the original code when decoding.
    """

    success: bool
    game: str = ""
    format: str = ""
    code: Optional[str] = None          # encoded share code (encode results)
    settings: Optional[dict] = None     # game-native settings (decode results)
    error: Optional[str] = None
    warnings: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


@dataclass
class DetectionResult:
    """Result of automatic format detection + full validation."""

    valid: bool
    game: str = ""
    format: str = ""
    settings: Optional[dict] = None
    error: Optional[str] = None
    warnings: list = field(default_factory=list)
    code: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class ConversionReport:
    """Report produced when converting a crosshair between games."""

    source_game: str = ""
    source_format: str = ""
    target_game: str = ""
    target_format: str = ""
    converted: list = field(default_factory=list)        # properties carried over
    unsupported: list = field(default_factory=list)      # not representable in target
    defaulted: list = field(default_factory=list)        # target default applied
    unrepresentable: list = field(default_factory=list)  # could not be mapped at all
    warnings: list = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "Converted %s (%s) -> %s (%s)" % (
                self.source_game, self.source_format,
                self.target_game, self.target_format),
            "  converted: %d" % len(self.converted),
            "  unsupported: %d" % len(self.unsupported),
            "  defaulted: %d" % len(self.defaulted),
            "  unrepresentable: %d" % len(self.unrepresentable),
        ]
        return "\n".join(lines)


class GameCodec:
    """Interface every game codec implements."""

    game_id: str = ""
    display_name: str = ""
    #: formats this codec can encode; default_format is used for new codes
    encodable_formats: tuple = ()
    default_format: str = ""

    def matches_prefix(self, code: str) -> bool:
        raise NotImplementedError

    def decode(self, code: str) -> CodecResult:
        raise NotImplementedError

    def encode(self, settings: dict, format: str = None) -> CodecResult:
        raise NotImplementedError
