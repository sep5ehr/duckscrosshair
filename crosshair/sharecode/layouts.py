"""CS2 share code binary layouts for different versions."""

from dataclasses import dataclass
from typing import Optional
from crosshair.sharecode.exceptions import UnsupportedVersionError, InvalidLengthError


# CS2 share code prefix
CS2_PREFIX = "CSGO-"


@dataclass
class CS2CrosshairData:
    """Parsed CS2 crosshair share code data (current format)."""
    version: int = 1

    # Crosshair style (0-5)
    style: int = 4

    # Classic static crosshair fields
    gap: int = -2  # CS2 internal: -2 = gap 2
    length: float = 4.0
    thickness: float = 1.0
    size: float = 4.0
    draw_outline: int = 1
    outline_thickness: float = 1.0
    dot: int = 0

    # Color (RGB packed)
    color_r: int = 0
    color_g: int = 255
    color_b: int = 0

    # Advanced / dynamic fields
    dynamic_spread_limit: float = 0.0
    split_distance: int = 7
    inner_split_alpha: int = 255
    outer_split_alpha: int = 255
    split_size_ratio: float = 0.5

    # Reference resolution
    reference_resolution: int = 1920

    # Scope settings
    scope_dot_scale: float = 1.0
    scope_dot_use_crosshair_color: int = 0

    # T-style
    t_style: int = 0

    # Sniper width
    sniper_width: int = 1

    # Reserved/padding bits
    reserved: int = 0

    def to_internal_model(self) -> dict:
        """Convert to internal crosshair model (gap is positive in internal)."""
        return {
            "style": self.style,
            "gap": max(0, -self.gap),  # CS2 stores gap as negative
            "length": self.length,
            "thickness": self.thickness,
            "size": self.size,
            "outline_enabled": bool(self.draw_outline),
            "outline_thickness": self.outline_thickness,
            "center_dot": bool(self.dot),
            "color": f"#{self.color_r:02X}{self.color_g:02X}{self.color_b:02X}",
            "dynamic_spread_limit": self.dynamic_spread_limit,
            "split_distance": self.split_distance,
            "inner_split_alpha": self.inner_split_alpha,
            "outer_split_alpha": self.outer_split_alpha,
            "split_size_ratio": self.split_size_ratio,
            "reference_resolution": self.reference_resolution,
            "scope_dot_scale": self.scope_dot_scale,
            "scope_dot_use_crosshair_color": bool(self.scope_dot_use_crosshair_color),
            "t_style": bool(self.t_style),
        }

    @classmethod
    def from_internal_model(cls, model: dict) -> "CS2CrosshairData":
        """Create from internal crosshair model."""
        return cls(
            style=model.get("style", 4),
            gap=-model.get("gap", 2),  # Internal stores positive, CS2 stores negative
            length=model.get("length", 4.0),
            thickness=model.get("thickness", 1.0),
            size=model.get("size", 4.0),
            draw_outline=1 if model.get("outline_enabled", True) else 0,
            outline_thickness=model.get("outline_thickness", 1.0),
            dot=1 if model.get("center_dot", False) else 0,
            color_r=int(model.get("color", "#00FF00")[1:3], 16),
            color_g=int(model.get("color", "#00FF00")[3:5], 16),
            color_b=int(model.get("color", "#00FF00")[5:7], 16),
            dynamic_spread_limit=model.get("dynamic_spread_limit", 0.0),
            split_distance=model.get("split_distance", 7),
            inner_split_alpha=model.get("inner_split_alpha", 255),
            outer_split_alpha=model.get("outer_split_alpha", 255),
            split_size_ratio=model.get("split_size_ratio", 0.5),
            reference_resolution=model.get("reference_resolution", 1920),
            scope_dot_scale=model.get("scope_dot_scale", 1.0),
            scope_dot_use_crosshair_color=1 if model.get("scope_dot_use_crosshair_color", False) else 0,
            t_style=1 if model.get("t_style", False) else 0,
            reserved=0,
        )


