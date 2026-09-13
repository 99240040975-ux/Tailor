import re


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)


def validate_email(email):
    """Validate an email address."""
    if not email or not isinstance(email, str):
        return False, "Email address is required."

    email = email.strip().lower()

    if not EMAIL_PATTERN.fullmatch(email):
        return False, "Invalid email address format."

    if len(email) > 254:
        return False, "Email address is too long."

    return True, None


def validate_phone(phone):
    """
    Validate an optional phone number.

    Spaces, hyphens, brackets and a leading plus sign are accepted.
    """
    if phone is None or not str(phone).strip():
        return True, None

    phone = str(phone).strip()

    # Remove common formatting characters.
    cleaned = re.sub(
        r"[\s\-().+]",
        "",
        phone,
    )

    if not cleaned.isdigit():
        return False, "Phone number must contain only digits."

    if len(cleaned) < 7 or len(cleaned) > 15:
        return False, (
            "Phone number must be between "
            "7 and 15 digits."
        )

    return True, None


def validate_password(password):
    """Validate a user password."""
    if not password:
        return False, "Password is required."

    if not isinstance(password, str):
        return False, "Password must be text."

    if len(password) < 6:
        return False, (
            "Password must be at least "
            "6 characters long."
        )

    if len(password) > 128:
        return False, (
            "Password must be 128 characters "
            "or fewer."
        )

    return True, None


def validate_measurement_value(
    name,
    value,
    unit="inches",
):
    """
    Validate a numeric measurement value.

    This checks that the value is numeric, non-negative,
    and within a broad practical range.
    """

    if value is None or str(value).strip() == "":
        return True, None

    try:
        number = float(value)
    except (ValueError, TypeError):
        return False, (
            f"{str(name).capitalize()} "
            "must be a valid number."
        )

    if number < 0:
        return False, (
            f"{str(name).capitalize()} "
            "cannot be negative."
        )

    normalized_unit = str(unit or "inches").lower()

    if normalized_unit in {"cm", "centimeter", "centimeters"}:
        maximum = 300
        unit_label = "cm"
    elif normalized_unit in {"in", "inch", "inches"}:
        maximum = 120
        unit_label = "inches"
    else:
        maximum = 300
        unit_label = str(unit)

    if number > maximum:
        return False, (
            f"{str(name).capitalize()} seems "
            f"unrealistically large "
            f"({number:g} {unit_label})."
        )

    return True, None


def validate_required_text(
    value,
    field_name,
    min_length=1,
    max_length=None,
):
    """Validate a required text field."""
    if value is None:
        return False, f"{field_name} is required."

    text = str(value).strip()

    if len(text) < min_length:
        return False, f"{field_name} is required."

    if max_length is not None and len(text) > max_length:
        return False, (
            f"{field_name} must be "
            f"{max_length} characters or fewer."
        )

    return True, None