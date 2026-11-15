"""Deadlock reticle share code encoder.

Lossless path: pass the decoded settings (which carry `raw_hex`) and the exact
original bytes are re-encoded. Semantic path: modify wire fields by number.
"""

from __future__ import annotations

from crosshair.codecs.base import CodecResult
from crosshair.codecs.deadlock.schema import InvalidDeadlockCode, join_code
from crosshair.codecs.deadlock.protobuf_wire import Field, parse_fields, serialize_fields, WireError


def encode_deadlock_crosshair(settings: dict) -> CodecResult:
    settings = settings or {}
    try:
        raw_hex = settings.get("raw_hex")
        if raw_hex is not None:
            raw = bytes.fromhex(raw_hex)
        elif "wire_fields" in settings and settings["wire_fields"] is not None:
            fields = []
            for entry in settings["wire_fields"]:
                wt = entry["wire_type"]
                if wt == 0:
                    fields.append(Field(entry["field"], wt, int(entry["varint"])))
                else:
                    raw = bytes.fromhex(entry.get("bytes_hex", ""))
                    nested = entry.get("nested")
                    if nested is not None and wt == 2:
                        sub = []
                        for n in nested:
                            if n["wire_type"] == 0:
                                sub.append(Field(n["field"], 0, int(n["varint"])))
                            else:
                                sub.append(Field(n["field"], n["wire_type"],
                                                 bytes.fromhex(n.get("bytes_hex", ""))))
                        raw = serialize_fields(sub)
                    fields.append(Field(entry["field"], wt, raw))
            raw = serialize_fields(fields)
        else:
            return CodecResult(success=False, game="deadlock",
                               error="Nothing to encode: settings must contain 'raw_hex' "
                                     "or 'wire_fields'")
        code = join_code(raw)
        return CodecResult(success=True, game="deadlock", format="deadlock-reticle",
                           code=code, settings=settings,
                           metadata={"container": "DL."})
    except (InvalidDeadlockCode, WireError, ValueError) as e:
        return CodecResult(success=False, game="deadlock", error="Encoding failed: %s" % e)
