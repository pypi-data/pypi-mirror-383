from dataclasses import dataclass
from typing import TypeAlias

from flake8_digit_separator.fds_numbers.enums import (
    NumberDelimiter,
    NumberPrefix,
    NumeralSystem,
)

CleanedToken: TypeAlias = str
NumberTokenLikeStr: TypeAlias = str


@dataclass(frozen=True)
class FDSNumber:
    """Base number object.

    Without inheritance and overriding, only suitable for `int`.
    """

    token: NumberTokenLikeStr
    numeral_system: NumeralSystem
    is_supported: bool


@dataclass(frozen=True)
class NumberWithPrefix(FDSNumber):
    """Number object for octal, hex and binary."""

    prefix: NumberPrefix


@dataclass(frozen=True)
class NumberWithDelimiter(FDSNumber):
    """Number object for float."""

    delimiter: NumberDelimiter
