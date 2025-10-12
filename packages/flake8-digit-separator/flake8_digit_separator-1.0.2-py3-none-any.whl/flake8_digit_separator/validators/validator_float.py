from typing import final

from flake8_digit_separator.fds_numbers.fds_numbers import FloatNumber
from flake8_digit_separator.rules.rules import FloatFDSRules
from flake8_digit_separator.validators.base import BaseValidator


@final
class FloatValidator(BaseValidator):
    """Validator for float numbers."""

    def __init__(self, number: FloatNumber) -> None:
        self._number = number
        self._pattern = r'^[+-]?(?:(?!0_)\d{1,3}(?:_\d{3})*\.\d{1,3}(?:_\d{3})*|\.\d{1,3}(?:_\d{3})*)$'

    def validate(self) -> bool:
        """Validates number token.

        1. Check that it can be converted to float.
        2. Check for pattern compliance.

        :return: `True` if all steps are completed. Otherwise `False`.
        :rtype: bool
        """
        return self.validate_token_as_float() and self.validate_token_by_pattern()

    @property
    def pattern(self) -> str:
        """The regular expression that will be validated.

        :return: Regular expression.
        :rtype: str
        """
        return self._pattern

    @property
    def number(self) -> FloatNumber:
        """FDS decimal number object."""
        return self._number

    @property
    def error_message(self) -> str:
        """The rule that the validator checked.

        :return: FDS rule.
        :rtype: str
        """
        return FloatFDSRules.FDS200.create_message()
