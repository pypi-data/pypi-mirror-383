from typing import final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.fds_numbers import IntNumber


@final
class IntClassifier(BaseClassifier):
    """Classifier for int numbers."""

    def __init__(
        self,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self) -> IntNumber:
        """Returns a int number if it matches.

        :return: Int number
        :rtype: IntNumber
        """
        return IntNumber(self.token)

    @property
    def token(self) -> TokenLikeStr:
        """Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
