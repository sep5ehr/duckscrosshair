"""Universal (normalized) crosshair model.

This is an application-level schema, not a native game schema. Properties
that cannot be represented universally live in `game_extensions`; the
original imported code is kept in `metadata` so nothing is ever lost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DotModel:
    enabled: bool = False
    size: float = 1.0
    opacity: float = 1.0


@dataclass
class LineModel:
    enabled: bool = True
    thickness: float = 1.0
    length: float = 5.0
    offset: float = 2.0
    opacity: float = 1.0
    movement_error: bool = False
    firing_error: bool = False


@dataclass
class OutlineModel:
    enabled: bool = True
    color: str = "#000000"
    thickness: float = 1.0
    opacity: float = 1.0


@dataclass
class UniversalCrosshair:
    game: str = "universal"
    color: str = "#00FF00"
    alpha: float = 1.0
    scale: float = 1.0  # global size multiplier (app-level; games scale via own settings)
    center_dot: DotModel = field(default_factory=DotModel)
    inner_lines: LineModel = field(default_factory=LineModel)
    outer_lines: LineModel = field(default_factory=lambda: LineModel(enabled=False, offset=10.0))
    outline: OutlineModel = field(default_factory=OutlineModel)
    # game-specific properties that have no universal equivalent
    game_extensions: dict = field(default_factory=dict)
    # original imported code / source info, never lost
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UniversalCrosshair":
        import dataclasses
        kwargs = {}
        for fname, sub in (("center_dot", DotModel), ("inner_lines", LineModel),
                           ("outer_lines", LineModel), ("outline", OutlineModel)):
            raw = data.get(fname)
            if isinstance(raw, dict):
                valid = {f for f in sub.__dataclass_fields__}
                kwargs[fname] = sub(**{k: v for k, v in raw.items() if k in valid})
        valid = {f for f in cls.__dataclass_fields__}
        for k, v in data.items():
            if k in valid and k not in kwargs:
                kwargs[k] = v
        return cls(**kwargs)
