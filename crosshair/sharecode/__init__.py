"""CS2 Share Code package."""

from crosshair.sharecode.codec import (
    CS2ShareCodec,
    DecodeResult,
    EncodeResult,
    decode_share_code,
    encode_share_code,
    validate_share_code,
)
from crosshair.sharecode.exceptions import (
    ShareCodeError,
    InvalidFormatError,
    InvalidLengthError,
    InvalidChecksumError,
    UnsupportedVersionError,
    InvalidAlphabetError,
    DecodeError,
    EncodeError,
)
from crosshair.sharecode.alphabet import encode_bytes, decode_string
from crosshair.sharecode.checksum import crc8, verify_checksum, add_checksum, validate_and_strip_checksum
from crosshair.sharecode.layouts import (
    CS2CrosshairData,
    CS2_FIELDS_V1,
    pack_fields,
    unpack_fields,
    get_fields_for_version,
)

__all__ = [
    # Codec
    "CS2ShareCodec",
    "DecodeResult",
    "EncodeResult",
    "decode_share_code",
    "encode_share_code",
    "validate_share_code",
    # Exceptions
    "ShareCodeError",
    "InvalidFormatError",
    "InvalidLengthError",
    "InvalidChecksumError",
    "UnsupportedVersionError",
    "InvalidAlphabetError",
    "DecodeError",
    "EncodeError",
    # Alphabet
    "encode_bytes",
    "decode_string",
    # Checksum
    "crc8",
    "verify_checksum",
    "add_checksum",
    "validate_and_strip_checksum",
    # Layouts
    "CS2CrosshairData",
    "CS2_FIELDS_V1",
    "pack_fields",
    "unpack_fields",
    "get_fields_for_version",
]