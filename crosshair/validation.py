"""Crosshair settings validation and clamping."""

from dataclasses import dataclass
from typing import Optional
from crosshair.models import CrosshairSettings

# Validation ranges (moved here to avoid circular imports)
VALIDATION_RANGES = {
    "gap": (0, 50),
    "length": (0, 100),
    "thickness": (1, 20),
    "size": (0, 50),
    "opacity": (0.0, 1.0),
    "scale": (0.1, 10.0),
    "outline_thickness": (0, 10),
    "dynamic_spread_limit": (0.0, 1.0),
    "split_distance": (0, 100),
    "inner_split_alpha": (0, 255),
    "outer_split_alpha": (0, 255),
    "split_size_ratio": (0.0, 1.0),
    "reference_resolution": (640, 7680),
    "scope_dot_scale": (0.0, 10.0),
    "style": (0, 5),
}


@dataclass
class ValidationResult:
    """Result of validating a crosshair setting."""
    valid: bool
    value: any
    error_message: Optional[str] = None
    clamped: bool = False


def clamp_value(value: float, min_val: float, max_val: float) -> tuple[float, bool]:
    """Clamp a value to range, return (clamped_value, was_clamped)."""
    if value < min_val:
        return min_val, True
    if value > max_val:
        return max_val, True
    return value, False


def validate_int(value: any, min_val: int, max_val: int, field_name: str) -> ValidationResult:
    """Validate and clamp an integer value."""
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            value=min_val,
            error_message=f"{field_name}: must be an integer"
        )

    clamped_val, was_clamped = clamp_value(int_val, min_val, max_val)
    return ValidationResult(
        valid=True,
        value=clamped_val,
        clamped=was_clamped,
        error_message=f"{field_name}: clamped to [{min_val}, {max_val}]" if was_clamped else None
    )


def validate_float(value: any, min_val: float, max_val: float, field_name: str) -> ValidationResult:
    """Validate and clamp a float value."""
    try:
        float_val = float(value)
    except (ValueError, TypeError):
        return ValidationResult(
            valid=False,
            value=min_val,
            error_message=f"{field_name}: must be a number"
        )

    clamped_val, was_clamped = clamp_value(float_val, min_val, max_val)
    return ValidationResult(
        valid=True,
        value=clamped_val,
        clamped=was_clamped,
        error_message=f"{field_name}: clamped to [{min_val}, {max_val}]" if was_clamped else None
    )


def validate_color(value: any, field_name: str) -> ValidationResult:
    """Validate a hex color string."""
    if not isinstance(value, str):
        return ValidationResult(
            valid=False,
            value="#000000",
            error_message=f"{field_name}: must be a string"
        )

    color = value.strip()
    if not color.startswith("#"):
        color = "#" + color

    if len(color) not in (4, 7, 9):  # #RGB, #RRGGBB, #RRGGBBAA
        return ValidationResult(
            valid=False,
            value="#000000",
            error_message=f"{field_name}: invalid hex color format (use #RGB, #RRGGBB, or #RRGGBBAA)"
        )

    try:
        int(color[1:], 16)
    except ValueError:
        return ValidationResult(
            valid=False,
            value="#000000",
            error_message=f"{field_name}: invalid hex characters"
        )

    return ValidationResult(valid=True, value=color.upper())


def validate_crosshair_settings(settings: CrosshairSettings) -> tuple[CrosshairSettings, list[str]]:
    """Validate all crosshair settings, return corrected settings and warnings."""
    corrected = settings.copy()
    warnings = []

    # Validate core settings
    validations = [
        ("gap", validate_int, VALIDATION_RANGES["gap"]),
        ("length", validate_int, VALIDATION_RANGES["length"]),
        ("thickness", validate_int, VALIDATION_RANGES["thickness"]),
        ("size", validate_int, VALIDATION_RANGES["size"]),
        ("opacity", validate_float, VALIDATION_RANGES["opacity"]),
        ("scale", validate_float, VALIDATION_RANGES["scale"]),
        ("outline_thickness", validate_int, VALIDATION_RANGES["outline_thickness"]),
        ("dynamic_spread_limit", validate_float, VALIDATION_RANGES["dynamic_spread_limit"]),
        ("split_distance", validate_int, VALIDATION_RANGES["split_distance"]),
        ("inner_split_alpha", validate_int, VALIDATION_RANGES["inner_split_alpha"]),
        ("outer_split_alpha", validate_int, VALIDATION_RANGES["outer_split_alpha"]),
        ("split_size_ratio", validate_float, VALIDATION_RANGES["split_size_ratio"]),
        ("reference_resolution", validate_int, VALIDATION_RANGES["reference_resolution"]),
        ("scope_dot_scale", validate_float, VALIDATION_RANGES["scope_dot_scale"]),
    ]

    for field_name, validator, (min_val, max_val) in validations:
        current_value = getattr(corrected, field_name)
        result = validator(current_value, min_val, max_val, field_name)
        if not result.valid:
            warnings.append(result.error_message or f"{field_name}: invalid value")
        elif result.clamped:
            warnings.append(result.error_message or f"{field_name}: value clamped")
        setattr(corrected, field_name, result.value)

    # Validate colors
    for field_name in ["color", "outline_color"]:
        current_value = getattr(corrected, field_name)
        result = validate_color(current_value, field_name)
        if not result.valid:
            warnings.append(result.error_message or f"{field_name}: invalid color")
        setattr(corrected, field_name, result.value)

    # Validate style (0-5 for CS2)
    style_result = validate_int(corrected.style, 0, 5, "style")
    if not style_result.valid:
        warnings.append(style_result.error_message or "style: invalid value")
    elif style_result.clamped:
        warnings.append(style_result.error_message or "style: value clamped")
    corrected.style = style_result.value

    # Validate boolean fields (ensure they're actually bools)
    for field_name in ["outline_enabled", "center_dot", "t_style",
                       "scope_dot_use_crosshair_color"]:
        current_value = getattr(corrected, field_name)
        if not isinstance(current_value, bool):
            setattr(corrected, field_name, bool(current_value))
            warnings.append(f"{field_name}: converted to boolean")

    return corrected, warnings