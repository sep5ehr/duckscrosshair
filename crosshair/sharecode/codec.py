"""CS2 share code codec - main encode/decode interface."""

from typing import Optional, Tuple
from dataclasses import dataclass

from crosshair.sharecode.alphabet import encode_bytes, decode_string
from crosshair.sharecode.checksum import add_checksum, validate_and_strip_checksum
from crosshair.sharecode.layouts import (
    CS2CrosshairData, CS2_FIELDS_V1, CS2_PREFIX,
    pack_fields, unpack_fields, get_fields_for_version
)
from crosshair.sharecode.exceptions import (
    ShareCodeError, InvalidFormatError, InvalidLengthError,
    InvalidChecksumError, UnsupportedVersionError, DecodeError, EncodeError
)
from crosshair.models import CrosshairSettings


@dataclass
class DecodeResult:
    """Result of decoding a share code."""
    success: bool
    crosshair_data: Optional[CS2CrosshairData] = None
    internal_model: Optional[dict] = None
    version: Optional[int] = None
    format_name: str = ""
    error: Optional[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class EncodeResult:
    """Result of encoding a share code."""
    success: bool
    share_code: Optional[str] = None
    version: int = 1
    error: Optional[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class CS2ShareCodec:
    """CS2 Crosshair Share Code Encoder/Decoder."""

    SUPPORTED_VERSIONS = [1]
    CURRENT_VERSION = 1

    def __init__(self):
        pass

    def decode(self, share_code: str) -> DecodeResult:
        """
        Decode a CS2 share code to internal crosshair model.

        Args:
            share_code: The share code string (e.g., "CSGO-ABCDEF...")

        Returns:
            DecodeResult with parsed data or error
        """
        warnings = []

        try:
            # Step 1: Normalize and validate prefix
            code = share_code.strip().upper()

            if not code.startswith(CS2_PREFIX):
                # Try without prefix (legacy support)
                if "-" not in code and len(code) > 20:
                    code = CS2_PREFIX + code
                else:
                    return DecodeResult(
                        success=False,
                        error="Invalid format: share code must start with 'CSGO-'",
                        format_name="Unknown"
                    )

            # Extract encoded part
            encoded_part = code[len(CS2_PREFIX):]
            if not encoded_part:
                return DecodeResult(
                    success=False,
                    error="Empty share code data",
                    format_name="CS2"
                )

            # Step 2: Decode from base32 alphabet
            try:
                decoded_bytes = decode_string(encoded_part)
            except Exception as e:
                return DecodeResult(
                    success=False,
                    error=f"Invalid share code characters: {e}",
                    format_name="CS2"
                )

            # Step 3: Validate and strip checksum
            try:
                payload = validate_and_strip_checksum(decoded_bytes)
            except InvalidChecksumError as e:
                return DecodeResult(
                    success=False,
                    error=str(e),
                    format_name="CS2"
                )

            # Step 4: Read version (first 4 bits)
            if len(payload) < 1:
                return DecodeResult(
                    success=False,
                    error="Share code too short",
                    format_name="CS2"
                )

            version = (payload[0] >> 4) & 0xF

            if version not in self.SUPPORTED_VERSIONS:
                return DecodeResult(
                    success=False,
                    error=f"Unsupported share code version: {version}. Supported: {self.SUPPORTED_VERSIONS}",
                    format_name=f"CS2 v{version}"
                )

            # Step 5: Parse fields for this version
            fields = get_fields_for_version(version)
            try:
                crosshair_data = unpack_fields(payload, fields)
            except Exception as e:
                return DecodeResult(
                    success=False,
                    error=f"Failed to parse share code fields: {e}",
                    format_name=f"CS2 v{version}"
                )

            # Step 6: Convert to internal model
            internal_model = crosshair_data.to_internal_model()

            # Check for unrepresentable fields
            if crosshair_data.style not in (0, 1, 2, 3, 4, 5):
                warnings.append(f"Unknown style value: {crosshair_data.style}")

            format_name = f"CS2 v{version}"
            return DecodeResult(
                success=True,
                crosshair_data=crosshair_data,
                internal_model=internal_model,
                version=version,
                format_name=format_name,
                warnings=warnings
            )

        except Exception as e:
            return DecodeResult(
                success=False,
                error=f"Unexpected decode error: {e}",
                format_name="Unknown"
            )

    def encode(self, model: dict, version: int = None) -> EncodeResult:
        """
        Encode internal crosshair model to CS2 share code.

        Args:
            model: Internal crosshair model dictionary
            version: Target version (default: current)

        Returns:
            EncodeResult with share code or error
        """
        warnings = []
        version = version or self.CURRENT_VERSION

        if version not in self.SUPPORTED_VERSIONS:
            return EncodeResult(
                success=False,
                error=f"Unsupported version for encoding: {version}",
                version=version
            )

        try:
            # Convert internal model to CS2 data structure
            crosshair_data = CS2CrosshairData.from_internal_model(model)

            # Pack fields
            fields = get_fields_for_version(version)
            payload = pack_fields(crosshair_data, fields)

            # Add checksum
            payload_with_checksum = add_checksum(payload)

            # Encode to base32 alphabet
            encoded = encode_bytes(payload_with_checksum)

            # Add prefix
            share_code = CS2_PREFIX + encoded

            # Validate by decoding back
            decode_result = self.decode(share_code)
            if not decode_result.success:
                warnings.append("Generated code failed validation round-trip")

            return EncodeResult(
                success=True,
                share_code=share_code,
                version=version,
                warnings=warnings
            )

        except Exception as e:
            return EncodeResult(
                success=False,
                error=f"Encoding failed: {e}",
                version=version,
                warnings=warnings
            )

    def validate_code(self, share_code: str) -> Tuple[bool, str, list[str]]:
        """
        Validate a share code without fully decoding.

        Returns:
            (is_valid, format_name, warnings)
        """
        result = self.decode(share_code)
        return result.success, result.format_name, result.warnings

    def convert_legacy(self, share_code: str) -> DecodeResult:
        """
        Attempt to decode legacy CS:GO share codes and convert to current format.
        Currently only supports current CS2 format.
        """
        # Try current format first
        result = self.decode(share_code)
        if result.success:
            return result

        # Could add legacy format decoders here
        return DecodeResult(
            success=False,
            error="Legacy format conversion not yet implemented. Only current CS2 format supported.",
            format_name="Legacy"
        )


# Convenience functions
_default_codec = CS2ShareCodec()


def decode_share_code(share_code: str) -> DecodeResult:
    """Decode a share code using the default codec."""
    return _default_codec.decode(share_code)


def encode_share_code(model: dict, version: int = None) -> EncodeResult:
    """Encode a share code using the default codec."""
    return _default_codec.encode(model, version)


def validate_share_code(share_code: str) -> Tuple[bool, str, list[str]]:
    """Validate a share code using the default codec."""
    return _default_codec.validate_code(share_code)