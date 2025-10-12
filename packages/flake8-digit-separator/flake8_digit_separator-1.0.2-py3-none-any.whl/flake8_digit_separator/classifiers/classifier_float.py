from typing import final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.enums import NumberDelimiter
from flake8_digit_separator.fds_numbers.fds_numbers import FloatNumber


@final
class FloatClassifier(BaseClassifier):
    """Classifier for float numbers."""

    def __init__(
        self,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self) -> FloatNumber | None:
        """Returns a float number if it matches.

        :return: Float number
        :rtype: FloatNumber | None
        """
        if NumberDelimiter.FLOAT.value in self.token:
            return FloatNumber(self.token)

        return None

    @property
    def token(self) -> TokenLikeStr:
        """Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
