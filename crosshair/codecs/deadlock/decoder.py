"""Deadlock reticle share code decoder (`DL.` prefix + base64url + protobuf wire)."""

from __future__ import annotations

from crosshair.codecs.base import CodecResult
from crosshair.codecs.deadlock.schema import (
    InvalidDeadlockCode, split_code, join_code, FIELD_NAMES,
)
from crosshair.codecs.deadlock.protobuf_wire import parse_fields, serialize_fields, WireError


def _fields_to_dict(fields: list) -> list:
    out = []
    for f in fields:
        entry = {"field": f.number, "wire_type": f.wire_type,
                 "name": FIELD_NAMES.get(f.number)}
        if f.wire_type == 0:
            entry["varint"] = f.value
        else:
            entry["bytes_hex"] = f.value.hex()
            # best effort: try nested protobuf parse
            try:
                entry["nested"] = _fields_to_dict(parse_fields(f.value))
            except WireError:
                entry["nested"] = None
        out.append(entry)
    return out


def decode_deadlock_crosshair(code: str) -> CodecResult:
    code = (code or "").strip()
    try:
        raw = split_code(code)
    except InvalidDeadlockCode as e:
        return CodecResult(success=False, game="deadlock", error=str(e))

    warnings = [
        "Deadlock DL. payload parsed at the protobuf wire level; per-field game "
        "semantics are best-effort/unverified (no verified reference available).",
    ]
    try:
        fields = parse_fields(raw)
        wire_ok = True
    except WireError as e:
        fields = []
        wire_ok = False
        warnings.append("Payload is not cleanly parseable as protobuf wire format "
                        "(%s); raw bytes preserved for lossless round-trip." % e)

    settings = {
        "format": "deadlock-reticle",
        "raw_hex": raw.hex(),
        "wire_fields": _fields_to_dict(fields) if wire_ok else None,
        "wire_parse_ok": wire_ok,
    }
    return CodecResult(
        success=True, game="deadlock", format="deadlock-reticle",
        settings=settings, code=code, warnings=warnings,
        metadata={"original_code": code, "raw": raw},
    )
