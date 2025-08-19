"""common validator used and shared.

mostly akan menggunakan regex untuk validasi input
dan anotated , agar bisa digunakan as field di pydantic atau di field validator
"""

import re
from typing import Annotated

from pydantic import AfterValidator


def is_alphanumeric_underscore(value: str) -> str:
    """Validasi input hanya boleh alphanumeric dan underscore, min length 3."""
    pattern = r"^[a-zA-Z0-9_]+$"
    if len(value) < 3:
        raise ValueError("Input minimal 3 karakter.")
    if re.match(pattern, value):
        return value
    raise ValueError("Input harus alphanumeric dan underscore saja.")


AlphanumericUnderscoreStr = Annotated[str, AfterValidator(is_alphanumeric_underscore)]


def is_alphanumric_withspace(value: str) -> str:
    """Validasi input hanya boleh alphanumeric dan spasi, min length 3."""
    pattern = r"^[a-zA-Z0-9 ]+$"
    if len(value) < 3:
        raise ValueError("Input minimal 3 karakter.")
    if re.match(pattern, value):
        return value
    raise ValueError("Input harus alphanumeric dan spasi saja.")


AlphanumericWithSpaceStr = Annotated[str, AfterValidator(is_alphanumric_withspace)]


def validate_password(value: str) -> str:
    """Validasi password, minimal 6 karakter, alphanumeric dan special char (kecuali spasi).

    Password harus:
    - Minimal 6 karakter
    - Mengandung alphanumeric dan special character
    - Tidak boleh ada spasi
    """
    if len(value) < 6:
        raise ValueError("Password minimal 6 karakter.")
    if " " in value:
        raise ValueError("Password tidak boleh mengandung spasi.")
    # regex: at least one alphanumeric, at least one special char, no spaces
    pattern = r"^(?=.*[a-zA-Z0-9])(?=.*[^a-zA-Z0-9\s]).{6,}$"
    if not re.match(pattern, value):
        raise ValueError(
            "Password harus mengandung alphanumeric dan special character (kecuali spasi)."
        )
    return value


PasswordStrongStr = Annotated[str, AfterValidator(validate_password)]
