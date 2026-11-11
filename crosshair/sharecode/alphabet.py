"""CS2 share code alphabet encoding/decoding."""

from crosshair.sharecode.exceptions import InvalidAlphabetError

# CS2 uses a custom base32 alphabet (32 characters)
# Based on standard RFC 4648 base32: "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
CS2_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
# Ensure we have exactly 32 characters
assert len(CS2_ALPHABET) == 32, f"CS2 alphabet must have 32 characters, got {len(CS2_ALPHABET)}"

ALPHABET_TO_VALUE = {c: i for i, c in enumerate(CS2_ALPHABET)}
VALUE_TO_ALPHABET = {i: c for i, c in enumerate(CS2_ALPHABET)}


def encode_bytes(data: bytes) -> str:
    """Encode bytes to CS2 share code alphabet (base32)."""
    if not data:
        return ""

    # Convert bytes to bits
    bits = []
    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    # Pad to multiple of 5 bits
    padding = (5 - len(bits) % 5) % 5
    bits.extend([0] * padding)

    # Convert 5-bit chunks to alphabet
    result = []
    for i in range(0, len(bits), 5):
        chunk = 0
        for j in range(5):
            chunk = (chunk << 1) | bits[i + j]
        result.append(VALUE_TO_ALPHABET[chunk])

    return "".join(result)


def decode_string(encoded: str) -> bytes:
    """Decode CS2 share code alphabet to bytes."""
    if not encoded:
        return b""

    # Validate characters
    for c in encoded:
        if c not in ALPHABET_TO_VALUE:
            raise InvalidAlphabetError(f"Invalid character in share code: {c}")

    # Convert alphabet to 5-bit values
    bits = []
    for c in encoded:
        val = ALPHABET_TO_VALUE[c]
        for i in range(4, -1, -1):
            bits.append((val >> i) & 1)

    # Convert bits to bytes (8 bits per byte)
    # Remove padding bits (the last incomplete byte)
    num_bytes = len(bits) // 8
    result = bytearray()
    for i in range(num_bytes):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits[i * 8 + j]
        result.append(byte)

    return bytes(result)