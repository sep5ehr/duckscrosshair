"""Share code exceptions."""


class ShareCodeError(Exception):
    """Base exception for share code errors."""
    pass


class InvalidFormatError(ShareCodeError):
    """Raised when the share code format is invalid."""
    pass


class InvalidLengthError(ShareCodeError):
    """Raised when the share code has invalid length."""
    pass


class InvalidChecksumError(ShareCodeError):
    """Raised when the share code checksum fails."""
    pass


class UnsupportedVersionError(ShareCodeError):
    """Raised when the share code version is not supported."""
    pass


class InvalidAlphabetError(ShareCodeError):
    """Raised when the share code contains invalid characters."""
    pass


class DecodeError(ShareCodeError):
    """Raised when decoding fails."""
    pass


class EncodeError(ShareCodeError):
    """Raised when encoding fails."""
    pass