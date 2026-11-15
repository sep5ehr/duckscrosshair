"""VALORANT crosshair profile code encoder.

Produces native profile codes accepted by the game's Import Profile Code.
Two modes:
- `encode_valorant_crosshair(profile_dict)` serializes the semantic profile
  to a canonical code.
- `encode_from_tokens(...)` (via decoder metadata) reproduces the exact
  original code losslessly.
"""

from __future__ import annotations

from crosshair.codecs.base import CodecResult
from crosshair.codecs.valorant.parser import ParsedCode, SectionMarker, Token, serialize_code
from crosshair.codecs.valorant.schema import (
    ValorantProfile, GunCrosshairSection, SniperSection, CUSTOM_COLOR_INDEX,
)

_LINE_KEYS = {
    "show": "b", "opacity": "a", "length": "l", "vertical_length": "v",
    "length_linked": "g", "thickness": "t", "offset": "o",
    "movement_error": "m", "movement_error_multiplier": "s",
    "firing_error": "f", "firing_error_multiplier": "e",
}


def _fmt_num(value) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _gun_section_tokens(section: GunCrosshairSection, defaults: GunCrosshairSection) -> list:
    tokens: list = []

    def add(key, value):
        tokens.append(Token(key, _fmt_num(value), None))

    # color
    if section.color_preset == CUSTOM_COLOR_INDEX and section.custom_color:
        add("c", CUSTOM_COLOR_INDEX)
        hexc = section.custom_color
        add("u", hexc if len(hexc) in (6, 8) else hexc + "FF")
    elif section.color_preset != defaults.color_preset:
        add("c", section.color_preset)

    # outline
    if section.outline.enabled != defaults.outline.enabled:
        add("h", int(section.outline.enabled))
    else:
        if section.outline.thickness != defaults.outline.thickness:
            add("t", section.outline.thickness)
        if section.outline.opacity != defaults.outline.opacity:
            add("o", section.outline.opacity)

    # center dot
    if section.center_dot.enabled:
        add("d", 1)
        if section.center_dot.thickness != defaults.center_dot.thickness:
            add("z", section.center_dot.thickness)
        if section.center_dot.opacity != defaults.center_dot.opacity:
            add("a", section.center_dot.opacity)

    if section.override_firing_error_offset:
        add("m", 1)
    if section.fade_with_firing_error is not None and not section.fade_with_firing_error:
        add("f", 0)
    if section.follow_spectating is not None and not section.follow_spectating:
        add("s", 0)

    # lines
    for prefix, lines, dlines in (("0", section.inner_lines, defaults.inner_lines),
                                  ("1", section.outer_lines, defaults.outer_lines)):
        if lines.show != dlines.show:
            add(prefix + "b", int(lines.show))
        if lines.thickness != dlines.thickness:
            add(prefix + "t", lines.thickness)
        if lines.length != dlines.length:
            add(prefix + "l", lines.length)
        if lines.length_linked:
            add(prefix + "v", lines.vertical_length)
            add(prefix + "g", 1)
        elif lines.vertical_length != lines.length:
            add(prefix + "v", lines.vertical_length)
        if lines.offset != dlines.offset:
            add(prefix + "o", lines.offset)
        if lines.opacity != dlines.opacity:
            add(prefix + "a", lines.opacity)
        if lines.firing_error != dlines.firing_error:
            add(prefix + "f", int(lines.firing_error))
        if lines.firing_error_multiplier != dlines.firing_error_multiplier:
            add(prefix + "e", lines.firing_error_multiplier)
        if lines.movement_error != dlines.movement_error:
            add(prefix + "m", int(lines.movement_error))
        if lines.movement_error_multiplier != dlines.movement_error_multiplier:
            add(prefix + "s", lines.movement_error_multiplier)
    return tokens


