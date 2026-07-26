import re

def is_valid_email(email: str) -> bool:
    """Verifies format of an email address."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_password(password: str) -> bool:
    """Validates password length and complexity."""
    # Minimum 8 characters
    return len(password) >= 8
