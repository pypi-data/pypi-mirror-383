from typing import final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.enums import NumberPrefix
from flake8_digit_separator.fds_numbers.fds_numbers import BinaryNumber


@final
class BinaryClassifier(BaseClassifier):
    """Classifier for binary numbers."""

    def __init__(
        self,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self) -> BinaryNumber | None:
        """Returns a binary number if it matches.

        :return: Binary number
        :rtype: BinaryNumber | None
        """
        if self.token_lower.startswith(NumberPrefix.BINARY.get_value_without_separator()):
            return BinaryNumber(self.token_lower)

        return None

    @property
    def token(self) -> TokenLikeStr:
        """Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
