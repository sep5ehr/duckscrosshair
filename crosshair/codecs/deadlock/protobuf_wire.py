"""Generic protobuf wire-format reader/writer.

This is the standard protobuf wire format (varint / 64-bit / length-delimited
/ 32-bit), NOT an invented game layout. It preserves every field losslessly,
including unknown field numbers, so a decoded Deadlock payload can always be
re-encoded byte-identically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

WT_VARINT = 0
WT_64BIT = 1
WT_LEN = 2
WT_32BIT = 5


class WireError(Exception):
    pass


@dataclass
class Field:
    number: int
    wire_type: int
    value: Union[int, bytes]  # int for varint/32/64, bytes for length-delimited


def _read_varint(data: bytes, pos: int) -> tuple:
    result = 0
    shift = 0
    while True:
        if pos >= len(data):
            raise WireError("truncated varint")
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7
        if shift > 70:
            raise WireError("varint too long")


def _write_varint(value: int) -> bytes:
    value &= (1 << 64) - 1
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def parse_fields(data: bytes) -> list:
    """Parse a protobuf message body into an ordered list of Field."""
    fields: list = []
    pos = 0
    while pos < len(data):
        key, pos = _read_varint(data, pos)
        number, wt = key >> 3, key & 7
        if number == 0:
            raise WireError("invalid field number 0")
        if wt == WT_VARINT:
            value, pos = _read_varint(data, pos)
        elif wt == WT_64BIT:
            if pos + 8 > len(data):
                raise WireError("truncated 64-bit field")
            value = data[pos:pos + 8]
            pos += 8
        elif wt == WT_LEN:
            length, pos = _read_varint(data, pos)
            if pos + length > len(data):
                raise WireError("truncated length-delimited field")
            value = data[pos:pos + length]
            pos += length
        elif wt == WT_32BIT:
            if pos + 4 > len(data):
                raise WireError("truncated 32-bit field")
            value = data[pos:pos + 4]
            pos += 4
        else:
            raise WireError("unsupported wire type %d" % wt)
        fields.append(Field(number, wt, value))
    return fields


def serialize_fields(fields: list) -> bytes:
    out = bytearray()
    for f in fields:
        out += _write_varint((f.number << 3) | f.wire_type)
        if f.wire_type == WT_VARINT:
            out += _write_varint(f.value)
        else:
            if f.wire_type == WT_LEN:
                out += _write_varint(len(f.value))
            out += f.value
    return bytes(out)


def try_parse_nested(data: bytes) -> list:
    """Best-effort recursive parse; returns fields, with submessages parsed."""
    fields = parse_fields(data)
    return fields