# Bit field definitions for CS2 crosshair (version 1)
# Based on reverse-engineered format
CS2_FIELDS_V1 = [
    # (name, bits, signed, scale_factor, description)
    ("version", 4, False, 1, "Format version"),
    ("style", 4, False, 1, "Crosshair style (0-5)"),

    # Classic static crosshair
    ("gap", 8, True, 1, "Gap (negative in CS2)"),
    ("length", 8, False, 0.25, "Line length * 4"),
    ("thickness", 6, False, 0.25, "Line thickness * 4"),
    ("size", 6, False, 0.25, "Dot size * 4"),
    ("draw_outline", 1, False, 1, "Draw outline (0/1)"),
    ("outline_thickness", 5, False, 0.25, "Outline thickness * 4"),
    ("dot", 1, False, 1, "Center dot (0/1)"),

    # Color (RGB)
    ("color_r", 8, False, 1, "Red component"),
    ("color_g", 8, False, 1, "Green component"),
    ("color_b", 8, False, 1, "Blue component"),

    # Advanced
    ("dynamic_spread_limit", 8, False, 1/255.0, "Dynamic spread limit"),
    ("split_distance", 8, False, 1, "Split distance"),
    ("inner_split_alpha", 8, False, 1, "Inner split alpha"),
    ("outer_split_alpha", 8, False, 1, "Outer split alpha"),
    ("split_size_ratio", 8, False, 1/255.0, "Split size ratio"),

    # Reference resolution
    ("reference_resolution", 13, False, 1, "Reference resolution"),

    # Scope
    ("scope_dot_scale", 8, False, 1/10.0, "Scope dot scale * 10"),
    ("scope_dot_use_crosshair_color", 1, False, 1, "Scope dot uses crosshair color"),

    # T-style
    ("t_style", 1, False, 1, "T-style (remove top line)"),

    # Sniper width
    ("sniper_width", 4, False, 1, "Sniper crosshair width"),

    # Padding/reserved
    ("reserved", 7, False, 1, "Reserved bits"),
]

# Total bits: 4+4+8+8+6+6+1+5+1+8+8+8+8+8+8+8+13+8+1+1+4+7 = 136 bits = 17 bytes + 1 checksum = 18 bytes
# Base32 encodes 5 bits per char, so 136 bits = 27.2 chars -> 28 chars + padding


def calculate_bit_size(fields: list) -> int:
    """Calculate total bit size of fields."""
    return sum(f[1] for f in fields)


def pack_fields(data: CS2CrosshairData, fields: list) -> bytes:
    """Pack CS2CrosshairData into bytes according to field definitions."""
    bits = []
    for name, bit_count, signed, scale, _ in fields:
        value = getattr(data, name)

        # Apply inverse scaling
        if scale != 1:
            value = int(round(value / scale))

        # Handle signed values
        if signed:
            # Two's complement for negative values
            if value < 0:
                value = (1 << bit_count) + value
            value = value & ((1 << bit_count) - 1)
        else:
            value = value & ((1 << bit_count) - 1)

        # Add bits (MSB first)
        for i in range(bit_count - 1, -1, -1):
            bits.append((value >> i) & 1)

    # Pad to byte boundary
    padding = (8 - len(bits) % 8) % 8
    bits.extend([0] * padding)

    # Convert to bytes
    result = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i + j]
        result.append(byte)

    return bytes(result)


def unpack_fields(data: bytes, fields: list) -> CS2CrosshairData:
    """Unpack bytes into CS2CrosshairData according to field definitions."""
    # Convert bytes to bits
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    result = CS2CrosshairData()
    bit_index = 0

    for name, bit_count, signed, scale, _ in fields:
        if bit_index + bit_count > len(bits):
            raise InvalidLengthError(f"Not enough bits for field {name}")

        # Read bits
        value = 0
        for i in range(bit_count):
            value = (value << 1) | bits[bit_index + i]
        bit_index += bit_count

        # Handle signed
        if signed:
            # Check sign bit
            if value & (1 << (bit_count - 1)):
                value = value - (1 << bit_count)

        # Apply scaling
        if scale != 1:
            value = value * scale

        setattr(result, name, value)

    return result


def get_fields_for_version(version: int) -> list:
    """Get field definitions for a specific version."""
    if version == 1:
        return CS2_FIELDS_V1
    raise UnsupportedVersionError(f"Unsupported CS2 share code version: {version}")
