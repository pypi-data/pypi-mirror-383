from typing import final

from flake8_digit_separator.classifiers.base import BaseClassifier
from flake8_digit_separator.classifiers.types import TokenLikeStr
from flake8_digit_separator.fds_numbers.enums import NumberPrefix
from flake8_digit_separator.fds_numbers.fds_numbers import OctalNumber


@final
class OctalClassifier(BaseClassifier):
    """Classifier for octal numbers."""

    def __init__(
        self,
        token: TokenLikeStr,
    ) -> None:
        self._token = token

    def classify(self) -> OctalNumber | None:
        """Returns a octal number if it matches.

        :return: Octal number
        :rtype: OctalNumber | None
        """
        if self.token_lower.startswith(NumberPrefix.OCTAL.get_value_without_separator()):
            return OctalNumber(self.token_lower)

        return None

    @property
    def token(self) -> TokenLikeStr:
        """Token string from `tokenize.TokenInfo` object.

        :return: Token like string.
        :rtype: TokenLikeStr
        """
        return self._token
