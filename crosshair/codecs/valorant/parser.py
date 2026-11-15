"""Lossless tokenizer/serializer for native VALORANT crosshair profile codes.

Format: semicolon-separated tokens. Token 0 is the format version ("0").
Section markers `P` (Primary), `A` (ADS), `S` (Sniper) switch the active
section; everything else is a key;value pair. `NAME;"..."` carries the
profile name. Parsing is lossless: unknown keys, duplicates, ordering and a
single trailing semicolon are all preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

MAX_CODE_LENGTH = 8192
MAX_ATOMS = 512

SECTION_MARKERS = frozenset({"P", "A", "S"})


@dataclass(frozen=True)
class SectionMarker:
    name: str


@dataclass(frozen=True)
class Token:
    key: str
    value: str
    section: Optional[str]  # None = general/header section


@dataclass
class ParsedCode:
    prefix: str
    elements: tuple = ()          # tuple of SectionMarker | Token
    trailing_separator: bool = False
    source: str = ""

    @property
    def tokens(self) -> tuple:
        return tuple(e for e in self.elements if isinstance(e, Token))

    def get(self, key: str, section: Optional[str] = None) -> Optional[str]:
        """Last value for key in section (None section = header)."""
        result = None
        for t in self.tokens:
            if t.key == key and t.section == section:
                result = t.value
        return result

    def get_all(self, key: str, section: Optional[str] = None) -> list:
        return [t.value for t in self.tokens if t.key == key and t.section == section]


@dataclass
class ParseResult:
    ok: bool
    code: Optional[ParsedCode] = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def parse_code(text: str) -> ParseResult:
    """Parse a VALORANT profile code losslessly."""
    errors: list = []
    warnings: list = []
    if not text or not text.strip():
        return ParseResult(False, errors=["empty_code: crosshair code is empty"])
    if len(text) > MAX_CODE_LENGTH:
        return ParseResult(False, errors=["code_too_long: exceeds %d chars" % MAX_CODE_LENGTH])

    atoms = text.split(";")
    trailing = atoms[-1] == ""
    if trailing:
        atoms.pop()
    if atoms and atoms[-1] == "":
        errors.append("repeated_separator: only one trailing semicolon is permitted")
        atoms.pop()
    if len(atoms) > MAX_ATOMS:
        return ParseResult(False, errors=["too_many_tokens: exceeds %d atoms" % MAX_ATOMS])
    if not atoms or not atoms[0]:
        return ParseResult(False, errors=["empty_prefix: code must start with a version token"])

    prefix = atoms[0]
    if prefix != "0":
        errors.append("unsupported_version: %r (only version '0' is supported)" % prefix)
        return ParseResult(False, errors=errors)

    elements: list = []
    section: Optional[str] = None
    seen: set = set()
    i = 1
    while i < len(atoms):
        key = atoms[i]
        if key in SECTION_MARKERS:
            section = key
            elements.append(SectionMarker(key))
            i += 1
            continue
        if not key:
            errors.append("empty_key at token %d" % i)
            i += 2
            continue
        if i + 1 >= len(atoms):
            errors.append("missing_value: parameter %r has no value" % key)
            break
        if atoms[i + 1] in SECTION_MARKERS:
            errors.append("missing_value: parameter %r has no value before section marker" % key)
            i += 1
            continue
        value = atoms[i + 1]
        if not value:
            errors.append("empty_value: parameter %r has an empty value" % key)
        identity = (section, key)
        if identity in seen:
            warnings.append("duplicate_parameter: %r duplicated in section %r" % (key, section))
        seen.add(identity)
        elements.append(Token(key, value, section))
        i += 2

    if errors:
        return ParseResult(False, errors=errors, warnings=warnings)
    return ParseResult(
        True,
        code=ParsedCode(prefix=prefix, elements=tuple(elements),
                        trailing_separator=trailing, source=text),
        warnings=warnings,
    )


def serialize_code(code: ParsedCode) -> str:
    """Serialize a parsed code back to its exact string form."""
    atoms = [code.prefix]
    for e in code.elements:
        if isinstance(e, SectionMarker):
            atoms.append(e.name)
        else:
            atoms.extend((e.key, e.value))
    out = ";".join(atoms)
    if code.trailing_separator:
        out += ";"
    return out
