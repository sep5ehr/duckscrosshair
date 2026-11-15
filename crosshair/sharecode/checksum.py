"""Share code checksum calculation (CRC8)."""

from crosshair.sharecode.exceptions import InvalidChecksumError


# CRC8 polynomial (0x1D = x^8 + x^4 + x^3 + x^2 + 1)
# This is the standard CRC-8-ATM (HEC) polynomial used in CS2 share codes
CRC8_POLY = 0x1D
CRC8_INIT = 0x00


def crc8(data: bytes) -> int:
    """Calculate CRC8 checksum."""
    crc = CRC8_INIT
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) & 0xFF) ^ CRC8_POLY
            else:
                crc = (crc << 1) & 0xFF
    return crc


def verify_checksum(data: bytes, expected_checksum: int) -> bool:
    """Verify CRC8 checksum."""
    return crc8(data) == expected_checksum


def add_checksum(data: bytes) -> bytes:
    """Append CRC8 checksum to data."""
    return data + bytes([crc8(data)])


def validate_and_strip_checksum(data: bytes) -> bytes:
    """Validate checksum and return data without checksum."""
    if len(data) < 1:
        raise InvalidChecksumError("Data too short for checksum")
    payload = data[:-1]
    checksum = data[-1]
    if not verify_checksum(payload, checksum):
        raise InvalidChecksumError(f"Invalid checksum: expected {crc8(payload):02X}, got {checksum:02X}")
    return payload