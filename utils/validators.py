import re


def validate_email(email):
    if not email or not isinstance(email, str):
        return False, "Email address is required."
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email.strip()):
        return False, "Invalid email address format."
    return True, None


def validate_phone(phone):
    if not phone:
        return True, None  # Optional field
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Phone number must be between 7 and 15 digits."
    return True, None


def validate_password(password):
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, None


def validate_measurement_value(name, val, unit='inches'):
    """Validates numeric range for human body measurements."""
    if val is None or val == '':
        return True, None
    try:
        num = float(val)
    except (ValueError, TypeError):
        return False, f"{name.capitalize()} must be a valid number."

    if num < 0:
        return False, f"{name.capitalize()} cannot be negative."

    # Max reasonable bounds based on unit
    max_val = 300 if unit == 'cm' else 120
    if num > max_val:
        return False, f"{name.capitalize()} seems unrealistically large ({num} {unit})."

    return True, None
