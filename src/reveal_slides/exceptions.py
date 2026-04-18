from __future__ import annotations


class InvalidInputError(Exception):
    """Raised when the input JSON file cannot be read or parsed."""


class ValidationFailedError(Exception):
    """Raised when presentation data fails Pydantic validation."""

    def __init__(self, errors: list[dict]) -> None:
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s)")
