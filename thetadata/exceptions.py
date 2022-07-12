"""Module that contains custom exceptions."""
import enum
from typing import Any


class EnumParseError(Exception):
    """Raise when a value cannot be parsed into an associated enum member."""

    def __init__(self, value: Any, enm: Any):
        """Create a new `EnumParseError`

        :param value: The value that cannot be parsed.
        :param enm: The enum.
        """
        assert issubclass(
            enm, enum.Enum
        ), "Cannot create an EnumParseError with a non-enum."
        msg = f"Value {value} cannot be parsed into a {enm.__name__}!"
        super().__init__(msg)


class ResponseError(Exception):
    """Raised if there was an error indicated in the body of a response."""
