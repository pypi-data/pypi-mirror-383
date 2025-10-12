from typing import final

from flake8_digit_separator.fds_numbers.fds_numbers import IntNumber
from flake8_digit_separator.rules.rules import IntFDSRules
from flake8_digit_separator.validators.base import BaseValidator


@final
class IntValidator(BaseValidator):
    """Validator for int numbers."""

    def __init__(self, number: IntNumber) -> None:
        self._number = number
        self._pattern = r'^[+-]?(?!0_)\d{1,3}(?:_\d{3})*$'

    def validate(self) -> bool:
        """Validates number token.

        1. Check that it can be converted to int.
        2. Check for pattern compliance.

        :return: `True` if all steps are completed. Otherwise `False`.
        :rtype: bool
        """
        return self.validate_token_as_int() and self.validate_token_by_pattern()

    @property
    def pattern(self) -> str:
        """The regular expression that will be validated.

        :return: Regular expression.
        :rtype: str
        """
        return self._pattern

    @property
    def number(self) -> IntNumber:
        """FDS int number object."""
        return self._number

    @property
    def error_message(self) -> str:
        """The rule that the validator checked.

        :return: FDS rule.
        :rtype: str
        """
        return IntFDSRules.FDS100.create_message()