def _sniper_tokens(sniper: SniperSection, defaults: SniperSection) -> list:
    tokens: list = []
    if not sniper.show:
        tokens.append(Token("d", "0", None))
        return tokens
    if sniper.opacity != defaults.opacity:
        tokens.append(Token("o", _fmt_num(sniper.opacity), None))
    if sniper.thickness != defaults.thickness:
        tokens.append(Token("s", _fmt_num(sniper.thickness), None))
    if sniper.color_preset == CUSTOM_COLOR_INDEX and sniper.custom_color:
        tokens.append(Token("c", str(CUSTOM_COLOR_INDEX), None))
        hexc = sniper.custom_color
        tokens.append(Token("t", hexc if len(hexc) in (6, 8) else hexc + "FF", None))
    elif sniper.color_preset != defaults.color_preset:
        tokens.append(Token("c", _fmt_num(sniper.color_preset), None))
    return tokens


def _profile_to_parsed(profile: ValorantProfile) -> ParsedCode:
    defaults = ValorantProfile()
    elements: list = []

    header: list = []
    if profile.override_all_with_primary:
        header.append(Token("c", "1", None))
    if not profile.ads_copy_primary:
        header.append(Token("p", "0", None))
    if profile.advanced_options:
        header.append(Token("s", "1", None))

    def section_differs(sec: GunCrosshairSection) -> bool:
        d = defaults.primary
        return (sec.color_preset != d.color_preset or sec.custom_color != d.custom_color
                or sec.outline != d.outline or sec.center_dot != d.center_dot
                or sec.inner_lines != d.inner_lines or sec.outer_lines != d.outer_lines
                or sec.override_firing_error_offset
                or sec.fade_with_firing_error is not None
                or sec.follow_spectating is not None)

    if section_differs(profile.primary):
        elements.append(SectionMarker("P"))
        for t in _gun_section_tokens(profile.primary, defaults.primary):
            elements.append(Token(t.key, t.value, "P"))
    if profile.advanced_options and not profile.ads_copy_primary and section_differs(profile.ads):
        elements.append(SectionMarker("A"))
        for t in _gun_section_tokens(profile.ads, defaults.ads):
            elements.append(Token(t.key, t.value, "A"))
    if profile.advanced_options and profile.sniper != defaults.sniper:
        elements.append(SectionMarker("S"))
        for t in _sniper_tokens(profile.sniper, defaults.sniper):
            elements.append(Token(t.key, t.value, "S"))
    if profile.name:
        elements.append(Token("NAME", '"%s"' % profile.name, None))

    return ParsedCode(prefix=profile.version or "0",
                      elements=tuple(header + elements), source="")


def encode_valorant_crosshair(settings: dict) -> CodecResult:
    """Encode to a native VALORANT profile code.

    Accepts either a semantic profile dict ({"profile": {...}} as produced by
    the decoder, or a bare profile dict) or a decoded token stream
    ({"tokens": [...], "section_markers": [...]}), which is re-serialized
    losslessly.
    """
    settings = settings or {}
    try:
        parsed = settings.get("parsed")
        if parsed is not None and hasattr(parsed, "elements"):
            # exact lossless re-serialization of a decoded code
            code = serialize_code(parsed)
            return CodecResult(success=True, game="valorant", format="valorant-native",
                               code=code, settings=settings)
        if "tokens" in settings:
            # lossless re-serialization from the token stream: rebuild section
            # markers by tracking section changes (tokens carry their section)
            elements = []
            current = None
            for t in settings["tokens"]:
                sec = t.get("section")
                if sec != current:
                    if sec is not None:
                        elements.append(SectionMarker(sec))
                    current = sec
                elements.append(Token(t["key"], t["value"], sec))
            code = serialize_code(ParsedCode(
                prefix=settings.get("version", "0"), elements=tuple(elements),
                trailing_separator=bool(settings.get("trailing_separator"))))
            return CodecResult(success=True, game="valorant", format="valorant-native",
                               code=code, settings=settings)
        profile = ValorantProfile.from_dict(settings.get("profile", settings))
        code = serialize_code(_profile_to_parsed(profile))
        return CodecResult(success=True, game="valorant", format="valorant-native",
                           code=code, settings={"profile": profile.to_dict()})
    except Exception as e:
        return CodecResult(success=False, game="valorant",
                           error="Encoding failed: %s" % e)
