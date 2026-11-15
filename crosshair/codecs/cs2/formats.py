"""CS2 share code containers and primitives.

Ported from the verified reference implementation `csgo-sharecode@7.0.1`
(https://github.com/akiver/csgo-sharecode), which documents the real
game-generated formats:

- legacy container: `CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx` (18 bytes, base-57
  dictionary, dash separated), versions: legacy-v1, legacy-v3, legacy-v4
  (legacy-v2 was never released; the CS2 client rejects it).
- cs2 container: `CS` + 44 dictionary chars (32 bytes, no dashes), version
  cs2-v1.

Both containers store a big number written in base 57 with the dictionary
characters, least significant character first. Byte 0 is a checksum:
sum(bytes[1:]) % 256. Byte 1 is the version byte. Because each container
numbers its own versions from 1, the format is identified by the container,
never by the version number alone.
"""

from __future__ import annotations

import re

DICTIONARY = "ABCDEFGHJKLMNOPQRSTUVWXYZabcdefhijkmnopqrstuvwxyz23456789"
DICTIONARY_LENGTH = len(DICTIONARY)  # 57
assert DICTIONARY_LENGTH == 57

SHARECODE_BYTE_LENGTH = 18
SHARECODE_CHAR_COUNT = 25
CS2_BYTE_LENGTH = 32
CS2_CHAR_COUNT = 44

_DICT_CHARS = re.escape(DICTIONARY)
LEGACY_CONTAINER_RE = re.compile(r"^CSGO(-?[%s]{5}){5}$" % _DICT_CHARS)
CS2_CONTAINER_RE = re.compile(r"^CS[%s]{%d}$" % (_DICT_CHARS, CS2_CHAR_COUNT))


class InvalidShareCode(Exception):
    """The string is not a well-formed share code container."""


class InvalidCrosshairShareCode(Exception):
    """Well-formed container but not a valid crosshair (checksum/version)."""


def chars_to_bytes(chars: str, byte_length: int) -> bytes:
    """Decode dictionary chars (LSB first) into `byte_length` bytes."""
    big = 0
    for ch in reversed(chars):
        idx = DICTIONARY.find(ch)
        if idx < 0:
            raise InvalidShareCode("Invalid character in share code: %r" % ch)
        big = big * DICTIONARY_LENGTH + idx
    return big.to_bytes(byte_length, "big")


def bytes_to_chars(data: bytes, char_count: int) -> str:
    """Encode bytes as `char_count` dictionary chars (LSB first)."""
    big = int.from_bytes(data, "big")
    chars = []
    for _ in range(char_count):
        big, rem = divmod(big, DICTIONARY_LENGTH)
        chars.append(DICTIONARY[rem])
    return "".join(chars)


def share_code_to_bytes(share_code: str) -> bytes:
    """Decode the legacy `CSGO-xxxxx-...` container to 18 bytes."""
    if not LEGACY_CONTAINER_RE.match(share_code):
        raise InvalidShareCode("Invalid share code")
    chars = share_code.replace("CSGO", "").replace("-", "")
    return chars_to_bytes(chars, SHARECODE_BYTE_LENGTH)


def bytes_to_share_code(data: bytes) -> str:
    """Encode 18 bytes as the legacy `CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx`."""
    chars = bytes_to_chars(data, SHARECODE_CHAR_COUNT)
    return "CSGO-%s-%s-%s-%s-%s" % (
        chars[0:5], chars[5:10], chars[10:15], chars[15:20], chars[20:25])


def cs2_code_to_bytes(code: str) -> bytes:
    """Decode the native `CS...` container (44 chars) to 32 bytes."""
    if not CS2_CONTAINER_RE.match(code):
        raise InvalidShareCode("Invalid CS2 share code")
    return chars_to_bytes(code[2:], CS2_BYTE_LENGTH)


def bytes_to_cs2_code(data: bytes) -> str:
    """Encode 32 bytes as the native `CS...` code (44 chars)."""
    return "CS" + bytes_to_chars(data, CS2_CHAR_COUNT)


def assert_crosshair_checksum(data: bytes) -> None:
    """Byte 0 must equal sum(bytes[1:]) % 256."""
    if not data or data[0] != sum(data[1:]) % 256:
        raise InvalidCrosshairShareCode("Invalid crosshair share code checksum")


def apply_crosshair_checksum(data: bytearray) -> None:
    data[0] = sum(data[1:]) % 256


def uint8_to_int8(value: int) -> int:
    # Python ints don't wrap at 32 bits like JS, so do it explicitly
    value &= 0xFF
    return value - 0x100 if value >= 0x80 else value


def clamp(value, min_val, max_val):
    return min(max(value, min_val), max_val)
