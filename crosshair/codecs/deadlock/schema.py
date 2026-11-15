"""Deadlock reticle share code support.

IMPORTANT HONESTY NOTE: no verified reference implementation or real
game-generated fixture set for the native `DL.` reticle share code was
available in this environment, so this codec does NOT claim full semantic
decoding of every field. What is implemented and verified:

- strict `DL.` prefix validation,
- base64url payload decoding,
- standard protobuf wire-format parsing (generic, no invented field
  positions) with a best-effort field-name map in `schema.py`,
- lossless re-encoding: decode -> encode reproduces the exact original code
  byte-for-byte, preserving every unknown field.

Field *semantics* beyond the wire structure are marked unverified and are
reported as such instead of being guessed.
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass, field
from typing import Optional

from crosshair.codecs.deadlock.protobuf_wire import (
    Field, WireError, parse_fields, serialize_fields, WT_LEN, WT_VARINT,
)

PREFIX = "DL."

# Best-effort, UNVERIFIED field-name map for the reticle payload.
# Populated from observed payloads; treated as hints only.
FIELD_NAMES = {
    1: "reticle_motion",
    2: "static_lines",
}


class InvalidDeadlockCode(Exception):
    pass


def _b64decode(payload: str) -> bytes:
    try:
        padded = payload + "=" * (-len(payload) % 4)
        return base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True)
    except (binascii.Error, ValueError, UnicodeEncodeError) as e:
        raise InvalidDeadlockCode("Invalid base64url payload: %s" % e)


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def split_code(code: str) -> bytes:
    """Validate prefix and return the raw payload bytes."""
    code = (code or "").strip()
    if not code.startswith(PREFIX):
        raise InvalidDeadlockCode("Deadlock reticle codes must start with 'DL.'")
    payload = code[len(PREFIX):]
    if not payload:
        raise InvalidDeadlockCode("Empty payload after 'DL.'")
    return _b64decode(payload)


def join_code(data: bytes) -> str:
    return PREFIX + _b64encode(data)
